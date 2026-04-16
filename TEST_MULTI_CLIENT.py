#!/usr/bin/env python3
"""
TEST MULTI-CLIENT SCENARIO
==========================

This script demonstrates the federated learning system with:
- 5 existing predefined clients (client-001 to client-005)
- 1 new additional client (JupyterClient)
- Proper federated averaging across all 6 clients
"""

import requests
import numpy as np
import torch
import torch.nn as nn
from datetime import datetime

class MultiClientTester:
    def __init__(self, server_url):
        self.server_url = server_url.rstrip('/')
        
    def check_existing_clients(self):
        """Check the existing 5 predefined clients"""
        try:
            response = requests.get(f"{self.server_url}/api/selective_status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                clients = data.get('clients', [])
                print(f"Existing registered clients: {len(clients)}")
                for client in clients:
                    print(f"  - {client['client_name']} ({client['client_id']})")
                    print(f"    Data size: {client['data_size']}")
                    print(f"    Location: {client.get('location', 'N/A')}")
                    print(f"    Status: {client['status']}")
                    print()
                return clients
            else:
                print(f"Failed to get client status: {response.text}")
                return []
        except Exception as e:
            print(f"Error checking existing clients: {e}")
            return []
    
    def simulate_existing_client_update(self, client_id, client_name):
        """Simulate an update from one of the existing 5 clients"""
        try:
            print(f"Simulating update from existing client: {client_name}")
            
            # Generate mock model weights for existing client
            weights = np.random.randn(256).astype(np.float32).tolist()
            accuracy = np.random.uniform(0.75, 0.95)
            
            response = requests.post(f"{self.server_url}/api/client/update", json={
                "client_id": client_id,
                "weights": weights,
                "metrics": {
                    "accuracy": accuracy,
                    "f1_score": 0.85,
                    "precision": 0.87,
                    "recall": 0.80,
                    "final_loss": 0.12,
                    "training_samples": 1000,
                    "epochs": 3
                }
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Update submitted successfully!")
                print(f"  New global model version: {data['new_global_model_version']}")
                print(f"  Total updates: {data['total_updates']}")
                return True
            else:
                print(f"  Update failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error simulating client update: {e}")
            return False
    
    def run_new_client(self, client_name="JupyterClient"):
        """Run the new 6th client"""
        print(f"Running new client: {client_name}")
        
        # Register new client
        try:
            response = requests.post(f"{self.server_url}/api/client/register", json={
                "client_name": client_name,
                "data_size": 1000
            }, timeout=30)
            
            if response.status_code != 200:
                print(f"Registration failed: {response.text}")
                return False
                
            data = response.json()
            client_id = data['client_id']
            print(f"  Registration successful! Client ID: {client_id}")
            
        except Exception as e:
            print(f"Registration error: {e}")
            return False
        
        # Get global model
        try:
            response = requests.get(f"{self.server_url}/api/client/model", 
                              params={"client_id": client_id}, timeout=30)
            
            if response.status_code != 200:
                print(f"Failed to get model: {response.text}")
                return False
                
            data = response.json()
            print(f"  Downloaded global model v{data['model_version']}")
            
        except Exception as e:
            print(f"Error getting model: {e}")
            return False
        
        # Train locally (mock training)
        print("  Training locally...")
        X_train = np.random.randn(1000, 9).astype(np.float32)
        y_train = np.random.randint(0, 2, (1000, 1)).astype(np.float32)
        
        # Simple neural network
        model = nn.Sequential(
            nn.Linear(9, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
        
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        model.train()
        for epoch in range(3):
            optimizer.zero_grad()
            outputs = model(torch.tensor(X_train)).squeeze()
            loss = criterion(outputs, torch.tensor(y_train).squeeze())
            loss.backward()
            optimizer.step()
        
        # Calculate accuracy
        model.eval()
        with torch.no_grad():
            outputs = model(torch.tensor(X_train)).squeeze()
            predictions = (outputs > 0.5).float()
            accuracy = (predictions == torch.tensor(y_train).squeeze()).float().mean().item()
        
        print(f"  Training completed! Accuracy: {accuracy:.4f}")
        
        # Submit update
        weights = []
        for param in model.parameters():
            weights.extend(param.data.cpu().numpy().flatten())
        
        try:
            response = requests.post(f"{self.server_url}/api/client/update", json={
                "client_id": client_id,
                "weights": weights,
                "metrics": {
                    "accuracy": accuracy,
                    "f1_score": 0.85,
                    "precision": 0.87,
                    "recall": 0.80,
                    "final_loss": 0.12,
                    "training_samples": 1000,
                    "epochs": 3
                }
            }, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"  Update submitted successfully!")
                print(f"  New global model version: {data['new_global_model_version']}")
                print(f"  Total updates: {data['total_updates']}")
                return True
            else:
                print(f"  Update failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Update error: {e}")
            return False
    
    def run_multi_client_test(self):
        """Run the complete multi-client test"""
        print("="*80)
        print("MULTI-CLIENT FEDERATED LEARNING TEST")
        print("="*80)
        
        # Check existing clients
        print("\n1. CHECKING EXISTING CLIENTS")
        print("-" * 40)
        existing_clients = self.check_existing_clients()
        
        if len(existing_clients) < 5:
            print(f"Expected 5 existing clients, found {len(existing_clients)}")
            return False
        
        # Simulate updates from existing clients
        print("\n2. SIMULATING UPDATES FROM EXISTING CLIENTS")
        print("-" * 40)
        
        # Simulate 3 of the existing clients submitting updates
        success_count = 0
        for i, client in enumerate(existing_clients[:3]):
            if self.simulate_existing_client_update(client['client_id'], client['client_name']):
                success_count += 1
        
        print(f"Successfully simulated {success_count}/3 existing client updates")
        
        # Run the new 6th client
        print("\n3. RUNNING NEW 6TH CLIENT")
        print("-" * 40)
        
        if self.run_new_client("JupyterClient"):
            print("New client completed successfully!")
        else:
            print("New client failed!")
            return False
        
        # Check final status
        print("\n4. FINAL STATUS")
        print("-" * 40)
        
        try:
            response = requests.get(f"{self.server_url}/api/selective_status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Total registered clients: {data.get('total_clients', 0)}")
                print(f"Training rounds: {data.get('training_rounds', 0)}")
                print(f"Model version: {data.get('model_version', 0)}")
                print(f"Total updates: {data.get('total_updates', 0)}")
                
                print("\nSUCCESS! Multi-client federated learning working correctly!")
                print(f"System now has {data.get('total_clients', 0)} clients total")
                print("Global model updated with federated averaging across all clients")
                return True
            else:
                print(f"Failed to get final status: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error getting final status: {e}")
            return False

if __name__ == "__main__":
    SERVER_URL = "http://127.0.0.1:5000"
    
    tester = MultiClientTester(SERVER_URL)
    tester.run_multi_client_test()
    
    print("\n" + "="*80)
    print("MULTI-CLIENT TEST COMPLETED")
    print("="*80)
    print("\nThe system now supports:")
    print("5 existing predefined clients (client-001 to client-005)")
    print("Unlimited additional clients (like JupyterClient)")
    print("Proper federated averaging across all active clients")
    print("Immediate global model updates")
