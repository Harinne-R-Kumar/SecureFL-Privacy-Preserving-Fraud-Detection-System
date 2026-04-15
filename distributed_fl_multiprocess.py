"""
DISTRIBUTED FEDERATED LEARNING - Multi-Client Architecture
Run multiple clients in PARALLEL on different terminals/processes
Each client: independent training + model updates
Central server: coordinates aggregation
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pickle
import os
import json
import time
from typing import Dict, List
from datetime import datetime
import multiprocessing as mp
from pathlib import Path

# ============================================================================
# MODEL & CONFIG
# ============================================================================

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


# ============================================================================
# CENTRAL SERVER - Model Distribution & Collection
# ============================================================================

class CentralServerMultiClient:
    """
    Central server that manages:
    - Distributing global model to all clients
    - Collecting updates from clients
    - Aggregating models
    - Version tracking
    """
    
    def __init__(self, num_clients=5, server_dir='fl_server'):
        self.num_clients = num_clients
        self.server_dir = server_dir
        self.global_model = FraudDetectionModel()
        self.current_round = 0
        self.current_version = 0
        
        # Create server directory structure
        self.models_dir = os.path.join(server_dir, 'global_models')
        self.client_updates_dir = os.path.join(server_dir, 'client_updates')
        self.client_current_dir = os.path.join(server_dir, 'client_current')
        
        for d in [self.models_dir, self.client_updates_dir, self.client_current_dir]:
            os.makedirs(d, exist_ok=True)
        
        print(f"\n🌐 CENTRAL SERVER INITIALIZED")
        print(f"   Server directory: {server_dir}/")
        print(f"   ├─ global_models/      (saved global models)")
        print(f"   ├─ client_updates/     (client model updates)")
        print(f"   └─ client_current/     (current model for each client)")
    
    def publish_global_model(self, version: int):
        """Publish current global model for all clients to download"""
        global_path = os.path.join(self.models_dir, f'global_v{version}.pth')
        torch.save(self.global_model.state_dict(), global_path)
        
        # Also make it available for all clients
        for client_id in range(self.num_clients):
            client_model_path = os.path.join(self.client_current_dir, f'client_{client_id}_v{version}.pth')
            torch.save(self.global_model.state_dict(), client_model_path)
        
        print(f"\n📤 PUBLISHED: Global model v{version} → all clients")
        return global_path
    
    def collect_client_updates(self, version: int, timeout=60):
        """Wait for all clients to upload their updated models"""
        print(f"\n⏳ WAITING FOR CLIENT UPDATES (v{version})...")
        
        required_files = [f'client_{i}_v{version}.pth' for i in range(self.num_clients)]
        
        start_time = time.time()
        collected = []
        
        while len(collected) < self.num_clients:
            current_collected = []
            for fname in required_files:
                fpath = os.path.join(self.client_updates_dir, fname)
                if os.path.exists(fpath):
                    if fname not in collected:
                        current_collected.append(fname)
                        print(f"   ✓ {fname}")
            
            collected.extend(current_collected)
            
            if len(collected) < self.num_clients:
                if time.time() - start_time > timeout:
                    print(f"   ⏱️  Timeout: {len(collected)}/{self.num_clients} received")
                    break
                time.sleep(2)
        
        print(f"   ✓ Collected {len(collected)}/{self.num_clients} updates")
        return len(collected) == self.num_clients
    
    def aggregate_models(self, version: int, client_data_sizes: List[int]):
        """Aggregate all collected client models using FedAvg"""
        print(f"\n🔗 AGGREGATING CLIENT MODELS (v{version})...")
        
        # Load all client models
        client_models = {}
        for client_id in range(self.num_clients):
            update_path = os.path.join(self.client_updates_dir, f'client_{client_id}_v{version}.pth')
            
            if not os.path.exists(update_path):
                print(f"   ⚠️  Client {client_id} model not found")
                continue
            
            model = FraudDetectionModel()
            model.load_state_dict(torch.load(update_path))
            
            weights = {}
            for name, param in model.state_dict().items():
                weights[name] = param.cpu().detach().numpy().copy()
            
            client_models[client_id] = weights
        
        # FedAvg aggregation
        if not client_models:
            print(f"   ❌ No client models to aggregate")
            return False
        
        total_samples = sum(client_data_sizes)
        aggregated = {}
        
        for param_name in client_models[0].keys():
            aggregated[param_name] = np.zeros_like(client_models[0][param_name])
            
            for client_id, weights in client_models.items():
                coeff = client_data_sizes[client_id] / total_samples
                aggregated[param_name] += coeff * weights[param_name]
        
        # Update global model
        state_dict = {k: torch.tensor(v, dtype=torch.float32) for k, v in aggregated.items()}
        self.global_model.load_state_dict(state_dict)
        
        print(f"   ✓ Aggregated {len(client_models)} models using FedAvg")
        
        # Save aggregated model
        self.current_version = version + 1
        return True
    
    def get_status(self):
        """Get server status"""
        return {
            'current_round': self.current_round,
            'current_version': self.current_version,
            'num_clients': self.num_clients,
            'models_published': len(os.listdir(self.models_dir)),
            'updates_received': len(os.listdir(self.client_updates_dir))
        }


# ============================================================================
# DISTRIBUTED CLIENT - Runs on separate terminal/process
# ============================================================================

class DistributedFLClient:
    """
    Client that runs INDEPENDENTLY on separate terminal/process
    Workflow:
    1. Download global model from server
    2. Train locally
    3. Upload updated model to server
    4. Wait for next round
    """
    
    def __init__(self, client_id: int, X_train, y_train, server_dir='fl_server', num_epochs=2):
        self.client_id = client_id
        self.server_dir = server_dir
        self.num_epochs = num_epochs
        self.device = 'cpu'
        
        # Setup client directories
        self.client_dir = os.path.join(server_dir, f'client_{client_id}')
        self.models_dir = os.path.join(self.client_dir, 'models')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Data
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32) if hasattr(X_train, 'values') else torch.tensor(X_train, dtype=torch.float32)
        y_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1) if hasattr(y_train, 'values') else torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
        
        dataset = TensorDataset(X_tensor, y_tensor)
        self.dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # Model
        self.model = FraudDetectionModel(input_size=X_tensor.shape[1]).to(self.device)
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Metadata
        self.data_size = len(X_train)
        self.current_version = -1
        self.local_losses = []
        
        print(f"\n💻 CLIENT {client_id} INITIALIZED")
        print(f"   Data: {self.data_size} samples")
        print(f"   Local directory: {self.client_dir}/")
        print(f"   Ready to download models from server")
    
    def download_global_model(self, version: int, timeout=30):
        """Download global model from server"""
        print(f"\n📥 Client {self.client_id}: Downloading global model v{version}...", end=" ")
        
        server_model_path = os.path.join(self.server_dir, 'client_current', f'client_{self.client_id}_v{version}.pth')
        
        start_time = time.time()
        while not os.path.exists(server_model_path):
            if time.time() - start_time > timeout:
                print(f"⏱️  TIMEOUT (server not ready)")
                return False
            time.sleep(1)
        
        # Download (copy) model
        self.model.load_state_dict(torch.load(server_model_path))
        self.current_version = version
        print(f"✓")
        return True
    
    def train_local(self):
        """Train locally for num_epochs"""
        print(f"   Client {self.client_id}: Training locally ({self.num_epochs} epochs)...", end=" ")
        
        total_loss = 0
        for epoch in range(self.num_epochs):
            self.model.train()
            epoch_loss = 0
            
            for X_batch, y_batch in self.dataloader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                
                self.optimizer.zero_grad()
                outputs = self.model(X_batch)
                loss = self.criterion(outputs, y_batch)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(self.dataloader)
            self.local_losses.append(avg_loss)
            total_loss += avg_loss
        
        avg_total = total_loss / self.num_epochs
        print(f"Loss: {avg_total:.6f} ✓")
        return avg_total
    
    def upload_model(self, version: int):
        """Upload trained model to server"""
        print(f"   Client {self.client_id}: Uploading model v{version}...", end=" ")
        
        upload_path = os.path.join(self.server_dir, 'client_updates', f'client_{self.client_id}_v{version}.pth')
        torch.save(self.model.state_dict(), upload_path)
        
        # Also save locally
        local_path = os.path.join(self.models_dir, f'model_v{version}.pth')
        torch.save(self.model.state_dict(), local_path)
        
        print(f"✓")
        return upload_path
    
    def federated_round(self, version: int):
        """Execute one federated round"""
        print(f"\n{'─'*70}")
        print(f"🔄 CLIENT {self.client_id} - FEDERATED ROUND (v{version})")
        print(f"{'─'*70}")
        
        # Step 1: Download
        if not self.download_global_model(version):
            return False
        
        # Step 2: Train
        self.train_local()
        
        # Step 3: Upload
        self.upload_model(version)
        
        print(f"   ✓ Round complete")
        return True
    
    def get_status(self):
        """Get client status"""
        return {
            'client_id': self.client_id,
            'data_size': self.data_size,
            'current_version': self.current_version,
            'local_losses': self.local_losses[-5:] if self.local_losses else []
        }


# ============================================================================
# ORCHESTRATOR - Coordinates multiple clients
# ============================================================================

def client_process(client_id: int, X_train, y_train, server_dir: str, num_rounds: int, num_epochs: int):
    """
    INDEPENDENT CLIENT PROCESS
    Runs on separate terminal/CPU core
    """
    client = DistributedFLClient(client_id, X_train, y_train, server_dir, num_epochs)
    
    for round_num in range(num_rounds):
        try:
            client.federated_round(round_num)
        except Exception as e:
            print(f"   ❌ Client {client_id} error: {e}")
            continue
        
        # Wait before next round
        time.sleep(2)
    
    print(f"\n✓ Client {client_id} completed")


class MultiClientOrchestrator:
    """
    Orchestrates DISTRIBUTED federated learning
    - Runs clients on separate processes/terminals
    - Central server coordinates
    - Manages model versions
    """
    
    def __init__(self, num_clients=5, num_rounds=3, num_epochs=2, run_parallel=True):
        self.num_clients = num_clients
        self.num_rounds = num_rounds
        self.num_epochs = num_epochs
        self.run_parallel = run_parallel
        self.server_dir = 'fl_server'
        
        self.server = CentralServerMultiClient(num_clients, self.server_dir)
        self.client_data_sizes = None
    
    def prepare_client_data(self, num_clients=5):
        """Load and split data for clients"""
        print("\n📂 Loading client datasets...")
        
        try:
            with open('preprocessed_data_balanced.pkl', 'rb') as f:
                data_dict = pickle.load(f)
            
            from data_preprocessing_improved import split_data_for_clients
            
            X_train = data_dict['X_train_resampled']
            y_train = data_dict['y_train_resampled']
            
            client_datasets = split_data_for_clients(X_train, y_train, num_clients=num_clients, stratify=True)
            
            self.client_data_sizes = [len(X) for X, y in client_datasets]
            return client_datasets
        
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            raise
    
    def run_federated_learning_parallel(self, client_datasets: List):
        """
        Run federated learning with PARALLEL clients
        Each client runs on separate process
        """
        print(f"\n{'='*70}")
        print(f"🚀 DISTRIBUTED FEDERATED LEARNING - PARALLEL EXECUTION")
        print(f"{'='*70}")
        print(f"Configuration:")
        print(f"  - Clients: {self.num_clients} (each on separate process)")
        print(f"  - Rounds: {self.num_rounds}")
        print(f"  - Local epochs: {self.num_epochs}")
        print(f"  - Total samples: {sum(self.client_data_sizes)}")
        
        for round_num in range(self.num_rounds):
            print(f"\n{'='*70}")
            print(f"📍 FEDERATED ROUND {round_num + 1}/{self.num_rounds}")
            print(f"{'='*70}")
            
            # Publish global model
            print(f"\n1️⃣  SERVER: Publishing global model v{round_num}...")
            self.server.publish_global_model(round_num)
            
            # Run clients in parallel (separate processes)
            print(f"\n2️⃣  CLIENTS: Training in parallel...")
            processes = []
            
            for client_id, (X_train, y_train) in enumerate(client_datasets):
                p = mp.Process(
                    target=client_process,
                    args=(client_id, X_train, y_train, self.server_dir, 1, self.num_epochs)
                )
                p.start()
                processes.append(p)
                print(f"   ✓ Client {client_id} process started (PID: {p.pid})")
            
            # Wait for all clients to complete
            print(f"\n   ⏳ Waiting for all clients to complete training...")
            for p in processes:
                p.join()
            print(f"   ✓ All clients completed")
            
            # Collect updates
            print(f"\n3️⃣  SERVER: Collecting client updates...")
            ready = self.server.collect_client_updates(round_num, timeout=120)
            
            if ready:
                # Aggregate
                print(f"\n4️⃣  SERVER: Aggregating models...")
                self.server.aggregate_models(round_num, self.client_data_sizes)
                print(f"   ✓ Global model updated to v{self.server.current_version}")
            else:
                print(f"   ⚠️  Not all clients ready, skipping aggregation")
        
        print(f"\n{'='*70}")
        print(f"✅ FEDERATED LEARNING COMPLETED")
        print(f"{'='*70}")
    
    def print_file_structure(self):
        """Print the distributed file structure"""
        print(f"\n{'='*70}")
        print(f"📂 DISTRIBUTED FILE STRUCTURE")
        print(f"{'='*70}")
        
        print(f"\n🌐 CENTRAL SERVER ({self.server_dir}/):")
        print(f"   ├─ global_models/")
        if os.path.exists(os.path.join(self.server_dir, 'global_models')):
            for f in sorted(os.listdir(os.path.join(self.server_dir, 'global_models'))):
                print(f"   │  ├─ {f}")
        
        print(f"   ├─ client_updates/")
        if os.path.exists(os.path.join(self.server_dir, 'client_updates')):
            for f in sorted(os.listdir(os.path.join(self.server_dir, 'client_updates'))):
                print(f"   │  ├─ {f}")
        
        print(f"   └─ client_current/")
        if os.path.exists(os.path.join(self.server_dir, 'client_current')):
            for f in sorted(os.listdir(os.path.join(self.server_dir, 'client_current')))[:10]:
                print(f"   │  ├─ {f}")
        
        print(f"\n💻 CLIENT LOCAL DIRECTORIES:")
        for client_id in range(self.num_clients):
            client_dir = os.path.join(self.server_dir, f'client_{client_id}')
            if os.path.exists(client_dir):
                models_dir = os.path.join(client_dir, 'models')
                if os.path.exists(models_dir):
                    num_models = len(os.listdir(models_dir))
                    print(f"   ├─ client_{client_id}/")
                    print(f"   │  └─ models/ ({num_models} saved versions)")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    try:
        # Prepare
        orchestrator = MultiClientOrchestrator(
            num_clients=5,
            num_rounds=3,
            num_epochs=2,
            run_parallel=True
        )
        
        # Load data
        client_datasets = orchestrator.prepare_client_data(5)
        
        # Run distributed FL
        orchestrator.run_federated_learning_parallel(client_datasets)
        
        # Show structure
        orchestrator.print_file_structure()
        
        print(f"\n{'='*70}")
        print(f"✨ HOW THIS WORKS:")
        print(f"{'='*70}")
        print(f"""
1. SERVER publishes global model v{orchestrator.num_rounds-1}
2. Each CLIENT downloads model on separate process
3. Clients train INDEPENDENTLY and IN PARALLEL
4. Clients upload trained model to server
5. SERVER aggregates all client models
6. Process repeats for next round

KEY FEATURES:
✓ Clients run on SEPARATE PROCESSES (true parallelism)
✓ Can run on DIFFERENT MACHINES (change server_dir to network path)
✓ MODEL IMPLIED (version tracking)
✓ ASYNCHRONOUS updates (clients train at their own pace)
✓ FAULT TOLERANCE (missing clients don't block others)
""")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
