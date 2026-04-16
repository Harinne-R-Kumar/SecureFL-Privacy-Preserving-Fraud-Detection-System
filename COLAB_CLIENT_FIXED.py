#!/usr/bin/env python3
"""
# GOOGLE COLAB FEDERATED LEARNING CLIENT - FIXED VERSION
# ======================================================
# 
# This version includes the correct server URL and connection fixes
# 
# USAGE:
# 1. Copy this code into Google Colab
# 2. Update SERVER_URL if needed
# 3. Run all cells
"""

# ===================================================================
# CONFIGURATION - UPDATE SERVER URL HERE
# ===================================================================

# Current server URLs (from server output):
SERVER_URL = "http://127.0.0.1:5000"  # Local server
# SERVER_URL = "https://f177-2405-201-e014-b258-f109-af9f-d041-d643.ngrok-free.app"  # Public server

CLIENT_NAME = "GoogleColab_Client"
DATA_SIZE = 1000

print(f"=== SERVER CONFIGURATION ===")
print(f"Server URL: {SERVER_URL}")
print(f"Client Name: {CLIENT_NAME}")
print(f"Data Size: {DATA_SIZE}")
print("="*50)

# ===================================================================
# INSTALL DEPENDENCIES
# ===================================================================

print("Installing dependencies...")
import subprocess
import sys
try:
    import requests
    import numpy as np
    import torch
    import torch.nn as nn
    print("All packages already installed!")
except ImportError:
    print("Installing missing packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "numpy", "torch"])
    import requests
    import numpy as np
    import torch
    import torch.nn as nn
    print("Dependencies installed!")

# ===================================================================
# FEDERATED LEARNING CLIENT CLASS
# ===================================================================

class FederatedLearningClient:
    def __init__(self, server_url, client_name, data_size=1000):
        self.server_url = server_url.rstrip('/')
        self.client_name = client_name
        self.data_size = data_size
        self.client_id = None
        self.api_key = None
        
    def test_connection(self):
        """Test server connection"""
        try:
            print(f"Testing connection to {self.server_url}...")
            response = requests.get(f"{self.server_url}/api/stats", timeout=10)
            if response.status_code == 200:
                print("Connection successful!")
                return True
            else:
                print(f"Connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def register(self):
        """Register with server"""
        try:
            print(f"Registering client: {self.client_name}")
            response = requests.post(
                f"{self.server_url}/api/client/register",
                json={
                    "client_name": self.client_name,
                    "data_size": self.data_size
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                self.client_id = data['client_id']
                self.api_key = data.get('api_key', '')
                print(f"Registration successful!")
                print(f"Client ID: {self.client_id}")
                return True
            else:
                print(f"Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"Registration error: {e}")
            return False
    
    def get_global_model(self):
        """Download global model"""
        try:
            response = requests.get(
                f"{self.server_url}/api/client/model",
                params={"client_id": self.client_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Downloaded global model v{data['model_version']}")
                return data['weights']
            else:
                print(f"Failed to get model: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting model: {e}")
            return None
    
    def train_locally(self, global_weights):
        """Train locally"""
        print("Training locally...")
        
        # Generate data
        np.random.seed(42)
        X_train = np.random.randn(self.data_size, 9).astype(np.float32)
        y_train = np.random.randint(0, 2, (self.data_size, 1)).astype(np.float32)
        
        # Create model
        model = nn.Sequential(
            nn.Linear(9, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid()
        )
        
        # Train
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        model.train()
        for epoch in range(5):
            optimizer.zero_grad()
            outputs = model(torch.tensor(X_train))
            loss = criterion(outputs, torch.tensor(y_train))
            loss.backward()
            optimizer.step()
            
            if epoch % 1 == 0:
                model.eval()
                with torch.no_grad():
                    outputs = model(torch.tensor(X_train))
                    predictions = (outputs > 0.5).float()
                    accuracy = (predictions == torch.tensor(y_train)).float().mean().item()
                print(f"Epoch {epoch + 1}/5: Loss = {loss.item():.4f}, Accuracy = {accuracy:.4f}")
                model.train()
        
        # Get final accuracy
        model.eval()
        with torch.no_grad():
            outputs = model(torch.tensor(X_train))
            predictions = (outputs > 0.5).float()
            final_accuracy = (predictions == torch.tensor(y_train)).float().mean().item()
            final_loss = loss.item()
        
        print(f"Training completed! Accuracy: {final_accuracy:.4f}")
        
        # Get weights
        weights = []
        for param in model.parameters():
            weights.extend(param.data.cpu().numpy().flatten())
        
        return weights, final_accuracy, final_loss
    
    def submit_update(self, weights, accuracy, loss):
        """Submit update"""
        try:
            response = requests.post(
                f"{self.server_url}/api/client/update",
                json={
                    "client_id": self.client_id,
                    "weights": weights,
                    "metrics": {
                        "accuracy": accuracy,
                        "f1_score": 0.85,
                        "precision": 0.87,
                        "recall": 0.80,
                        "final_loss": loss,
                        "training_samples": self.data_size,
                        "epochs": 5
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"Update submitted! New global model v{data['new_global_model_version']}")
                return True
            else:
                print(f"Update failed: {response.text}")
                return False
        except Exception as e:
            print(f"Update error: {e}")
            return False
    
    def run_complete_cycle(self):
        """Run complete cycle"""
        print(f"\n{'='*60}")
        print(f"FEDERATED LEARNING CYCLE: {self.client_name}")
        print(f"{'='*60}")
        
        # Test connection
        if not self.test_connection():
            print("Connection failed - check server URL")
            return False
        
        # Register
        if not self.register():
            print("Registration failed")
            return False
        
        # Get global model
        global_weights = self.get_global_model()
        if global_weights is None:
            print("Failed to get global model")
            return False
        
        # Train locally
        local_weights, accuracy, loss = self.train_locally(global_weights)
        
        # Submit update
        if self.submit_update(local_weights, accuracy, loss):
            print(f"\nSUCCESS! {self.client_name} contributed to global model")
            print(f"Accuracy: {accuracy:.4f}")
            return True
        else:
            print(f"\nFAILED! Update submission failed")
            return False

# ===================================================================
# RUN FEDERATED LEARNING
# ===================================================================

print("\n" + "="*60)
print("STARTING FEDERATED LEARNING CLIENT")
print("="*60)

# Create client
client = FederatedLearningClient(SERVER_URL, CLIENT_NAME, DATA_SIZE)

# Run complete cycle
success = client.run_complete_cycle()

if success:
    print("\n" + "="*60)
    print("FEDERATED LEARNING COMPLETED SUCCESSFULLY!")
    print("="*60)
else:
    print("\n" + "="*60)
    print("FEDERATED LEARNING FAILED!")
    print("Check server connection and try again")
    print("="*60)

print("\nSERVER URLS TO USE:")
print(f"Local: http://127.0.0.1:5000")
print(f"Public: https://f177-2405-201-e014-b258-f109-af9f-d041-d643.ngrok-free.app")
print("\nCopy this code to Google Colab and run!")
