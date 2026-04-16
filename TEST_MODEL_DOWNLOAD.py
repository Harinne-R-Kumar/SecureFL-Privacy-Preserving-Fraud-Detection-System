#!/usr/bin/env python3
"""
Test script to verify model download fix
"""

import requests
import json

# Server configuration
SERVER_URL = "http://127.0.0.1:5000"
CLIENT_ID = "7720f04e-333f-460f-808d-6a0ff06c5cf0"  # Use the client ID from your error

def test_model_download():
    """Test model download endpoint"""
    try:
        print(f"Testing model download for client: {CLIENT_ID}")
        print(f"Server URL: {SERVER_URL}")
        
        # Make request to get model
        response = requests.get(
            f"{SERVER_URL}/api/client/model",
            params={"client_id": CLIENT_ID},
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Model download successful!")
            print(f"Model version: {data['model_version']}")
            print(f"Model architecture: {data['model_architecture']}")
            print(f"Number of weights: {len(data['weights'])}")
            print(f"First 5 weights: {data['weights'][:5]}")
            print(f"Metadata: {data['metadata']}")
            return True
        else:
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_registration():
    """Test client registration"""
    try:
        print(f"\nTesting client registration...")
        
        response = requests.post(
            f"{SERVER_URL}/api/client/register",
            json={
                "client_name": "Test_Client_Fix",
                "data_size": 1000
            },
            timeout=30
        )
        
        print(f"Registration status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Registration successful!")
            print(f"Client ID: {data['client_id']}")
            return data['client_id']
        else:
            print(f"Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"Registration error: {e}")
        return None

if __name__ == "__main__":
    print("="*60)
    print("TESTING MODEL DOWNLOAD FIX")
    print("="*60)
    
    # Test with existing client ID first
    success = test_model_download()
    
    if not success:
        print("\nTrying with new client registration...")
        new_client_id = test_registration()
        if new_client_id:
            # Test with new client ID
            CLIENT_ID = new_client_id
            success = test_model_download()
    
    if success:
        print("\n" + "="*60)
        print("MODEL DOWNLOAD FIX VERIFIED!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("MODEL DOWNLOAD STILL HAS ISSUES")
        print("="*60)
