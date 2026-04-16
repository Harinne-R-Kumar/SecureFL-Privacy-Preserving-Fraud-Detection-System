#!/usr/bin/env python3
"""
CLIENT MANAGEMENT SYSTEM FOR SELECTIVE FEDERATED LEARNING
Controls which clients participate in global model updates
"""

import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ClientManager:
    """Manages client participation, trust scores, and selection"""
    
    def __init__(self):
        # Client registry
        self.registered_clients: Dict[str, dict] = {}
        
        # Client selection control
        self.selected_clients: List[str] = []
        self.blocked_clients: List[str] = []
        
        # Client performance tracking
        self.client_scores: Dict[str, dict] = {}
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Configuration
        self.max_clients = 50
        self.trust_threshold = 0.5
        self.accuracy_threshold = 0.6
        
    def register_client(self, client_id: str, client_info: dict) -> bool:
        """Register new client with initial trust score"""
        with self.lock:
            if len(self.registered_clients) >= self.max_clients:
                return False
                
            self.registered_clients[client_id] = {
                **client_info,
                'registered_at': datetime.now().isoformat(),
                'status': 'active',
                'updates_contributed': 0,
                'last_update': None
            }
            
            # Initialize client score
            self.client_scores[client_id] = {
                'trust_score': 0.5,  # Start with neutral trust
                'data_size': client_info.get('data_size', 1000),
                'accuracy': 0.0,
                'reliability': 0.5,
                'contribution_score': 0.0
            }
            
            # Auto-select if no explicit selection
            if not self.selected_clients:
                self.selected_clients.append(client_id)
            
            return True
    
    def update_client_score(self, client_id: str, accuracy: float, data_size: int) -> None:
        """Update client performance metrics"""
        with self.lock:
            if client_id not in self.client_scores:
                return
                
            # Update accuracy with exponential moving average
            current_score = self.client_scores[client_id]['accuracy']
            new_accuracy = 0.7 * current_score + 0.3 * accuracy
            
            # Update trust score based on consistency
            accuracy_improvement = accuracy - current_score
            trust_delta = 0.1 * accuracy_improvement
            new_trust = max(0.0, min(1.0, 
                self.client_scores[client_id]['trust_score'] + trust_delta))
            
            # Calculate contribution score
            contribution_score = (data_size / 10000) * accuracy * new_trust
            
            self.client_scores[client_id].update({
                'accuracy': new_accuracy,
                'trust_score': new_trust,
                'data_size': data_size,
                'reliability': min(1.0, new_trust + 0.2),
                'contribution_score': contribution_score,
                'last_scored': datetime.now().isoformat()
            })
    
    def select_clients_for_training(self, num_clients: int = 5, 
                               selection_method: str = 'weighted') -> List[str]:
        """Select clients for next training round"""
        with self.lock:
            # Filter eligible clients
            eligible = [
                client_id for client_id in self.registered_clients
                if (client_id not in self.blocked_clients and
                    self.client_scores[client_id]['trust_score'] >= self.trust_threshold and
                    self.client_scores[client_id]['accuracy'] >= self.accuracy_threshold)
            ]
            
            if not eligible:
                return []
            
            if selection_method == 'weighted':
                # Weighted selection based on contribution score
                scores = [self.client_scores[cid]['contribution_score'] for cid in eligible]
                total_score = sum(scores)
                
                if total_score == 0:
                    return eligible[:num_clients]
                
                probabilities = [score/total_score for score in scores]
                selected = np.random.choice(eligible, 
                                       size=min(num_clients, len(eligible)), 
                                       replace=False, 
                                       p=probabilities)
                return selected.tolist()
            
            elif selection_method == 'top':
                # Select top performers
                sorted_clients = sorted(eligible, 
                    key=lambda cid: self.client_scores[cid]['contribution_score'], 
                    reverse=True)
                return sorted_clients[:num_clients]
            
            else:  # random
                return np.random.choice(eligible, 
                                     size=min(num_clients, len(eligible)), 
                                     replace=False).tolist()
    
    def block_client(self, client_id: str, reason: str = "") -> bool:
        """Block client from participation"""
        with self.lock:
            if client_id in self.registered_clients:
                self.blocked_clients.append(client_id)
                self.registered_clients[client_id]['status'] = 'blocked'
                self.registered_clients[client_id]['block_reason'] = reason
                self.registered_clients[client_id]['blocked_at'] = datetime.now().isoformat()
                return True
            return False
    
    def unblock_client(self, client_id: str) -> bool:
        """Unblock client"""
        with self.lock:
            if client_id in self.blocked_clients:
                self.blocked_clients.remove(client_id)
                if client_id in self.registered_clients:
                    self.registered_clients[client_id]['status'] = 'active'
                    self.registered_clients[client_id].pop('block_reason', None)
                    self.registered_clients[client_id].pop('blocked_at', None)
                return True
            return False
    
    def get_client_status(self, client_id: str) -> Optional[dict]:
        """Get detailed client status"""
        with self.lock:
            if client_id in self.registered_clients:
                client_info = self.registered_clients[client_id].copy()
                if client_id in self.client_scores:
                    client_info.update(self.client_scores[client_id])
                return client_info
            return None
    
    def get_all_clients(self) -> Dict[str, dict]:
        """Get all clients with their scores"""
        with self.lock:
            result = {}
            for client_id, info in self.registered_clients.items():
                client_data = info.copy()
                if client_id in self.client_scores:
                    client_data.update(self.client_scores[client_id])
                result[client_id] = client_data
            return result
    
    def set_selected_clients(self, client_ids: List[str]) -> None:
        """Manually set which clients should participate"""
        with self.lock:
            # Validate all clients exist and are not blocked
            valid_clients = [
                cid for cid in client_ids 
                if (cid in self.registered_clients and 
                    cid not in self.blocked_clients)
            ]
            self.selected_clients = valid_clients
    
    def get_selected_clients(self) -> List[str]:
        """Get currently selected clients"""
        with self.lock:
            return self.selected_clients.copy()
    
    def is_client_selected(self, client_id: str) -> bool:
        """Check if client is selected for training"""
        with self.lock:
            return client_id in self.selected_clients
    
    def update_client_activity(self, client_id: str) -> None:
        """Update client last activity timestamp"""
        with self.lock:
            if client_id in self.registered_clients:
                self.registered_clients[client_id]['last_update'] = datetime.now().isoformat()
    
    def get_statistics(self) -> dict:
        """Get client management statistics"""
        with self.lock:
            active_clients = [
                cid for cid, info in self.registered_clients.items()
                if info.get('status') == 'active' and 
                cid not in self.blocked_clients
            ]
            
            return {
                'total_registered': len(self.registered_clients),
                'active_clients': len(active_clients),
                'blocked_clients': len(self.blocked_clients),
                'selected_clients': len(self.selected_clients),
                'average_trust_score': np.mean([
                    score['trust_score'] for score in self.client_scores.values()
                ]) if self.client_scores else 0.0,
                'average_accuracy': np.mean([
                    score['accuracy'] for score in self.client_scores.values()
                ]) if self.client_scores else 0.0,
                'total_data_size': sum([
                    score['data_size'] for score in self.client_scores.values()
                ])
            }
