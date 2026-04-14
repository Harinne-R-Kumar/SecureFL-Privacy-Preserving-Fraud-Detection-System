import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pickle
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, roc_auc_score

class FraudDetectionModel(nn.Module):
    def __init__(self, input_size):
        super(FraudDetectionModel, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.fc2 = nn.Linear(64, 32)
        self.fc3 = nn.Linear(32, 1)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.sigmoid(self.fc3(x))
        return x

def train_centralized_model(X, y, epochs=10, batch_size=32):
    # Convert to tensors
    X_tensor = torch.tensor(X.values, dtype=torch.float32)
    y_tensor = torch.tensor(y.values, dtype=torch.float32).unsqueeze(1)

    dataset = TensorDataset(X_tensor, y_tensor)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    model = FraudDetectionModel(X.shape[1])
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    losses = []
    for epoch in range(epochs):
        epoch_loss = 0
        for X_batch, y_batch in dataloader:
            optimizer.zero_grad()
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        losses.append(epoch_loss / len(dataloader))
        print(f"Epoch {epoch+1}/{epochs}, Loss: {losses[-1]:.4f}")

    return model, losses

def evaluate_model(model, X, y):
    X_tensor = torch.tensor(X.values, dtype=torch.float32)
    with torch.no_grad():
        preds = model(X_tensor).squeeze()
        preds_binary = (preds > 0.5).float()
        accuracy = (preds_binary == torch.tensor(y.values, dtype=torch.float32)).float().mean().item()
        auc = roc_auc_score(y, preds.numpy())
    return accuracy, auc, classification_report(y, preds_binary.numpy())

if __name__ == "__main__":
    with open('preprocessed_data.pkl', 'rb') as f:
        X, y, client_data, scaler, encoders = pickle.load(f)

    # Split into train/test
    from sklearn.model_selection import train_test_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model, losses = train_centralized_model(X_train, y_train, epochs=20)

    # Evaluate
    acc, auc, report = evaluate_model(model, X_test, y_test)
    print(f"Centralized Model - Accuracy: {acc:.4f}, AUC: {auc:.4f}")
    print("Classification Report:\n", report)

    # Save model
    torch.save(model.state_dict(), 'centralized_model.pth')

    # Plot loss
    plt.plot(losses)
    plt.title('Centralized Training Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.savefig('centralized_loss.png')
    plt.show()