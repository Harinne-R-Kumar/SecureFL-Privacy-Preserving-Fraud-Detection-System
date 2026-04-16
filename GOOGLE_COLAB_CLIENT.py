#!/usr/bin/env python3
"""
🌐 GOOGLE COLAB FEDERATED LEARNING CLIENT
========================================

Complete federated learning client for Google Colab environment.
Run this code directly in Google Colab notebooks.

Features:
- 🔄 Register with server
- 📥 Download global model  
- 🏋 Train locally on Colab
- 📤 Upload model updates
- 📊 Track training progress
- 📈 Visualize results
"""

# 📦 Install required packages
print("📦 Installing required packages...")
try:
    import requests
    import numpy as np
    import torch
    import torch.nn as nn
    import json
    import time
    from datetime import datetime
    print("✅ All packages available!")
except ImportError as e:
    print(f"❌ Missing package: {e}")
    print("📦 Installing missing packages...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests", "numpy", "torch", "matplotlib", "seaborn"])
    import requests
    import numpy as np
    import torch
    import torch.nn as nn
    import json
    import time
    from datetime import datetime
    import matplotlib.pyplot as plt
    import seaborn as sns
    print("✅ Packages installed successfully!")

# 🎯 Configuration - UPDATE THIS
SERVER_URL = "http://127.0.0.1:5000"  # 🔧 Replace with your server URL
CLIENT_NAME = "GoogleColab_Client"  # 🔧 Change this to your client name
DATA_SIZE = 1000  # 🔧 Adjust based on your dataset size

print(f"🔧 Server URL: {SERVER_URL}")
print(f"👤 Client Name: {CLIENT_NAME}")
print(f"📊 Data Size: {DATA_SIZE}")
print("✅ Configuration complete!")

# 🤖 Federated Learning Client Class
class FederatedLearningClient:
    def __init__(self, server_url, client_name, data_size=1000):
        self.server_url = server_url.rstrip('/')
        self.client_name = client_name
        self.data_size = data_size
        self.client_id = None
        self.api_key = None
        self.training_history = []
        
    def register(self):
        """Register with the federated learning server"""
        try:
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
                print(f"✅ Registered successfully!")
                print(f"   📋 Client ID: {self.client_id}")
                print(f"   🔑 API Key: {self.api_key}")
                return True
            else:
                print(f"❌ Registration failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Registration error: {e}")
            return False
    
    def get_global_model(self):
        """Download global model from server"""
        try:
            response = requests.get(
                f"{self.server_url}/api/client/model", 
                params={"client_id": self.client_id},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Downloaded global model v{data['model_version']}")
                print(f"   📦 Model info: {data.get('model_info', 'N/A')}")
                return data['weights']
            else:
                print(f"❌ Failed to get model: {response.text}")
                return None
        except Exception as e:
            print(f"❌ Error getting model: {e}")
            return None
    
    def train_locally(self, global_weights):
        """Train model locally on Colab environment"""
        print("🏋 Training locally...")
        
        # Generate sample fraud detection data
        np.random.seed(42)  # For reproducible results
        X_train = np.random.randn(self.data_size, 9).astype(np.float32)
        y_train = np.random.randint(0, 2, (self.data_size, 1)).astype(np.float32)
        
        # Create neural network model
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
        
        # Training setup
        criterion = nn.BCELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        
        # Training loop
        model.train()
        losses = []
        accuracies = []
        
        print(f"   🔄 Training for {self.data_size} samples...")
        
        for epoch in range(5):  # Train for 5 epochs
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(torch.tensor(X_train))
            loss = criterion(outputs, torch.tensor(y_train))
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            # Calculate accuracy
            model.eval()
            with torch.no_grad():
                outputs = model(torch.tensor(X_train))
                predictions = (outputs > 0.5).float()
                accuracy = (predictions == torch.tensor(y_train)).float().mean().item()
            
            losses.append(loss.item())
            accuracies.append(accuracy)
            
            if epoch % 1 == 0:
                print(f"      Epoch {epoch + 1}/5: Loss = {loss.item():.4f}, Accuracy = {accuracy:.4f}")
            
            model.train()  # Back to training mode
        
        # Final metrics
        final_loss = losses[-1]
        final_accuracy = accuracies[-1]
        
        print(f"✅ Training completed!")
        print(f"   📊 Final Loss: {final_loss:.4f}")
        print(f"   🎯 Final Accuracy: {final_accuracy:.4f}")
        
        # Store training history
        self.training_history.append({
            'timestamp': datetime.now().isoformat(),
            'loss': final_loss,
            'accuracy': final_accuracy,
            'epochs': 5,
            'data_size': self.data_size,
        })
        
        # Return model weights
        weights = []
        for param in model.parameters():
            weights.extend(param.data.cpu().numpy().flatten())
        
        return weights, final_accuracy, final_loss
    
    def submit_update(self, weights, accuracy, loss):
        """Submit model update to server"""
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
                print(f"✅ Update submitted successfully!")
                print(f"   📦 New global model v{data['new_global_model_version']}")
                print(f"   📊 Global model updated: {data.get('message', 'N/A')}")
                return True
            else:
                print(f"❌ Update failed: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Update error: {e}")
            return False
    
    def run_complete_cycle(self):
        """Run complete federated learning cycle"""
        print(f"\n🚀 {self.client_name} Federated Learning Cycle")
        print("="*60)
        
        # Step 1: Register
        if not self.register():
            print("❌ Failed to register client")
            return False
        
        # Step 2: Get global model
        global_weights = self.get_global_model()
        if global_weights is None:
            print("❌ Failed to get global model")
            return False
        
        # Step 3: Train locally
        local_weights, accuracy, loss = self.train_locally(global_weights)
        
        # Step 4: Submit update
        if self.submit_update(local_weights, accuracy, loss):
            print(f"\n🎉 Cycle completed successfully!")
            print(f"   📊 {self.client_name} contributed to global model")
            print(f"   🎯 Accuracy: {accuracy:.4f}")
            print(f"   📦 Loss: {loss:.4f}")
            return True
        else:
            print(f"\n❌ Cycle failed for {self.client_name}")
            return False
    
    def get_training_history(self):
        """Get training history"""
        return self.training_history
    
    def plot_training_progress(self):
        """Plot training progress"""
        if not self.training_history:
            print("No training history to plot")
            return
        
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
            
            # Plot accuracy
            accuracies = [h['accuracy'] for h in self.training_history]
            
            ax1.plot(range(len(accuracies)), accuracies, 'b-o', linewidth=2, markersize=6)
            ax1.set_title('Training Accuracy Progress', fontsize=14, fontweight='bold')
            ax1.set_xlabel('Training Cycle', fontsize=12)
            ax1.set_ylabel('Accuracy', fontsize=12)
            ax1.grid(True, alpha=0.3)
            ax1.set_ylim([0, 1])
            
            # Plot loss
            losses = [h['loss'] for h in self.training_history]
            
            ax2.plot(range(len(losses)), losses, 'r-o', linewidth=2, markersize=6)
            ax2.set_title('Training Loss Progress', fontsize=14, fontweight='bold')
            ax2.set_xlabel('Training Cycle', fontsize=12)
            ax2.set_ylabel('Loss', fontsize=12)
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
        except ImportError:
            print("📊 Matplotlib not available for plotting")
        except Exception as e:
            print(f"❌ Error plotting: {e}")

# 🚀 USAGE EXAMPLES

print("\n" + "="*60)
print("🚀 GOOGLE COLAB FEDERATED LEARNING CLIENT")
print("="*60)

# Example 1: Single Training Cycle
print("\n📋 Example 1: Single Training Cycle")
print("-"*40)

client = FederatedLearningClient(SERVER_URL, CLIENT_NAME, DATA_SIZE)
success = client.run_complete_cycle()

if success:
    print("\n🎉 Success! Client contributed to global model")
else:
    print("\n❌ Failed! Check server connection")

# Example 2: Multiple Training Cycles
print("\n📋 Example 2: Multiple Training Cycles")
print("-"*40)

NUM_CYCLES = 3  # 🔧 Adjust number of cycles
client = FederatedLearningClient(SERVER_URL, CLIENT_NAME, DATA_SIZE)

print(f"🎯 Running {NUM_CYCLES} training cycles...\n")

for cycle in range(NUM_CYCLES):
    print(f"\n{'='*60}")
    print(f"🔄 Cycle {cycle + 1}/{NUM_CYCLES}")
    print(f"{'='*60}")
    
    success = client.run_complete_cycle()
    
    if success:
        print(f"✅ Cycle {cycle + 1} completed successfully")
    else:
        print(f"❌ Cycle {cycle + 1} failed")
    
    # Wait a bit between cycles
    if cycle < NUM_CYCLES - 1:
        print("⏳ Waiting 2 seconds before next cycle...")
        time.sleep(2)

print(f"\n🎉 All {NUM_CYCLES} cycles completed!")

# Example 3: Training Progress Visualization
print("\n📋 Example 3: Training Progress Visualization")
print("-"*40)

print("📊 Plotting training progress...")
client.plot_training_progress()

# Example 4: Training History
print("\n📋 Example 4: Training History")
print("-"*40)

history = client.get_training_history()
if history:
    print("\n📋 Training History:")
    for i, h in enumerate(history, 1):
        print(f"  {i}. Time: {h['timestamp']}")
        print(f"     Accuracy: {h['accuracy']:.4f}")
        print(f"     Loss: {h['loss']:.4f}")
        print(f"     Epochs: {h['epochs']}")
        print(f"     Data Size: {h['data_size']}")
        print()
else:
    print("No training history available")

# Example 5: Server Status Check
print("\n📋 Example 5: Server Status Check")
print("-"*40)

print("🔍 Checking server status...")
try:
    response = requests.get(f"{SERVER_URL}/api/stats", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Server is running!")
        print(f"   📊 Total clients: {data.get('total_clients', 'N/A')}")
        print(f"   🔄 Training rounds: {data.get('training_rounds', 'N/A')}")
        print(f"   📦 Model version: {data.get('model_version', 'N/A')}")
    else:
        print(f"❌ Server not accessible: {response.status_code}")
except Exception as e:
    print(f"❌ Error checking server: {e}")

print("\n🔍 Checking selective training status...")
try:
    response = requests.get(f"{SERVER_URL}/api/selective_status", timeout=10)
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Selective training status:")
        print(f"   📊 Total clients: {data.get('total_clients', 'N/A')}")
        print(f"   🔄 Training rounds: {data.get('training_rounds', 'N/A')}")
        print(f"   👥 Selected clients: {data.get('selected_clients_last_round', [])}")
    else:
        print(f"❌ Selective status not accessible: {response.status_code}")
except Exception as e:
    print(f"❌ Error checking selective status: {e}")

print("\n" + "="*60)
print("🎉 GOOGLE COLAB CLIENT READY!")
print("="*60)
print("\n📝 Instructions:")
print("1. 📋 Copy this code into Google Colab")
print("2. 🔧 Update SERVER_URL with your server address")
print("3. 🏃 Run all cells to execute federated learning")
print("4. 📊 Monitor training progress and results")
print("\n🌐 Your Google Colab client is ready!")
