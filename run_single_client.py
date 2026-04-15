"""
DISTRIBUTED FL - SINGLE CLIENT SIMULATOR
Shows how a SINGLE CLIENT would run on a separate terminal
Can be replicated for Client 0, 1, 2, 3, 4 in different terminals
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import time
import os
import json

class FraudDetectionModel(nn.Module):
    def __init__(self, input_size=9):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.net(x)


def run_single_client_fl(client_id: int, X_train, y_train, num_rounds=3):
    """
    SINGLE CLIENT FEDERATED LEARNING
    Run this on SEPARATE terminal per client
    Example:
      Terminal 1: python run_single_client.py 0
      Terminal 2: python run_single_client.py 1
      Terminal 3: python run_single_client.py 2
      Terminal 4: python run_single_client.py 3
      Terminal 5: python run_single_client.py 4
    """
    
    # Setup directories
    server_dir = 'fl_server'
    model_dir = os.path.join(server_dir, 'client_current')
    upload_dir = os.path.join(server_dir, 'client_updates')
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Data
    X_tensor = torch.tensor(X_train.values, dtype=torch.float32)
    y_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1)
    dataset = TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
    
    # Model
    model = FraudDetectionModel(input_size=X_tensor.shape[1])
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    data_size = len(X_train)
    
    print(f"\n{'='*70}")
    print(f"💻 CLIENT {client_id} - FEDERATED LEARNING")
    print(f"{'='*70}")
    print(f"Data size: {data_size} samples")
    print(f"Server directory: {server_dir}/")
    print(f"Running {num_rounds} federated rounds...")
    
    for round_num in range(num_rounds):
        print(f"\n{'─'*70}")
        print(f"🔄 ROUND {round_num + 1}/{num_rounds}")
        print(f"{'─'*70}")
        
        # Step 1: Download global model from server
        print(f"\n1️⃣  DOWNLOAD: Fetching global model from server...")
        global_model_path = os.path.join(model_dir, f'client_{client_id}_v{round_num}.pth')
        
        # Wait for server to publish model
        timeout = 60
        start = time.time()
        while not os.path.exists(global_model_path):
            if time.time() - start > timeout:
                print(f"   ⏱️  TIMEOUT: Server didn't publish model")
                return
            time.sleep(1)
        
        model.load_state_dict(torch.load(global_model_path))
        print(f"   ✓ Downloaded: {global_model_path}")
        
        # Step 2: Train locally
        print(f"\n2️⃣  TRAIN: Training locally on {data_size} samples...")
        for epoch in range(2):  # 2 local epochs
            model.train()
            epoch_loss = 0
            for X_batch, y_batch in dataloader:
                optimizer.zero_grad()
                outputs = model(X_batch)
                loss = criterion(outputs, y_batch)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(dataloader)
            print(f"   Epoch {epoch+1}/2: Loss {avg_loss:.6f}")
        
        # Step 3: Upload updated model to server
        print(f"\n3️⃣  UPLOAD: Sending trained model to server...")
        upload_path = os.path.join(upload_dir, f'client_{client_id}_v{round_num}.pth')
        torch.save(model.state_dict(), upload_path)
        print(f"   ✓ Uploaded: {upload_path}")
        
        print(f"\n✓ Round {round_num + 1} complete - waiting for aggregation...")
        time.sleep(3)
    
    print(f"\n{'='*70}")
    print(f"✅ CLIENT {client_id} COMPLETED ALL ROUNDS")
    print(f"{'='*70}")


if __name__ == '__main__':
    import sys
    import pickle
    from data_preprocessing_improved import split_data_for_clients
    
    # Get client ID from command line
    if len(sys.argv) > 1:
        client_id = int(sys.argv[1])
    else:
        print("Usage: python run_single_client.py <client_id>")
        print("Example:")
        print("  Terminal 1: python run_single_client.py 0")
        print("  Terminal 2: python run_single_client.py 1")
        print("  Terminal 3: python run_single_client.py 2")
        sys.exit(1)
    
    # Load data
    print("\n📂 Loading client data...")
    with open('preprocessed_data_balanced.pkl', 'rb') as f:
        data_dict = pickle.load(f)
    
    client_datasets = split_data_for_clients(
        data_dict['X_train_resampled'],
        data_dict['y_train_resampled'],
        num_clients=5,
        stratify=True
    )
    
    X_train, y_train = client_datasets[client_id]
    
    # Run this client
    run_single_client_fl(client_id, X_train, y_train, num_rounds=3)
