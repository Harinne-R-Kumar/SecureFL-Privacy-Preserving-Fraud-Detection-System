import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline as ImbPipeline
import pickle

def load_and_preprocess_data():
    """Load and preprocess data with proper class imbalance handling"""
    df = pd.read_csv('Fraud Detection Dataset.csv')
    
    print("=" * 80)
    print("DATA PREPROCESSING WITH CLASS IMBALANCE HANDLING")
    print("=" * 80)
    
    # Initial statistics
    print("\n📊 ORIGINAL DATA DISTRIBUTION:")
    print(f"Total transactions: {len(df)}")
    print(f"Non-fraudulent: {(df['Fraudulent'] == 0).sum()} ({(df['Fraudulent'] == 0).sum()/len(df)*100:.2f}%)")
    print(f"Fraudulent: {(df['Fraudulent'] == 1).sum()} ({(df['Fraudulent'] == 1).sum()/len(df)*100:.2f}%)")
    print(f"Imbalance ratio: {(df['Fraudulent'] == 0).sum() / (df['Fraudulent'] == 1).sum():.2f}:1")
    
    # Drop identifiers
    df = df.drop(['Transaction_ID', 'User_ID'], axis=1)
    
    # Handle missing values
    numerical_cols = ['Transaction_Amount', 'Time_of_Transaction', 'Previous_Fraudulent_Transactions',
                      'Account_Age', 'Number_of_Transactions_Last_24H']
    categorical_cols = ['Transaction_Type', 'Device_Used', 'Location', 'Payment_Method']
    
    for col in numerical_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mean())
    
    for col in categorical_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].mode()[0])
    
    # Encode categorical variables
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le
    
    # Separate features and target
    X = df.drop('Fraudulent', axis=1)
    y = df['Fraudulent']
    
    # Split into train and test BEFORE any resampling (stratified to preserve ratio)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print("\n✅ TRAIN-TEST SPLIT (STRATIFIED):")
    print(f"Training set: {len(X_train)} ({(y_train == 0).sum()} non-fraud, {(y_train == 1).sum()} fraud)")
    print(f"Test set: {len(X_test)} ({(y_test == 0).sum()} non-fraud, {(y_test == 1).sum()} fraud)")
    
    # Apply class imbalance handling to TRAINING data only
    print("\n🔄 APPLYING CLASS IMBALANCE TECHNIQUES...")
    
    # Strategy: SMOTE to oversample minority, then optionally undersample majority
    # SMOTE brings minority from ~5% to 50% of majority
    smote = SMOTE(random_state=42, k_neighbors=5)
    
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    
    print(f"After SMOTE + Undersampling:")
    print(f"Non-fraudulent: {(y_train_resampled == 0).sum()}")
    print(f"Fraudulent: {(y_train_resampled == 1).sum()}")
    print(f"Imbalance ratio: {(y_train_resampled == 0).sum() / (y_train_resampled == 1).sum():.2f}:1")
    
    # Scale numerical features
    scaler = StandardScaler()
    X_train_resampled = scaler.fit_transform(X_train_resampled)
    X_test_scaled = scaler.transform(X_test)
    X_train_original_scaled = scaler.transform(X_train)
    
    # Convert back to dataframes for client splitting
    X_train_resampled = pd.DataFrame(X_train_resampled, columns=X.columns)
    X_test_scaled = pd.DataFrame(X_test_scaled, columns=X.columns)
    X_train_original_scaled = pd.DataFrame(X_train_original_scaled, columns=X.columns)
    
    return {
        'X_train_resampled': X_train_resampled,
        'y_train_resampled': y_train_resampled,
        'X_train_original': X_train_original_scaled,
        'y_train_original': y_train,
        'X_test': X_test_scaled,
        'y_test': y_test,
        'scaler': scaler,
        'encoders': label_encoders,
        'feature_names': X.columns.tolist()
    }

def split_data_for_clients(X, y, num_clients=5, stratify=False):
    """Split data for federated clients while preserving class distribution"""
    print(f"\n📍 SPLITTING DATA FOR {num_clients} FEDERATED CLIENTS...")
    
    client_data = []
    
    if stratify:
        # Stratified splitting to maintain fraud ratio per client
        indices = np.arange(len(X))
        non_fraud_indices = np.where(y == 0)[0]
        fraud_indices = np.where(y == 1)[0]
        
        np.random.shuffle(non_fraud_indices)
        np.random.shuffle(fraud_indices)
        
        non_fraud_per_client = len(non_fraud_indices) // num_clients
        fraud_per_client = len(fraud_indices) // num_clients
        
        for i in range(num_clients):
            start_nf = i * non_fraud_per_client
            end_nf = (i + 1) * non_fraud_per_client if i < num_clients - 1 else len(non_fraud_indices)
            
            start_f = i * fraud_per_client
            end_f = (i + 1) * fraud_per_client if i < num_clients - 1 else len(fraud_indices)
            
            client_indices = np.concatenate([
                non_fraud_indices[start_nf:end_nf],
                fraud_indices[start_f:end_f]
            ])
            
            X_client = X.iloc[client_indices]
            y_client = y.iloc[client_indices]
            
            print(f"  Client {i+1}: {len(X_client)} samples " +
                  f"({(y_client == 0).sum()} non-fraud, {(y_client == 1).sum()} fraud)")
            
            client_data.append((X_client, y_client))
    else:
        # Random splitting
        indices = np.arange(len(X))
        np.random.shuffle(indices)
        client_size = len(X) // num_clients
        
        for i in range(num_clients):
            start = i * client_size
            end = (i + 1) * client_size if i < num_clients - 1 else len(X)
            client_indices = indices[start:end]
            
            X_client = X.iloc[client_indices]
            y_client = y.iloc[client_indices]
            
            print(f"  Client {i+1}: {len(X_client)} samples " +
                  f"({(y_client == 0).sum()} non-fraud, {(y_client == 1).sum()} fraud)")
            
            client_data.append((X_client, y_client))
    
    return client_data

if __name__ == "__main__":
    # Load and preprocess
    data = load_and_preprocess_data()
    
    # Split for FL clients using stratified approach
    client_data = split_data_for_clients(
        data['X_train_resampled'], 
        data['y_train_resampled'], 
        num_clients=5,
        stratify=True
    )
    
    # Prepare final dataset
    final_data = {
        'X_train_resampled': data['X_train_resampled'],
        'y_train_resampled': data['y_train_resampled'],
        'X_train_original': data['X_train_original'],
        'y_train_original': data['y_train_original'],
        'X_test': data['X_test'],
        'y_test': data['y_test'],
        'client_data': client_data,
        'scaler': data['scaler'],
        'encoders': data['encoders'],
        'feature_names': data['feature_names']
    }
    
    # Save
    with open('preprocessed_data_balanced.pkl', 'wb') as f:
        pickle.dump(final_data, f)
    
    print("\n✅ DATA PREPROCESSING COMPLETE!")
    print("📁 Saved: preprocessed_data_balanced.pkl")
    print("=" * 80)