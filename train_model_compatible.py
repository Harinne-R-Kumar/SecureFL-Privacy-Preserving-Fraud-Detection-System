"""
Train and save a model with the correct PredictionModel architecture
This ensures compatible weights for Flask app loading
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pickle
import numpy as np
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score, f1_score
import pandas as pd

class PredictionModel(nn.Module):
    """Model that matches Flask app's PredictionModel"""
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

def train_model():
    """Train model compatible with Flask app"""
    
    print("="*80)
    print("🔄 TRAINING MODEL WITH CORRECT ARCHITECTURE")
    print("="*80)
    
    # Load preprocessed data
    print("\n📂 Loading preprocessed balanced data...")
    try:
        with open('preprocessed_data_balanced.pkl', 'rb') as f:
            data_dict = pickle.load(f)
        
        X_train = data_dict['X_train_resampled']
        y_train = data_dict['y_train_resampled']
        X_test = data_dict['X_test']
        y_test = data_dict['y_test']
        
        print(f"✓ Loaded training data: {X_train.shape}")
        print(f"✓ Loaded test data: {X_test.shape}")
    
    except FileNotFoundError:
        print("❌ preprocessed_data_balanced.pkl not found")
        print("   Please run data_preprocessing_improved.py first")
        return
    
    # Convert to tensors
    print("\n🔧 Preparing tensors...")
    X_train_tensor = torch.tensor(X_train.values, dtype=torch.float32)
    y_train_tensor = torch.tensor(y_train.values, dtype=torch.float32).unsqueeze(1)
    X_test_tensor = torch.tensor(X_test.values, dtype=torch.float32)
    y_test_tensor = torch.tensor(y_test.values, dtype=torch.float32).unsqueeze(1)
    
    # Create dataloaders
    train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    test_dataset = TensorDataset(X_test_tensor, y_test_tensor)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)
    
    # Initialize model
    print("\n🧠 Initializing PredictionModel...")
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model = PredictionModel(input_size=X_train.shape[1]).to(device)
    print(f"✓ Model initialized on device: {device}")
    
    # Print model architecture
    print("\n📋 Model Architecture:")
    print(model)
    
    # Training setup
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    num_epochs = 20
    
    train_losses = []
    val_accuracies = []
    
    # Training loop
    print(f"\n🚀 TRAINING FOR {num_epochs} EPOCHS")
    print("="*80)
    
    for epoch in range(num_epochs):
        # Training phase
        model.train()
        train_loss = 0
        
        for X_batch, y_batch in train_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            # Forward pass
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            
            # Backward pass
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            
            train_loss += loss.item()
        
        avg_train_loss = train_loss / len(train_loader)
        train_losses.append(avg_train_loss)
        
        # Validation phase
        model.eval()
        with torch.no_grad():
            test_preds = []
            test_targets = []
            
            for X_batch, y_batch in test_loader:
                X_batch = X_batch.to(device)
                outputs = model(X_batch).cpu().sigmoid()
                test_preds.extend(outputs.numpy().flatten())
                test_targets.extend(y_batch.numpy().flatten())
            
            test_preds = np.array(test_preds)
            test_targets = np.array(test_targets)
            
            test_accuracy = accuracy_score(test_targets, (test_preds > 0.5).astype(int))
            val_accuracies.append(test_accuracy)
        
        if (epoch + 1) % 5 == 0 or epoch == 0:
            print(f"Epoch {epoch+1:2d}/{num_epochs} | Train Loss: {avg_train_loss:.6f} | Test Accuracy: {test_accuracy:.4f}")
    
    # Final evaluation
    print("\n" + "="*80)
    print("✅ TRAINING COMPLETED")
    print("="*80)
    
    model.eval()
    with torch.no_grad():
        test_preds = []
        test_targets = []
        
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            outputs = model(X_batch).cpu().sigmoid()
            test_preds.extend(outputs.numpy().flatten())
            test_targets.extend(y_batch.numpy().flatten())
        
        test_preds = np.array(test_preds)
        test_targets = np.array(test_targets)
        
        # Calculate metrics
        test_accuracy = accuracy_score(test_targets, (test_preds > 0.5).astype(int))
        test_auc = roc_auc_score(test_targets, test_preds)
        test_f1 = f1_score(test_targets, (test_preds > 0.5).astype(int))
        
        print("\n📊 FINAL METRICS:")
        print(f"  Accuracy: {test_accuracy:.4f}")
        print(f"  AUC-ROC:  {test_auc:.4f}")
        print(f"  F1-Score: {test_f1:.4f}")
        
        # Classification report
        print("\n📋 Classification Report:")
        print(classification_report(test_targets, (test_preds > 0.5).astype(int), 
                                    target_names=['Non-Fraud', 'Fraud']))
    
    # Save model
    print("\n💾 Saving model...")
    torch.save(model.state_dict(), 'centralized_model_balanced.pth')
    print("✓ Model saved to centralized_model_balanced.pth")
    
    # Verify model can be loaded
    print("\n🔍 Verifying model can be loaded...")
    test_model = PredictionModel(input_size=X_train.shape[1])
    test_model.load_state_dict(torch.load('centralized_model_balanced.pth'))
    print("✓ Model loaded successfully - architecture matches!")
    
    return model

if __name__ == "__main__":
    train_model()
