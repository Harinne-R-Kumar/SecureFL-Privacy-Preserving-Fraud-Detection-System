#!/usr/bin/env python3
"""
FEDERATED LEARNING CLIENT
Connects to the ngrok-enabled server and participates in federated learning
"""

import requests
import json
import time
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime
import argparse
import sys
import threading
from typing import Dict, Any, Optional

class FraudDetectionModel(nn.Module):
    """Simple fraud detection model for client training"""
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

class FederatedLearningClient:
    def __init__(self, server_url: str, client_name: str, data_size: int = 1000):
        self.server_url = server_url.rstrip('/')
        self.client_name = client_name
        self.data_size = data_size
        self.client_id = None
        self.model = FraudDetectionModel()
        self.heartbeat_interval = 30  # seconds
        self.training_interval = 60  # seconds
        self.running = False
        
    def register_client(self) -> bool:
        """Register this client with the server"""
        try:
            payload = {
                'client_name': self.client_name,
                'data_size': self.data_size,
                'location': 'Local Machine'
            }
            
            response = requests.post(
                f"{self.server_url}/api/client/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data['client_id']
                print(f"✅ Successfully registered as {self.client_name}")
                print(f"🆔 Client ID: {self.client_id}")
                print(f"📊 Data Size: {self.data_size} samples")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering client: {e}")
            return False
    
    def send_heartbeat(self) -> bool:
        """Send heartbeat to server"""
        if not self.client_id:
            return False
            
        try:
            response = requests.post(
                f"{self.server_url}/api/client/heartbeat",
                json={'client_id': self.client_id},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"💓 Heartbeat sent at {datetime.now().strftime('%H:%M:%S')}")
                return True
            else:
                print(f"❌ Heartbeat failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending heartbeat: {e}")
            return False
    
    def get_global_model(self) -> Optional[Dict]:
        """Get current global model from server"""
        if not self.client_id:
            return None
            
        try:
            response = requests.get(
                f"{self.server_url}/api/client/model",
                params={'client_id': self.client_id},
                timeout=10
            )
            
            if response.status_code == 200:
                model_info = response.json()
                print(f"📥 Received global model v{model_info['model_version']}")
                return model_info
            else:
                print(f"❌ Failed to get global model: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error getting global model: {e}")
            return None
    
    def generate_mock_data(self, num_samples: int = 100):
        """Generate mock training data for demonstration"""
        # Generate realistic-looking transaction data
        np.random.seed(42)  # For reproducible results
        
        data = {
            'amount': np.random.uniform(1, 5000, num_samples),
            'time': np.random.randint(0, 24, num_samples),
            'type': np.random.randint(0, 5, num_samples),
            'device': np.random.randint(0, 3, num_samples),
            'location': np.random.randint(0, 10, num_samples),
            'prev_fraud': np.random.randint(0, 3, num_samples),
            'age': np.random.randint(30, 365, num_samples),
            'trans_24h': np.random.randint(1, 20, num_samples),
            'payment': np.random.randint(0, 4, num_samples)
        }
        
        # Create labels (fraud indicators) - make it somewhat realistic
        # Higher amounts, unusual times, and previous fraud increase fraud probability
        fraud_prob = (
            (data['amount'] > 2000).astype(float) * 0.3 +
            ((data['time'] < 6) | (data['time'] > 22)).astype(float) * 0.2 +
            (data['prev_fraud'] > 0).astype(float) * 0.4 +
            np.random.uniform(0, 0.3, num_samples)
        )
        
        labels = (fraud_prob > 0.5).astype(float)
        
        # Convert to features tensor
        features = np.column_stack([
            data['amount'], data['time'], data['type'], data['device'],
            data['location'], data['prev_fraud'], data['age'],
            data['trans_24h'], data['payment']
        ])
        
        # Normalize features
        features = (features - features.mean(axis=0)) / (features.std(axis=0) + 1e-8)
        
        return torch.tensor(features, dtype=torch.float32), torch.tensor(labels, dtype=torch.float32).unsqueeze(1)
    
    def train_local_model(self, epochs: int = 3) -> Dict[str, Any]:
        """Train model locally on mock data"""
        print(f"🏋️ Training local model for {epochs} epochs...")
        
        # Generate training data
        X_train, y_train = self.generate_mock_data(min(self.data_size, 500))
        
        # Setup training
        criterion = nn.BCEWithLogitsLoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        
        self.model.train()
        epoch_losses = []
        
        for epoch in range(epochs):
            optimizer.zero_grad()
            
            # Forward pass
            outputs = self.model(X_train)
            loss = criterion(outputs, y_train)
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            epoch_losses.append(loss.item())
            print(f"  Epoch {epoch+1}/{epochs}: Loss = {loss.item():.4f}")
        
        # Calculate metrics
        self.model.eval()
        with torch.no_grad():
            outputs = self.model(X_train)
            predictions = torch.sigmoid(outputs)
            predicted_labels = (predictions > 0.5).float()
            
            accuracy = (predicted_labels == y_train).float().mean().item()
            
            # Simple F1 calculation
            tp = ((predicted_labels == 1) & (y_train == 1)).float().sum().item()
            fp = ((predicted_labels == 1) & (y_train == 0)).float().sum().item()
            fn = ((predicted_labels == 0) & (y_train == 1)).float().sum().item()
            
            precision = tp / (tp + fp + 1e-8)
            recall = tp / (tp + fn + 1e-8)
            f1_score = 2 * (precision * recall) / (precision + recall + 1e-8)
        
        metrics = {
            'accuracy': accuracy,
            'f1_score': f1_score,
            'precision': precision,
            'recall': recall,
            'final_loss': epoch_losses[-1],
            'training_samples': len(X_train),
            'epochs': epochs
        }
        
        print(f"✅ Training completed - Accuracy: {accuracy:.4f}, F1: {f1_score:.4f}")
        return metrics
    
    def get_model_weights(self) -> list:
        """Extract model weights as a list"""
        weights = []
        for param in self.model.parameters():
            weights.extend(param.data.cpu().numpy().flatten())
        return weights.tolist()
    
    def submit_update(self, metrics: Dict[str, Any]) -> bool:
        """Submit model update to server"""
        if not self.client_id:
            return False
            
        try:
            weights = self.get_model_weights()
            
            payload = {
                'client_id': self.client_id,
                'weights': weights,
                'metrics': metrics,
                'timestamp': datetime.now().isoformat()
            }
            
            response = requests.post(
                f"{self.server_url}/api/client/update",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"📤 Model update submitted successfully!")
                print(f"🔄 New global model version: {data['new_model_version']}")
                print(f"📊 Total updates on server: {data['total_updates']}")
                return True
            else:
                print(f"❌ Failed to submit update: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error submitting update: {e}")
            return False
    
    def heartbeat_loop(self):
        """Continuous heartbeat loop"""
        while self.running:
            self.send_heartbeat()
            time.sleep(self.heartbeat_interval)
    
    def training_loop(self):
        """Continuous training and update loop"""
        while self.running:
            print(f"\n🔄 Starting training cycle at {datetime.now().strftime('%H:%M:%S')}")
            
            # Get global model (in real implementation, would load weights)
            model_info = self.get_global_model()
            
            # Train locally
            metrics = self.train_local_model()
            
            # Submit update
            self.submit_update(metrics)
            
            print(f"⏳ Waiting {self.training_interval} seconds for next cycle...")
            time.sleep(self.training_interval)
    
    def start(self, continuous: bool = True):
        """Start the federated learning client"""
        print(f"🚀 Starting Federated Learning Client")
        print(f"🌐 Server URL: {self.server_url}")
        print(f"👤 Client Name: {self.client_name}")
        
        # Register with server
        if not self.register_client():
            print("❌ Failed to register with server. Exiting...")
            return
        
        self.running = True
        
        if continuous:
            # Start background threads
            heartbeat_thread = threading.Thread(target=self.heartbeat_loop, daemon=True)
            training_thread = threading.Thread(target=self.training_loop, daemon=True)
            
            heartbeat_thread.start()
            training_thread.start()
            
            print("✅ Client started in continuous mode")
            print("💓 Sending heartbeats every 30 seconds")
            print("🏋️ Training and updating every 60 seconds")
            print("⏹️ Press Ctrl+C to stop")
            
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping client...")
                self.running = False
                print("✅ Client stopped")
        else:
            # Single training cycle
            print("🔄 Running single training cycle...")
            model_info = self.get_global_model()
            metrics = self.train_local_model()
            self.submit_update(metrics)
            print("✅ Single cycle completed")

def main():
    parser = argparse.ArgumentParser(description='Federated Learning Client')
    parser.add_argument('--server', required=True, help='Server URL (e.g., https://abc123.ngrok.io)')
    parser.add_argument('--name', default='MyClient', help='Client name')
    parser.add_argument('--data-size', type=int, default=1000, help='Training data size')
    parser.add_argument('--single', action='store_true', help='Run single training cycle instead of continuous')
    
    args = parser.parse_args()
    
    # Create and start client
    client = FederatedLearningClient(
        server_url=args.server,
        client_name=args.name,
        data_size=args.data_size
    )
    
    client.start(continuous=not args.single)

if __name__ == '__main__':
    main()
