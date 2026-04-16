#!/usr/bin/env python3
"""
CLIENT MODEL UPDATE EXAMPLE FOR REAL-TIME FEDERATED LEARNING
Shows exactly how Client 2 (or any client) can update their model
"""

import requests
import json
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime

class ClientModel(nn.Module):
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

class FederatedClient:
    def __init__(self, server_url, client_name="Client2", data_size=2000):
        self.server_url = server_url.rstrip('/')
        self.client_name = client_name
        self.data_size = data_size
        self.client_id = None
        self.model = ClientModel()
        
    def register_client(self):
        """Step 1: Register this client with the server"""
        print(f"🔐 Registering {self.client_name} with server...")
        
        payload = {
            'client_name': self.client_name,
            'data_size': self.data_size,
            'location': 'Remote Location'
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/client/register",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data['client_id']
                print(f"✅ Successfully registered!")
                print(f"🆔 Client ID: {self.client_id}")
                print(f"📊 Data Size: {self.data_size} samples")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error registering: {e}")
            return False
    
    def get_global_model(self):
        """Step 2: Get current global model from server"""
        if not self.client_id:
            print("❌ Must register first!")
            return False
            
        print(f"📥 Downloading global model...")
        
        try:
            response = requests.get(
                f"{self.server_url}/api/client/model",
                params={'client_id': self.client_id},
                timeout=10
            )
            
            if response.status_code == 200:
                model_data = response.json()
                print(f"✅ Received global model v{model_data['model_version']}")
                
                # Load weights into local model
                weights = model_data['weights']
                self.load_weights_into_model(weights)
                
                return True
            else:
                print(f"❌ Failed to get model: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting model: {e}")
            return False
    
    def load_weights_into_model(self, weights):
        """Load weights into the model"""
        try:
            offset = 0
            for param in self.model.parameters():
                param_size = param.data.numel()
                param_weights = weights[offset:offset + param_size]
                param.data = torch.tensor(param_weights).reshape(param.data.shape).float()
                offset += param_size
            print(f"✅ Weights loaded into local model")
            return True
        except Exception as e:
            print(f"❌ Error loading weights: {e}")
            return False
    
    def train_locally(self, epochs=3):
        """Step 3: Train model locally on private data"""
        print(f"🏋️ Training local model for {epochs} epochs...")
        
        # Generate mock training data (in real scenario, this would be client's private data)
        np.random.seed(42)
        X_train = np.random.randn(100, 9).astype(np.float32)
        y_train = np.random.randint(0, 2, (100, 1)).astype(np.float32)
        
        X_train = torch.tensor(X_train)
        y_train = torch.tensor(y_train)
        
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
        
        print(f"✅ Training completed!")
        print(f"📊 Accuracy: {accuracy:.4f}, F1: {f1_score:.4f}")
        
        return metrics
    
    def submit_update(self, metrics):
        """Step 4: Submit trained model to server"""
        if not self.client_id:
            print("❌ Must register first!")
            return False
            
        print(f"📤 Submitting model update to server...")
        
        # Extract model weights
        weights = []
        for param in self.model.parameters():
            weights.extend(param.data.cpu().numpy().flatten())
        
        payload = {
            'client_id': self.client_id,
            'weights': weights,
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/client/update",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Update submitted successfully!")
                print(f"🔄 New global model version: {data['new_global_model_version']}")
                print(f"📊 Total updates on server: {data['total_updates']}")
                print(f"🎯 Your contributions: {data['your_contributions']}")
                return True
            else:
                print(f"❌ Failed to submit update: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error submitting update: {e}")
            return False
    
    def send_heartbeat(self):
        """Send heartbeat to maintain connection"""
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
    
    def complete_update_cycle(self):
        """Complete real-time update cycle"""
        print(f"\n🚀 Starting {self.client_name} Real-Time Update Cycle")
        print("="*60)
        
        # Step 1: Register
        if not self.register_client():
            return False
        
        # Step 2: Get global model
        if not self.get_global_model():
            return False
        
        # Step 3: Train locally
        metrics = self.train_locally()
        
        # Step 4: Submit update
        if not self.submit_update(metrics):
            return False
        
        # Step 5: Send heartbeat
        self.send_heartbeat()
        
        print(f"\n✅ {self.client_name} update cycle completed!")
        print(f"🌐 Global model has been updated with {self.client_name}'s contribution")
        print("="*60)
        
        return True

def main():
    """Main function to demonstrate Client 2 update process"""
    
    # Server configuration
    SERVER_URL = "http://127.0.0.1:5000"  # Your server URL
    
    print("🔥 CLIENT 2 REAL-TIME MODEL UPDATE DEMO")
    print("="*60)
    print(f"🌐 Server URL: {SERVER_URL}")
    print(f"👥 Client Name: Client2")
    print(f"📊 Data Size: 2000 samples")
    print("="*60)
    
    # Create client instance
    client2 = FederatedClient(
        server_url=SERVER_URL,
        client_name="Client2",
        data_size=2000
    )
    
    # Execute complete update cycle
    success = client2.complete_update_cycle()
    
    if success:
        print("\n🎉 SUCCESS! Client 2 has updated the global model!")
        print("\n💡 To see the update in real-time:")
        print("1. Check the dashboard at: http://127.0.0.1:5000")
        print("2. Look at: http://127.0.0.1:5000/api/advanced-fl/dashboard")
        print("3. Check client status: http://127.0.0.1:5000/api/client/status")
        print("\n🔄 The global model version should increment!")
        print("📊 Active clients count should increase!")
        print("📈 Model updates count should increase!")
    else:
        print("\n❌ Client 2 update failed. Check server connection.")

if __name__ == '__main__':
    main()
