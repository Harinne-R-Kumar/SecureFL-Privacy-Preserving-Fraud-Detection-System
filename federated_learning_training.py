"""
ACTUAL FEDERATED LEARNING TRAINING - NOT SIMULATION
- Train 5 models on 5 separate clients (in parallel)
- Each client trains locally on their own data
- Server aggregates weights using FedAvg
- Multiple rounds of FL
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
import pickle
import copy
from typing import List, Dict, Tuple
from datetime import datetime
import json
import os

# ============================================================================
# FRAUD DETECTION MODEL (Same as used in centralized training)
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
# INDIVIDUAL CLIENT TRAINING
# ============================================================================
class FLClient:
    """
    Represents one client (bank) in federated learning.
    Each client trains locally on their own data.
    """
    
    def __init__(self, client_id: int, X_train, y_train, device='cpu'):
        self.client_id = client_id
        self.device = device
        
        # Convert to tensors
        X_tensor = torch.tensor(X_train.values, dtype=torch.float32) if hasattr(X_train, 'values') else torch.tensor(X_train, dtype=torch.float32)
        y_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1) if hasattr(y_train, 'values') else torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
        
        # Create dataloader
        dataset = TensorDataset(X_tensor, y_tensor)
        self.dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
        
        # Initialize model
        self.model = FraudDetectionModel(input_size=X_tensor.shape[1]).to(device)
        
        # Training setup
        self.criterion = nn.BCELoss(weight=None)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        
        # Metrics
        self.training_losses = []
        self.accuracies = []
        self.data_size = len(X_train)
        
        print(f"✓ Client {client_id} initialized with {self.data_size} samples")
    
    def train_local_epoch(self, epochs: int = 1) -> float:
        """
        Train model locally for given number of epochs.
        Returns average loss for this epoch.
        """
        total_loss = 0
        batches = 0
        
        for epoch in range(epochs):
            self.model.train()
            epoch_loss = 0
            
            for X_batch, y_batch in self.dataloader:
                X_batch = X_batch.to(self.device)
                y_batch = y_batch.to(self.device)
                
                # Forward pass
                self.optimizer.zero_grad()
                outputs = self.model(X_batch)
                loss = self.criterion(outputs, y_batch)
                
                # Backward pass
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()
                
                epoch_loss += loss.item()
                batches += 1
            
            avg_epoch_loss = epoch_loss / len(self.dataloader)
            self.training_losses.append(avg_epoch_loss)
            total_loss += avg_epoch_loss
        
        return total_loss / epochs
    
    def get_weights(self) -> Dict[str, np.ndarray]:
        """Extract model weights as numpy arrays"""
        weights = {}
        for name, param in self.model.state_dict().items():
            weights[name] = param.cpu().detach().numpy().copy()
        return weights
    
    def set_weights(self, weights: Dict[str, np.ndarray]):
        """Set model weights from dictionary"""
        state_dict = {}
        for name, weight in weights.items():
            state_dict[name] = torch.tensor(weight, dtype=torch.float32)
        self.model.load_state_dict(state_dict)


# ============================================================================
# SERVER-SIDE AGGREGATION (FedAvg)
# ============================================================================
class FLServer:
    """
    Federated Learning Server.
    Aggregates weights from all clients using FedAvg.
    """
    
    def __init__(self, num_clients: int = 5, input_size: int = 9):
        self.num_clients = num_clients
        self.input_size = input_size
        
        # Global model
        self.global_model = FraudDetectionModel(input_size=input_size)
        
        # Aggregation history
        self.aggregation_history = []
        self.round_results = []
        
        print(f"✓ FL Server initialized for {num_clients} clients")
    
    def aggregate_weights(self, client_weights_list: List[Dict], client_data_sizes: List[int]) -> Dict:
        """
        Federated Averaging (FedAvg) aggregation.
        
        FedAvg formula:
        w_global = Σ (n_i / n_total) * w_i
        
        where:
            w_i = weights from client i
            n_i = data size of client i
            n_total = total data across all clients
        """
        
        total_data_size = sum(client_data_sizes)
        aggregated_weights = {}
        
        # Get parameter names from first client
        param_names = list(client_weights_list[0].keys())
        
        # Weighted average
        for param_name in param_names:
            aggregated_weights[param_name] = np.zeros_like(client_weights_list[0][param_name])
            
            for client_idx, client_weights in enumerate(client_weights_list):
                weight_coefficient = client_data_sizes[client_idx] / total_data_size
                aggregated_weights[param_name] += weight_coefficient * client_weights[param_name]
        
        return aggregated_weights
    
    def update_global_model(self, aggregated_weights: Dict):
        """Update global model with aggregated weights"""
        state_dict = {}
        for name, weight in aggregated_weights.items():
            state_dict[name] = torch.tensor(weight, dtype=torch.float32)
        self.global_model.load_state_dict(state_dict)
    
    def get_global_weights(self) -> Dict[str, np.ndarray]:
        """Get global model weights"""
        weights = {}
        for name, param in self.global_model.state_dict().items():
            weights[name] = param.cpu().detach().numpy().copy()
        return weights


# ============================================================================
# FEDERATED LEARNING ORCHESTRATOR
# ============================================================================
class FederatedLearningOrchestrator:
    """
    Orchestrates federated learning training across all clients.
    Manages the entire FL pipeline:
    1. Client initialization
    2. Round-based training
    3. Server aggregation
    4. Result tracking
    """
    
    def __init__(self, num_clients: int = 5, num_rounds: int = 5, local_epochs: int = 3):
        self.num_clients = num_clients
        self.num_rounds = num_rounds
        self.local_epochs = local_epochs
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        self.clients: List[FLClient] = []
        self.server: FLServer = None
        self.training_history = {
            'global_losses': [],
            'client_accuracies': {},
            'aggregation_times': [],
            'round_details': []
        }
        
        print(f"\n{'='*80}")
        print(f"🚀 FEDERATED LEARNING ORCHESTRATOR INITIALIZED")
        print(f"{'='*80}")
        print(f"Configuration:")
        print(f"  - Number of clients: {num_clients}")
        print(f"  - Number of rounds: {num_rounds}")
        print(f"  - Local epochs per round: {local_epochs}")
        print(f"  - Device: {self.device}")
    
    def initialize_clients(self, client_datasets: List[Tuple]):
        """
        Initialize all clients with their local data.
        
        Args:
            client_datasets: List of (X, y) tuples, one per client
        """
        print(f"\n{'─'*80}")
        print(f"📱 INITIALIZING {self.num_clients} CLIENTS")
        print(f"{'─'*80}")
        
        if len(client_datasets) != self.num_clients:
            raise ValueError(f"Expected {self.num_clients} datasets, got {len(client_datasets)}")
        
        for client_id, (X_train, y_train) in enumerate(client_datasets):
            client = FLClient(client_id, X_train, y_train, device=self.device)
            self.clients.append(client)
            self.training_history['client_accuracies'][f'client_{client_id}'] = []
        
        # Initialize server
        input_size = client_datasets[0][0].shape[1]
        self.server = FLServer(num_clients=self.num_clients, input_size=input_size)
        
        print(f"\n✓ All {self.num_clients} clients initialized")
    
    def train_round(self, round_num: int) -> Dict:
        """
        Execute one federated learning round.
        
        Process:
        1. Send global model to all clients
        2. Each client trains locally
        3. Collect weights from all clients
        4. Aggregate weights on server
        5. Update global model
        """
        
        print(f"\n{'─'*80}")
        print(f"🔄 FEDERATED LEARNING ROUND {round_num + 1}/{self.num_rounds}")
        print(f"{'─'*80}")
        
        # Step 1: Distribute global model to clients
        global_weights = self.server.get_global_weights()
        for client in self.clients:
            client.set_weights(global_weights)
        
        # Step 2: Local training on all clients
        print(f"\n📍 LOCAL TRAINING PHASE:")
        client_weights_list = []
        client_data_sizes = []
        client_losses = []
        
        for client in self.clients:
            print(f"  Client {client.client_id} training locally for {self.local_epochs} epochs...", end=" ")
            loss = client.train_local_epoch(epochs=self.local_epochs)
            client_weights_list.append(client.get_weights())
            client_data_sizes.append(client.data_size)
            client_losses.append(loss)
            print(f"Loss: {loss:.6f}")
        
        # Step 3: Server-side aggregation
        print(f"\n🔗 AGGREGATION PHASE:")
        print(f"  Aggregating weights from {self.num_clients} clients using FedAvg...")
        aggregation_start = datetime.now()
        
        aggregated_weights = self.server.aggregate_weights(client_weights_list, client_data_sizes)
        self.server.update_global_model(aggregated_weights)
        
        aggregation_time = (datetime.now() - aggregation_start).total_seconds()
        
        # Step 4: Record results
        avg_loss = np.mean(client_losses)
        self.training_history['global_losses'].append(avg_loss)
        self.training_history['aggregation_times'].append(aggregation_time)
        
        round_result = {
            'round': round_num + 1,
            'average_client_loss': round(float(avg_loss), 6),
            'individual_client_losses': [round(float(loss), 6) for loss in client_losses],
            'aggregation_time_seconds': round(aggregation_time, 4),
            'total_samples_aggregated': sum(client_data_sizes),
            'clients_participated': self.num_clients
        }
        
        self.training_history['round_details'].append(round_result)
        
        print(f"\n✓ Round {round_num + 1} completed")
        print(f"  Average loss: {avg_loss:.6f}")
        print(f"  Aggregation time: {aggregation_time:.4f}s")
        
        return round_result
    
    def train(self) -> Dict:
        """
        Execute complete federated learning training.
        Runs for num_rounds with each client training locally then aggregating.
        """
        
        print(f"\n{'='*80}")
        print(f"🎯 STARTING FEDERATED LEARNING TRAINING")
        print(f"{'='*80}\n")
        
        training_start = datetime.now()
        
        for round_num in range(self.num_rounds):
            self.train_round(round_num)
        
        training_duration = (datetime.now() - training_start).total_seconds()
        
        # Final results
        print(f"\n{'='*80}")
        print(f"✅ FEDERATED LEARNING TRAINING COMPLETED")
        print(f"{'='*80}")
        print(f"Total training time: {training_duration:.2f} seconds")
        print(f"Average loss: {np.mean(self.training_history['global_losses']):.6f}")
        
        return {
            'status': 'completed',
            'total_rounds': self.num_rounds,
            'total_training_time_seconds': round(training_duration, 2),
            'final_global_model_loss': round(float(self.training_history['global_losses'][-1]), 6),
            'average_global_loss': round(float(np.mean(self.training_history['global_losses'])), 6),
            'training_history': self.training_history,
            'round_details': self.training_history['round_details']
        }
    
    def save_trained_model(self, filepath: str = 'fl_trained_model.pth'):
        """Save the trained global model"""
        if self.server is None:
            print("❌ No server/model to save")
            return
        
        torch.save(self.server.global_model.state_dict(), filepath)
        print(f"✓ Trained model saved to {filepath}")
    
    def get_training_summary(self) -> Dict:
        """Get comprehensive training summary"""
        return {
            'configuration': {
                'num_clients': self.num_clients,
                'num_rounds': self.num_rounds,
                'local_epochs_per_round': self.local_epochs,
                'device': self.device
            },
            'results': {
                'total_clients': self.num_clients,
                'total_rounds_completed': self.num_rounds,
                'global_losses': self.training_history['global_losses'],
                'average_aggregation_time': np.mean(self.training_history['aggregation_times']) if self.training_history['aggregation_times'] else 0,
                'details_per_round': self.training_history['round_details']
            }
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def load_client_data(num_clients: int = 5):
    """
    Load and split preprocessed data for clients.
    """
    try:
        with open('preprocessed_data_balanced.pkl', 'rb') as f:
            data_dict = pickle.load(f)
        
        print("✓ Loaded preprocessed balanced data")
        
        # Split into clients
        from data_preprocessing_improved import split_data_for_clients
        
        X_train = data_dict.get('X_train_resampled', data_dict.get('X_train'))
        y_train = data_dict.get('y_train_resampled', data_dict.get('y_train'))
        
        client_datasets = split_data_for_clients(X_train, y_train, num_clients=num_clients, stratify=True)
        
        return client_datasets
    
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        raise


# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    """
    Example: Run complete federated learning training with 5 clients
    """
    
    # Configuration
    NUM_CLIENTS = 5
    NUM_ROUNDS = 5
    LOCAL_EPOCHS = 3
    
    try:
        # Load data for clients
        print("📂 Loading client datasets...")
        client_datasets = load_client_data(num_clients=NUM_CLIENTS)
        
        # Initialize FL orchestrator
        fl_orchestrator = FederatedLearningOrchestrator(
            num_clients=NUM_CLIENTS,
            num_rounds=NUM_ROUNDS,
            local_epochs=LOCAL_EPOCHS
        )
        
        # Initialize clients
        fl_orchestrator.initialize_clients(client_datasets)
        
        # Run federated learning training
        results = fl_orchestrator.train()
        
        # Save trained model
        fl_orchestrator.save_trained_model('fl_trained_model.pth')
        
        # Print summary
        print("\n" + "="*80)
        print("📊 TRAINING SUMMARY")
        print("="*80)
        summary = fl_orchestrator.get_training_summary()
        print(json.dumps(summary, indent=2, default=str))
        
        # Save results to file
        with open('fl_training_results.json', 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"\n✓ Results saved to fl_training_results.json")
    
    except Exception as e:
        print(f"\n❌ Federated learning training failed: {e}")
        import traceback
        traceback.print_exc()
