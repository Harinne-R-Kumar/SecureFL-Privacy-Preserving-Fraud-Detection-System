#!/usr/bin/env python3
"""
ENHANCED CLIENT FOR PRODUCTION FEDERATED LEARNING
Works with enhanced server features: scoring, selective participation, version control
"""

import requests
import json
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime
import time
import argparse

class EnhancedFraudDetectionModel(nn.Module):
    """Enhanced fraud detection model matching server architecture"""
    def __init__(self, input_size=9):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1)
        )
    
    def forward(self, x):
        return self.net(x)
    
    def get_weights(self):
        """Extract model weights as flat list"""
        weights = []
        for param in self.parameters():
            weights.extend(param.data.cpu().numpy().flatten())
        return weights
    
    def set_weights(self, weights):
        """Load weights into model"""
        try:
            offset = 0
            for param in self.parameters():
                param_size = param.data.numel()
                param_weights = weights[offset:offset + param_size]
                param.data = torch.tensor(param_weights).reshape(param.data.shape).float()
                offset += param_size
            return True
        except Exception as e:
            print(f"Error loading weights: {e}")
            return False

class EnhancedFederatedClient:
    """Enhanced client with scoring, version control, and smart participation"""
    
    def __init__(self, server_url, client_name, data_size=1000, 
                 api_key=None, local_data_file=None):
        self.server_url = server_url.rstrip('/')
        self.client_name = client_name
        self.data_size = data_size
        self.api_key = api_key
        self.client_id = None
        self.model = EnhancedFraudDetectionModel()
        
        # Performance tracking
        self.training_history = []
        self.current_model_version = 0
        self.last_update_time = None
        
        # Local data (mock if not provided)
        self.local_data = self._generate_mock_data() if not local_data_file else None
        
        # Configuration
        self.training_epochs = 3
        self.learning_rate = 0.001
        self.batch_size = 32
        
    def _generate_mock_data(self):
        """Generate mock fraud detection data for testing"""
        np.random.seed(42)
        
        # Generate features (9 input features)
        X = np.random.randn(1000, 9).astype(np.float32)
        
        # Generate labels with some fraud cases (5%)
        y = np.random.choice([0, 1], size=1000, p=[0.95, 0.05]).astype(np.float32)
        
        # Add some realistic patterns
        # Higher amounts more likely to be fraud
        X[:, 0] = np.abs(X[:, 0]) * 1000  # Amount
        fraud_mask = y == 1
        X[fraud_mask, 0] *= 2.5  # Fraudulent transactions have higher amounts
        
        return torch.tensor(X), torch.tensor(y)
    
    def register_enhanced(self):
        """Register with enhanced server and get scoring info"""
        print(f"🔐 Registering {self.client_name} with enhanced server...")
        
        payload = {
            'client_name': self.client_name,
            'data_size': self.data_size,
            'location': 'Enhanced Client Location',
            'api_key': self.api_key or ''
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/client-management/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data['client_id']
                
                print(f"✅ Successfully registered!")
                print(f"🆔 Client ID: {self.client_id}")
                print(f"📊 Initial Trust Score: {data['server_info']['trust_score']:.3f}")
                print(f"⚖️ Initial Weight Factor: {data['server_info']['initial_weight']:.3f}")
                print(f"📦 Global Model Version: {data['server_info']['global_model_version']}")
                
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering: {e}")
            return False
    
    def get_global_model_enhanced(self):
        """Get global model with version tracking"""
        if not self.client_id:
            print("❌ Must register first!")
            return False
        
        print(f"📥 Downloading global model v{self.current_model_version}...")
        
        try:
            response = requests.get(
                f"{self.server_url}/api/client/model",
                params={'client_id': self.client_id},
                timeout=10
            )
            
            if response.status_code == 200:
                model_data = response.json()
                self.current_model_version = model_data['model_version']
                
                print(f"✅ Received global model v{self.current_model_version}")
                print(f"📊 Model Parameters: {model_data['metadata']['model_parameters']}")
                print(f"👥 Contributors: {model_data['metadata']['contributors']}")
                
                # Load weights into local model
                return self.model.set_weights(model_data['weights'])
            else:
                print(f"❌ Failed to get model: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting model: {e}")
            return False
    
    def train_locally_enhanced(self):
        """Enhanced local training with performance tracking"""
        print(f"🏋 Training locally for {self.training_epochs} epochs...")
        
        if not self.local_data:
            X, y = self._generate_mock_data()
        else:
            X, y = self.local_data
        
        # Setup training
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        
        self.model.train()
        epoch_losses = []
        
        for epoch in range(self.training_epochs):
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(X)
            loss = criterion(outputs, y)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            epoch_loss = loss.item()
            epoch_losses.append(epoch_loss)
            
            print(f"  Epoch {epoch+1}/{self.training_epochs}: Loss = {epoch_loss:.4f}")
        
        # Calculate metrics
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X)
            predictions = torch.sigmoid(outputs)
            predicted_labels = (predictions > 0.5).float()
            
            # Calculate accuracy
            accuracy = (predicted_labels == y).float().mean().item()
            
            # Calculate precision, recall, F1
            tp = ((predicted_labels == 1) & (y == 1)).float().sum().item()
            fp = ((predicted_labels == 1) & (y == 0)).float().sum().item()
            fn = ((predicted_labels == 0) & (y == 1)).float().sum().item()
            
            precision = tp / (tp + fp + 1e-8)
            recall = tp / (tp + fn + 1e-8)
            f1_score = 2 * (precision * recall) / (precision + recall + 1e-8)
        
        metrics = {
            'accuracy': accuracy,
            'f1_score': f1_score,
            'precision': precision,
            'recall': recall,
            'final_loss': epoch_losses[-1],
            'training_samples': len(X),
            'epochs': self.training_epochs,
            'training_time': datetime.now().isoformat()
        }
        
        print(f"✅ Training completed!")
        print(f"📊 Accuracy: {accuracy:.4f}, F1: {f1_score:.4f}")
        print(f"🎯 Precision: {precision:.4f}, Recall: {recall:.4f}")
        
        # Store training history
        self.training_history.append(metrics)
        
        return metrics
    
    def submit_enhanced_update(self, metrics):
        """Submit update with enhanced scoring and tracking"""
        if not self.client_id:
            print("❌ Must register first!")
            return False
        
        print(f"📤 Submitting enhanced model update...")
        
        payload = {
            'client_id': self.client_id,
            'weights': self.model.get_weights(),
            'metrics': metrics,
            'client_version': self.current_model_version,
            'submission_time': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/client-management/update",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Update submitted successfully!")
                print(f"🔄 New Global Model Version: {data['new_global_model_version']}")
                print(f"📊 Total Updates on Server: {data['total_updates']}")
                print(f"🎯 Your Total Contributions: {data['your_contributions']}")
                
                if data['status'] == 'queued':
                    print(f"⏳ Update queued (position {data.get('queue_position', 'unknown')})")
                elif data['status'] == 'rejected':
                    print(f"🚫 Update rejected: {data.get('rejection_reason', 'Unknown reason')}")
                
                self.last_update_time = datetime.now()
                return True
            else:
                print(f"❌ Failed to submit update: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error submitting update: {e}")
            return False
    
    def get_client_status_enhanced(self):
        """Get enhanced client status with scoring"""
        if not self.client_id:
            print("❌ Must register first!")
            return None
        
        try:
            response = requests.get(
                f"{self.server_url}/api/client-management/status/{self.client_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json()
                
                print(f"📊 Enhanced Client Status for {self.client_name}")
                print(f"🆔 Client ID: {status.get('client_id', 'Unknown')}")
                print(f"📈 Accuracy: {status.get('accuracy', 0):.4f}")
                print(f"⚖️ Trust Score: {status.get('trust_score', 0):.3f}")
                print(f"🎯 Contribution Score: {status.get('contribution_score', 0):.3f}")
                print(f"📦 Data Size: {status.get('data_size', 0)}")
                print(f"🔄 Updates Contributed: {status.get('updates_contributed', 0)}")
                
                if 'total_contributions' in status:
                    contribs = status['total_contributions']
                    print(f"📈 Contribution History:")
                    for i, contrib in enumerate(contribs[-5:], 1):
                        print(f"  {i}. Version {contrib.get('version', 'N/A')} - Score: {contrib.get('score', 0):.3f}")
                
                return status
            else:
                print(f"❌ Failed to get status: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting status: {e}")
            return None
    
    def check_aggregation_status(self):
        """Check aggregation queue status"""
        try:
            response = requests.get(
                f"{self.server_url}/api/aggregation/queue-status",
                timeout=10
            )
            
            if response.status_code == 200:
                status = response.json()
                
                print(f"🔄 Aggregation Queue Status:")
                print(f"📊 Queue Size: {status['queue_size']}")
                print(f"⏳ Pending Updates: {status['pending_updates']}")
                print(f"🔄 Aggregation in Progress: {status['aggregation_in_progress']}")
                print(f"📦 Current Global Model Version: {status['current_version']}")
                print(f"📋 Min Updates Needed: {status['min_updates_needed']}")
                print(f"🚫 Rejected Updates: {status['rejected_count']}")
                
                return status
            else:
                print(f"❌ Failed to get aggregation status: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error checking aggregation status: {e}")
            return None
    
    def complete_enhanced_cycle(self):
        """Complete enhanced federated learning cycle"""
        print(f"\n🚀 Enhanced {self.client_name} Training Cycle")
        print("="*60)
        
        # Step 1: Register
        if not self.register_enhanced():
            return False
        
        # Step 2: Get global model
        if not self.get_global_model_enhanced():
            return False
        
        # Step 3: Train locally
        metrics = self.train_locally_enhanced()
        if not metrics:
            return False
        
        # Step 4: Submit update
        if not self.submit_enhanced_update(metrics):
            return False
        
        # Step 5: Check status
        status = self.get_client_status_enhanced()
        
        # Step 6: Check aggregation
        self.check_aggregation_status()
        
        print(f"\n✅ Enhanced cycle completed!")
        print(f"🌐 Global model updated from v{self.current_model_version} to v{self.current_model_version + 1}")
        print(f"📊 {self.client_name} contributed to improved fraud detection")
        print("="*60)
        
        return True

def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description='Enhanced Federated Learning Client')
    parser.add_argument('--server', required=True, help='Server URL')
    parser.add_argument('--name', required=True, help='Client name')
    parser.add_argument('--data-size', type=int, default=1000, help='Data size')
    parser.add_argument('--api-key', help='API key for enhanced features')
    parser.add_argument('--cycles', type=int, default=1, help='Number of training cycles')
    parser.add_argument('--delay', type=int, default=60, help='Delay between cycles (seconds)')
    
    args = parser.parse_args()
    
    print("🌐 Enhanced Federated Learning Client")
    print(f"🔗 Server: {args.server}")
    print(f"👥 Client: {args.name}")
    print(f"📊 Data Size: {args.data_size}")
    print(f"🔄 Cycles: {args.cycles}")
    print("="*60)
    
    client = EnhancedFederatedClient(
        server_url=args.server,
        client_name=args.name,
        data_size=args.data_size,
        api_key=args.api_key
    )
    
    for cycle in range(args.cycles):
        print(f"\n🔄 Starting Cycle {cycle + 1}/{args.cycles}")
        
        success = client.complete_enhanced_cycle()
        if not success:
            print(f"❌ Cycle {cycle + 1} failed")
            break
        
        if cycle < args.cycles - 1:
            print(f"⏳ Waiting {args.delay} seconds before next cycle...")
            time.sleep(args.delay)
    
    print(f"\n🎉 All cycles completed!")
    print(f"📊 {args.name} participated in {args.cycles} federated learning rounds")

if __name__ == '__main__':
    main()
