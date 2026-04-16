#!/usr/bin/env python3
"""
QUICK FIX FOR TENSOR SIZE MISMATCH ERROR
========================================

The issue is in the tensor shapes. Replace these lines in your client code:

BEFORE (causing error):
y_train = np.random.randint(0, 2, (self.data_size, 1)).astype(np.float32)
y_train_tensor = torch.tensor(y_train)

AFTER (fixed):
y_train = np.random.randint(0, 2, (self.data_size, 1)).astype(np.float32)
y_train_tensor = torch.tensor(y_train).squeeze()  # <-- ADD .squeeze()

Also fix this line:
outputs = model(torch.tensor(X_train)).squeeze()  # <-- ADD .squeeze()

Here's the complete fixed train_locally method:
"""

def train_locally(self, global_weights):
    """Train model locally on Colab environment"""
    print("Training locally...")
    
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
    
    print(f"   Training for {self.data_size} samples...")
    
    for epoch in range(5):  # Train for 5 epochs
        optimizer.zero_grad()
        
        # Forward pass - ADD .squeeze() to fix tensor size
        outputs = model(torch.tensor(X_train)).squeeze()  # <-- FIX: Added .squeeze()
        loss = criterion(outputs, torch.tensor(y_train).squeeze())  # <-- FIX: Added .squeeze()
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Calculate accuracy
        model.eval()
        with torch.no_grad():
            outputs = model(torch.tensor(X_train)).squeeze()  # <-- FIX: Added .squeeze()
            predictions = (outputs > 0.5).float()
            accuracy = (predictions == torch.tensor(y_train).squeeze()).float().mean().item()  # <-- FIX: Added .squeeze()
        
        losses.append(loss.item())
        accuracies.append(accuracy)
        
        if epoch % 1 == 0:
            print(f"      Epoch {epoch + 1}/5: Loss = {loss.item():.4f}, Accuracy = {accuracy:.4f}")
        
        model.train()  # Back to training mode
    
    # Final metrics
    final_loss = losses[-1]
    final_accuracy = accuracies[-1]
    
    print(f"Training completed!")
    print(f"   Final Loss: {final_loss:.4f}")
    print(f"   Final Accuracy: {final_accuracy:.4f}")
    
    # Return model weights
    weights = []
    for param in model.parameters():
        weights.extend(param.data.cpu().numpy().flatten())
    
    return weights, final_accuracy, final_loss

"""
QUICK COPY-PASTE SOLUTION:
========================

Just replace your current train_locally method with the one above.
The key fixes are:
1. torch.tensor(y_train).squeeze()  # Removes extra dimension
2. model(torch.tensor(X_train)).squeeze()  # Removes extra dimension

This will fix the tensor size mismatch error!
"""
