"""
FEDERATED LEARNING WITH PERSISTENT CLIENT MODELS
- Train 5 clients independently
- SAVE each client model to client_models/ folder
- Aggregate from saved files
- Save central aggregated model
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pickle
import os
from typing import List, Dict, Tuple
from datetime import datetime
import json
import shutil

# ============================================================================
# MODEL ARCHITECTURE
# ============================================================================
class FraudDetectionModel(nn.Module):
    """Neural network for fraud detection"""
    def __init__(self, input_size=9):
        super(FraudDetectionModel, self).__init__()
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
# CLIENT WITH PERSISTENT STORAGE
# ============================================================================
class FLClientPersistent:
    """
    FL Client that SAVES its trained model to disk.
    Each client: independent training + model file storage
    """
    
    def __init__(self, client_id: int, X_train, y_train, client_models_dir='client_models', device='cpu'):
        self.client_id = client_id
        self.device = device
        self.client_models_dir = client_models_dir
        
        # Create client_models directory if not exists
        if not os.path.exists(client_models_dir):
            os.makedirs(client_models_dir)
            print(f"✓ Created directory: {client_models_dir}/")
        
        # Client model file path
        self.model_filepath = os.path.join(client_models_dir, f'client_{client_id}_model.pth')
        
        # Convert to tensors
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32) if hasattr(X_train, 'values') else torch.tensor(X_train, dtype=torch.float32)
        y_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1) if hasattr(y_train, 'values') else torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
        
        # Create dataloader
        dataset = TensorDataset(X_tensor, y_tensor)
        self.dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # Initialize model
        self.model = FraudDetectionModel(input_size=X_tensor.shape[1]).to(device)
        self.criterion = nn.BCELoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Metrics
        self.training_losses = []
        self.data_size = len(X_train)
        
        print(f"✓ Client {client_id} initialized with {self.data_size} samples")
        print(f"  Model will be saved to: {self.model_filepath}")
    
    def train_local_epoch(self, epochs: int = 1) -> float:
        """Train model locally"""
        total_loss = 0
        
        for epoch in range(epochs):
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
            
            avg_epoch_loss = epoch_loss / len(self.dataloader)
            self.training_losses.append(avg_epoch_loss)
            total_loss += avg_epoch_loss
        
        return total_loss / epochs
    
    def save_model(self):
        """Save trained model to disk"""
        torch.save(self.model.state_dict(), self.model_filepath)
        return self.model_filepath
    
    def load_model(self, filepath: str = None):
        """Load model from disk"""
        path = filepath or self.model_filepath
        self.model.load_state_dict(torch.load(path, map_location=self.device))
    
    def get_model_path(self):
        """Get the path where this client's model is saved"""
        return self.model_filepath


# ============================================================================
# CENTRAL SERVER WITH AGGREGATION
# ============================================================================
class CentralFLServer:
    """
    Central server that:
    1. Sends global model to clients
    2. Collects trained models from client_models/ folder
    3. Aggregates using FedAvg
    4. Saves aggregated result
    """
    
    def __init__(self, num_clients: int = 5, input_size: int = 9, client_models_dir='client_models'):
        self.num_clients = num_clients
        self.input_size = input_size
        self.client_models_dir = client_models_dir
        
        # Global model
        self.global_model = FraudDetectionModel(input_size=input_size)
        self.aggregation_history = []
        
        print(f"✓ Central Server initialized")
        print(f"  Monitoring client models in: {client_models_dir}/")
    
    def load_client_models_from_disk(self, client_data_sizes: List[int]) -> Dict:
        """Load all client models from client_models/ folder"""
        client_models = {}
        
        print(f"\n📂 Loading {self.num_clients} client models from disk...")
        
        for client_id in range(self.num_clients):
            model_path = os.path.join(self.client_models_dir, f'client_{client_id}_model.pth')
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"❌ Client {client_id} model not found at {model_path}")
            
            # Load model
            model = FraudDetectionModel(input_size=self.input_size)
            model.load_state_dict(torch.load(model_path))
            
            # Extract weights
            weights = {}
            for name, param in model.state_dict().items():
                weights[name] = param.cpu().detach().numpy().copy()
            
            client_models[client_id] = weights
            
            # Get file size
            file_size_kb = os.path.getsize(model_path) / 1024
            print(f"  ✓ Client {client_id}: {model_path} ({file_size_kb:.2f} KB)")
        
        return client_models
    
    def aggregate_weights_fedavg(self, client_weights_dict: Dict, client_data_sizes: List[int]) -> Dict:
        """
        FedAvg Aggregation from client models
        Formula: w_global = Σ (n_i / n_total) × w_i
        """
        print(f"\n🔗 FEDERATED AVERAGING AGGREGATION:")
        
        total_data_size = sum(client_data_sizes)
        aggregated_weights = {}
        
        # Get parameter names
        param_names = list(client_weights_dict[0].keys())
        
        # Weighted average
        for param_name in param_names:
            aggregated_weights[param_name] = np.zeros_like(client_weights_dict[0][param_name])
            
            for client_id, client_weights in client_weights_dict.items():
                weight_coefficient = client_data_sizes[client_id] / total_data_size
                aggregated_weights[param_name] += weight_coefficient * client_weights[param_name]
        
        print(f"  Formula: w_global = Σ (n_i / n_total) × w_i")
        print(f"  Total samples: {total_data_size}")
        for client_id in range(len(client_data_sizes)):
            coeff = client_data_sizes[client_id] / total_data_size
            print(f"    Client {client_id}: {coeff:.3f} coefficient ({client_data_sizes[client_id]} samples)")
        
        return aggregated_weights
    
    def update_global_model(self, aggregated_weights: Dict):
        """Update global model with aggregated weights"""
        state_dict = {}
        for name, weight in aggregated_weights.items():
            state_dict[name] = torch.tensor(weight, dtype=torch.float32)
        self.global_model.load_state_dict(state_dict)
    
    def save_global_model(self, filepath: str = 'centralized_model_aggregated.pth'):
        """Save the aggregated global model"""
        torch.save(self.global_model.state_dict(), filepath)
        return filepath


# ============================================================================
# FEDERATED LEARNING ORCHESTRATOR (WITH PERSISTENCE)
# ============================================================================
class FederatedLearningWithPersistence:
    """
    Complete FL workflow with persistent client models:
    1. Train 5 clients independently
    2. SAVE each client model to client_models/ folder
    3. Load models from disk
    4. Aggregate on central server
    5. Save aggregated model
    """
    
    def __init__(self, num_clients: int = 5, num_rounds: int = 3, local_epochs: int = 2):
        self.num_clients = num_clients
        self.num_rounds = num_rounds
        self.local_epochs = local_epochs
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.client_models_dir = 'client_models'
        
        # Create client_models directory
        if os.path.exists(self.client_models_dir):
            print(f"\n🗑️  Clearing existing {self.client_models_dir}/...")
            shutil.rmtree(self.client_models_dir)
        os.makedirs(self.client_models_dir)
        
        self.clients: List[FLClientPersistent] = []
        self.server: CentralFLServer = None
        self.training_results = []
        
        print(f"\n{'='*80}")
        print(f"🚀 FEDERATED LEARNING WITH PERSISTENT CLIENT MODELS")
        print(f"{'='*80}")
        print(f"Configuration:")
        print(f"  - Clients: {num_clients}")
        print(f"  - Rounds: {num_rounds}")
        print(f"  - Local epochs: {local_epochs}")
        print(f"  - Client models directory: {self.client_models_dir}/")
        print(f"  - Device: {self.device}")
    
    def initialize_clients(self, client_datasets: List[Tuple]):
        """Initialize 5 clients with their data"""
        print(f"\n{'─'*80}")
        print(f"📱 INITIALIZING {self.num_clients} CLIENTS")
        print(f"{'─'*80}")
        
        for client_id, (X_train, y_train) in enumerate(client_datasets):
            client = FLClientPersistent(
                client_id, X_train, y_train,
                client_models_dir=self.client_models_dir,
                device=self.device
            )
            self.clients.append(client)
        
        # Initialize server
        input_size = client_datasets[0][0].shape[1]
        self.server = CentralFLServer(
            num_clients=self.num_clients,
            input_size=input_size,
            client_models_dir=self.client_models_dir
        )
        
        print(f"\n✓ All {self.num_clients} clients initialized")
    
    def train_clients_and_save(self, round_num: int) -> Tuple[Dict, List[int]]:
        """
        Train all clients and SAVE their models to disk
        """
        print(f"\n{'─'*80}")
        print(f"🔄 FEDERATED LEARNING ROUND {round_num + 1}/{self.num_rounds}")
        print(f"{'─'*80}")
        
        print(f"\n📍 LOCAL TRAINING PHASE (Each client trains independently):")
        
        client_data_sizes = []
        
        for client in self.clients:
            # Train locally
            loss = client.train_local_epoch(epochs=self.local_epochs)
            
            # SAVE model to disk
            model_path = client.save_model()
            
            # Record metadata
            client_data_sizes.append(client.data_size)
            
            print(f"  ✓ Client {client.client_id}: Trained (loss: {loss:.6f}) → Saved to {model_path}")
        
        return {}, client_data_sizes
    
    def aggregate_from_disk(self, client_data_sizes: List[int]) -> str:
        """
        Load client models from disk and aggregate
        """
        print(f"\n🔗 AGGREGATION PHASE:")
        
        # Load all client models from disk
        client_weights = self.server.load_client_models_from_disk(client_data_sizes)
        
        # Aggregate using FedAvg
        aggregated_weights = self.server.aggregate_weights_fedavg(client_weights, client_data_sizes)
        
        # Update global model
        self.server.update_global_model(aggregated_weights)
        
        print(f"  ✓ Global model updated with FedAvg aggregation")
        
        return "aggregation_complete"
    
    def run_federated_learning(self) -> Dict:
        """Execute complete FL workflow with persistence"""
        
        start_time = datetime.now()
        
        for round_num in range(self.num_rounds):
            # Train clients and save models
            self.train_clients_and_save(round_num)
            
            # Get client data sizes
            client_data_sizes = [client.data_size for client in self.clients]
            
            # Aggregate from disk
            self.aggregate_from_disk(client_data_sizes)
            
            # Show file structure after each round
            self.print_folder_structure(round_num)
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Save final aggregated model
        print(f"\n{'─'*80}")
        print(f"💾 SAVING CENTRAL AGGREGATED MODEL:")
        central_path = self.server.save_global_model('centralized_model_aggregated.pth')
        print(f"  ✓ Saved to: {central_path}")
        
        print(f"\n{'='*80}")
        print(f"✅ FEDERATED LEARNING COMPLETED")
        print(f"{'='*80}")
        print(f"Total time: {total_time:.2f} seconds")
        
        return {
            'status': 'completed',
            'total_rounds': self.num_rounds,
            'client_models_dir': self.client_models_dir,
            'central_model': central_path,
            'total_time': total_time
        }
    
    def print_folder_structure(self, round_num: int):
        """Display the folder structure with all saved models"""
        print(f"\n📂 CLIENT MODELS FOLDER (After Round {round_num + 1}):")
        print(f"   {self.client_models_dir}/")
        
        if os.path.exists(self.client_models_dir):
            files = os.listdir(self.client_models_dir)
            for f in sorted(files):
                filepath = os.path.join(self.client_models_dir, f)
                size_kb = os.path.getsize(filepath) / 1024
                print(f"     ├─ {f} ({size_kb:.2f} KB)")
    
    def print_final_structure(self):
        """Print final file structure after FL"""
        print(f"\n{'='*80}")
        print(f"📊 FINAL FILE STRUCTURE")
        print(f"{'='*80}")
        
        print(f"\n🗂️  CLIENT MODELS FOLDER ({self.num_clients} separate trained models):")
        print(f"   {self.client_models_dir}/")
        
        if os.path.exists(self.client_models_dir):
            files = os.listdir(self.client_models_dir)
            for i, f in enumerate(sorted(files), 1):
                filepath = os.path.join(self.client_models_dir, f)
                size_kb = os.path.getsize(filepath) / 1024
                print(f"     {i}. {f} ({size_kb:.2f} KB)")
        
        print(f"\n🌐 CENTRAL SERVER:")
        if os.path.exists('centralized_model_aggregated.pth'):
            size_kb = os.path.getsize('centralized_model_aggregated.pth') / 1024
            print(f"     └─ centralized_model_aggregated.pth ({size_kb:.2f} KB)")
            print(f"        ↑ AGGREGATED from {self.num_clients} client models")
        
        print(f"\n✨ WORKFLOW:")
        print(f"   1. 5 clients each trained independently")
        print(f"   2. Each saved their model to {self.client_models_dir}/")
        print(f"   3. Central server loaded all 5 models from disk")
        print(f"   4. Aggregated using FedAvg algorithm")
        print(f"   5. Saved result to centralized_model_aggregated.pth")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def load_client_data(num_clients: int = 5):
    """Load and split preprocessed data for clients"""
    try:
        with open('preprocessed_data_balanced.pkl', 'rb') as f:
            data_dict = pickle.load(f)
        
        print("✓ Loaded preprocessed balanced data")
        
        from data_preprocessing_improved import split_data_for_clients
        
        X_train = data_dict.get('X_train_resampled', data_dict.get('X_train'))
        y_train = data_dict.get('y_train_resampled', data_dict.get('y_train'))
        
        client_datasets = split_data_for_clients(X_train, y_train, num_clients=num_clients, stratify=True)
        
        return client_datasets
    
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        raise


if __name__ == "__main__":
    try:
        # Load data
        print("📂 Loading client datasets...")
        client_datasets = load_client_data(num_clients=5)
        
        # Initialize FL with persistence
        fl = FederatedLearningWithPersistence(
            num_clients=5,
            num_rounds=3,
            local_epochs=2
        )
        
        # Initialize clients
        fl.initialize_clients(client_datasets)
        
        # Run federated learning
        results = fl.run_federated_learning()
        
        # Print final structure
        fl.print_final_structure()
        
        # Save summary
        with open('fl_workflow_summary.json', 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✓ Summary saved to fl_workflow_summary.json")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
