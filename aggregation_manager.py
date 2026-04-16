#!/usr/bin/env python3
"""
SMART REAL-TIME AGGREGATION MANAGER
Handles intelligent aggregation with queue, bad update detection, and version control
"""

import threading
import time
import numpy as np
import torch
import copy
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pickle
import os

class AggregationManager:
    """Manages real-time model aggregation with safety and intelligence"""
    
    def __init__(self, model, max_queue_size=10):
        self.model = model
        self.max_queue_size = max_queue_size
        
        # Update queue and buffer
        self.update_queue: List[dict] = []
        self.pending_updates: Dict[str, dict] = {}
        
        # Version control
        self.model_versions: Dict[int, dict] = {}
        self.current_version = 0
        self.version_history: List[dict] = []
        
        # Aggregation configuration
        self.aggregation_window = 5.0  # seconds
        self.min_updates_for_aggregation = 2
        self.max_updates_for_aggregation = 10
        self.deviation_threshold = 2.0  # Standard deviations
        
        # Safety and monitoring
        self.rejected_updates: List[dict] = []
        self.aggregation_logs: List[dict] = []
        
        # Thread safety
        self.lock = threading.Lock()
        self.aggregation_in_progress = False
        
        # Initialize with current model
        self._save_model_version(0, "Initial model")
    
    def _save_model_version(self, version: int, description: str) -> None:
        """Save model version with metadata"""
        with self.lock:
            # Extract model weights
            weights = []
            for param in self.model.parameters():
                weights.extend(param.data.cpu().numpy().flatten())
            
            version_info = {
                'version': version,
                'timestamp': datetime.now().isoformat(),
                'description': description,
                'weights': weights.copy(),
                'num_parameters': len(weights),
                'updates_included': len(self.update_queue) if self.update_queue else 0
            }
            
            self.model_versions[version] = version_info
            self.current_version = version
            
            # Save to disk
            self._save_model_to_disk(version, weights)
            
            # Log version
            self.version_history.append(version_info.copy())
            print(f"📦 Model version {version} saved: {description}")
    
    def _save_model_to_disk(self, version: int, weights: List[float]) -> None:
        """Save model weights to disk"""
        try:
            model_data = {
                'version': version,
                'weights': weights,
                'timestamp': datetime.now().isoformat(),
                'architecture': 'PredictionModel(input_size=9)'
            }
            
            filename = f'global_model_v{version}.pkl'
            with open(filename, 'wb') as f:
                pickle.dump(model_data, f)
            
            # Also save as latest
            with open('global_model_latest.pkl', 'wb') as f:
                pickle.dump(model_data, f)
                
        except Exception as e:
            print(f"⚠️ Error saving model v{version}: {e}")
    
    def _calculate_weight_factor(self, client_id: str, client_scores: dict) -> float:
        """Calculate client's weight in aggregation based on multiple factors"""
        if client_id not in client_scores:
            return 1.0
        
        scores = client_scores[client_id]
        
        # Multi-factor weight calculation
        data_size_weight = np.log1p(scores['data_size']) / np.log1p(10000)  # Log scale for data size
        accuracy_weight = scores['accuracy']  # Direct accuracy factor
        trust_weight = scores['trust_score']  # Trust factor
        reliability_weight = scores['reliability']  # Reliability factor
        
        # Combined weight (can be tuned)
        combined_weight = (
            0.4 * data_size_weight +
            0.3 * accuracy_weight +
            0.2 * trust_weight +
            0.1 * reliability_weight
        )
        
        return max(0.1, combined_weight)  # Minimum weight to avoid zero
    
    def _detect_bad_update(self, update: dict, global_weights: List[float]) -> Tuple[bool, str]:
        """Detect potentially malicious or erroneous updates"""
        client_weights = update.get('weights', [])
        
        if not client_weights or not global_weights:
            return False, "No weights provided"
        
        # Convert to numpy arrays
        client_arr = np.array(client_weights)
        global_arr = np.array(global_weights)
        
        # Check dimension mismatch
        if client_arr.shape != global_arr.shape:
            return False, f"Dimension mismatch: {client_arr.shape} vs {global_arr.shape}"
        
        # Calculate deviation
        deviation = np.linalg.norm(client_arr - global_arr)
        mean_norm = np.linalg.norm(global_arr)
        
        if mean_norm == 0:
            return False, "Global model is zero"
        
        # Relative deviation
        relative_deviation = deviation / mean_norm
        
        # Check against threshold
        if relative_deviation > self.deviation_threshold:
            return True, f"High deviation: {relative_deviation:.3f} (threshold: {self.deviation_threshold})"
        
        return False, "Update looks normal"
    
    def queue_update(self, client_id: str, weights: List[float], 
                   metrics: dict, client_scores: dict) -> Dict[str, any]:
        """Queue a client update for aggregation"""
        with self.lock:
            if self.aggregation_in_progress:
                return {
                    'status': 'queued',
                    'message': 'Aggregation in progress, update queued',
                    'queue_position': len(self.update_queue) + 1
                }
            
            # Detect bad updates before queuing
            global_weights = []
            if self.current_version in self.model_versions:
                global_weights = self.model_versions[self.current_version]['weights']
            
            is_bad, reason = self._detect_bad_update(
                {'client_id': client_id, 'weights': weights, 'metrics': metrics},
                global_weights
            )
            
            if is_bad:
                rejection_info = {
                    'client_id': client_id,
                    'timestamp': datetime.now().isoformat(),
                    'reason': reason,
                    'metrics': metrics,
                    'deviation': 'high'
                }
                self.rejected_updates.append(rejection_info)
                print(f"🚫 Rejected update from {client_id}: {reason}")
                return {
                    'status': 'rejected',
                    'message': f'Update rejected: {reason}',
                    'rejection_reason': reason
                }
            
            # Add to queue
            update_info = {
                'client_id': client_id,
                'weights': weights.copy(),
                'metrics': metrics,
                'client_scores': client_scores,
                'timestamp': datetime.now().isoformat(),
                'weight_factor': self._calculate_weight_factor(client_id, client_scores)
            }
            
            self.update_queue.append(update_info)
            self.pending_updates[client_id] = update_info
            
            # Auto-aggregate if enough updates
            if len(self.update_queue) >= self.min_updates_for_aggregation:
                # Start aggregation in background thread
                threading.Thread(target=self._aggregate_updates, daemon=True).start()
            
            return {
                'status': 'queued',
                'message': f'Update queued (position {len(self.update_queue)})',
                'queue_size': len(self.update_queue)
            }
    
    def _aggregate_updates(self) -> None:
        """Perform intelligent aggregation of queued updates"""
        with self.lock:
            if self.aggregation_in_progress or len(self.update_queue) < self.min_updates_for_aggregation:
                return
            
            self.aggregation_in_progress = True
            
            try:
                # Get updates for aggregation
                updates_to_aggregate = self.update_queue[:self.max_updates_for_aggregation]
                
                # Calculate weighted aggregation
                aggregated_weights = self._weighted_federation(updates_to_aggregate)
                
                # Update global model
                self._apply_aggregated_weights(aggregated_weights)
                
                # Create new version
                new_version = self.current_version + 1
                description = f"Aggregated {len(updates_to_aggregate)} client updates"
                self._save_model_version(new_version, description)
                
                # Log aggregation
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'version': new_version,
                    'num_updates': len(updates_to_aggregate),
                    'clients': [u['client_id'] for u in updates_to_aggregate],
                    'aggregation_method': 'weighted_federation',
                    'total_weight': sum(u['weight_factor'] for u in updates_to_aggregate)
                }
                self.aggregation_logs.append(log_entry)
                
                # Remove aggregated updates from queue
                self.update_queue = self.update_queue[len(updates_to_aggregate):]
                for update in updates_to_aggregate:
                    if update['client_id'] in self.pending_updates:
                        del self.pending_updates[update['client_id']]
                
                print(f"🔄 Aggregation complete: Version {new_version} from {len(updates_to_aggregate)} updates")
                
            except Exception as e:
                print(f"❌ Aggregation failed: {e}")
            finally:
                self.aggregation_in_progress = False
    
    def _weighted_federation(self, updates: List[dict]) -> List[float]:
        """Perform weighted federated averaging"""
        if not updates:
            return []
        
        # Extract weights and factors
        weights_list = [update['weights'] for update in updates]
        weight_factors = [update['weight_factor'] for update in updates]
        
        # Normalize weights
        total_weight = sum(weight_factors)
        if total_weight == 0:
            normalized_weights = [1.0 / len(updates)] * len(updates)
        else:
            normalized_weights = [w / total_weight for w in weight_factors]
        
        # Weighted averaging
        num_params = len(weights_list[0])
        aggregated = np.zeros(num_params)
        
        for i, (client_weights, weight) in enumerate(zip(weights_list, normalized_weights)):
            aggregated += weight * np.array(client_weights)
        
        return aggregated.tolist()
    
    def _apply_aggregated_weights(self, weights: List[float]) -> None:
        """Apply aggregated weights to global model"""
        try:
            if self.model is None:
                print("⚠️ No model available to apply weights")
                return
                
            # Convert weights back to model parameters
            offset = 0
            for param in self.model.parameters():
                param_size = param.data.numel()
                param_weights = weights[offset:offset + param_size]
                param.data = torch.tensor(param_weights).reshape(param.data.shape).float()
                offset += param_size
        except Exception as e:
            print(f"❌ Error applying weights: {e}")
    
    def force_aggregation(self) -> Dict[str, any]:
        """Force immediate aggregation of queued updates"""
        with self.lock:
            if len(self.update_queue) < self.min_updates_for_aggregation:
                return {
                    'status': 'insufficient_updates',
                    'message': f'Need at least {self.min_updates_for_aggregation} updates, have {len(self.update_queue)}'
                }
            
            if self.aggregation_in_progress:
                return {
                    'status': 'aggregation_in_progress',
                    'message': 'Aggregation already in progress'
                }
            
            # Start aggregation
            threading.Thread(target=self._aggregate_updates, daemon=True).start()
            
            return {
                'status': 'aggregation_started',
                'message': 'Forced aggregation started',
                'updates_count': len(self.update_queue)
            }
    
    def rollback_to_version(self, version: int) -> Dict[str, any]:
        """Rollback global model to specific version"""
        with self.lock:
            if version not in self.model_versions:
                return {
                    'status': 'version_not_found',
                    'message': f'Version {version} not found',
                    'available_versions': list(self.model_versions.keys())
                }
            
            # Load version weights
            version_info = self.model_versions[version]
            self._apply_aggregated_weights(version_info['weights'])
            self.current_version = version
            
            # Log rollback
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'rollback',
                'from_version': self.current_version,
                'to_version': version,
                'reason': 'manual_rollback'
            }
            self.aggregation_logs.append(log_entry)
            
            print(f"⏪ Rolled back to version {version}")
            
            return {
                'status': 'rollback_complete',
                'message': f'Rolled back to version {version}',
                'version_info': {
                    'version': version,
                    'timestamp': version_info['timestamp'],
                    'description': version_info['description']
                }
            }
    
    def get_queue_status(self) -> dict:
        """Get current aggregation queue status"""
        with self.lock:
            return {
                'queue_size': len(self.update_queue),
                'pending_updates': len(self.pending_updates),
                'aggregation_in_progress': self.aggregation_in_progress,
                'current_version': self.current_version,
                'min_updates_needed': self.min_updates_for_aggregation,
                'max_updates_per_aggregation': self.max_updates_for_aggregation,
                'queued_clients': [u['client_id'] for u in self.update_queue],
                'rejected_count': len(self.rejected_updates),
                'total_versions': len(self.model_versions)
            }
    
    def get_version_history(self, limit: int = 10) -> List[dict]:
        """Get model version history"""
        with self.lock:
            return self.version_history[-limit:]
    
    def get_aggregation_logs(self, limit: int = 20) -> List[dict]:
        """Get aggregation logs"""
        with self.lock:
            return self.aggregation_logs[-limit:]
    
    def get_rejected_updates(self, limit: int = 10) -> List[dict]:
        """Get rejected updates history"""
        with self.lock:
            return self.rejected_updates[-limit:]
    
    def get_client_contributions(self, client_id: str) -> dict:
        """Get specific client's contribution history"""
        with self.lock:
            contributions = [
                log for log in self.aggregation_logs
                if client_id in log.get('clients', [])
            ]
            
            return {
                'client_id': client_id,
                'total_contributions': len(contributions),
                'contributions': contributions[-10:],  # Last 10 contributions
                'last_contribution': contributions[-1] if contributions else None
            }
