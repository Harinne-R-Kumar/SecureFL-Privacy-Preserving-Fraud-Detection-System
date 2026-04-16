#!/usr/bin/env python3
"""
TEST SELECTIVE TRAINING FUNCTIONALITY
Tests the new selective training endpoints added to flask_app_advanced.py
"""

import requests
import json
import time

def test_selective_training():
    """Test selective training functionality"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Selective Training Functionality")
    print("="*60)
    
    # Test 1: Check selective training status
    print("\n1️⃣ Checking selective training status...")
    try:
        response = requests.get(f"{base_url}/api/selective_status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Selective status accessible")
            print(f"📊 Total clients: {data['total_clients']}")
            print(f"🔄 Training rounds: {data['training_rounds']}")
            print(f"👥 Selected clients: {data['selected_clients_last_round']}")
            print(f"📦 Global model version: {data['global_model_version']}")
        else:
            print(f"❌ Status check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Status error: {e}")
        return False
    
    # Test 2: Register a test client first
    print("\n2️⃣ Registering test client...")
    try:
        response = requests.post(
            f"{base_url}/api/client/register",
            json={
                "client_name": "TestSelectiveClient",
                "data_size": 5000,
                "location": "Test Location"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            client_id = data['client_id']
            print(f"✅ Client registered: {client_id}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 3: Submit model update for the client
    print("\n3️⃣ Submitting model update...")
    try:
        update_payload = {
            "client_id": client_id,
            "weights": [0.123, -0.456, 0.789] * 100,  # Mock weights
            "metrics": {
                "accuracy": 0.85,
                "f1_score": 0.82,
                "precision": 0.87,
                "recall": 0.80,
                "final_loss": 0.12,
                "training_samples": 5000,
                "epochs": 3
            }
        }
        
        response = requests.post(
            f"{base_url}/api/client/update",
            json=update_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Update submitted: {data['status']}")
            print(f"📦 Global model version: {data['new_global_model_version']}")
        else:
            print(f"❌ Update failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False
    
    # Test 4: Perform selective training
    print("\n4️⃣ Performing selective training...")
    try:
        training_payload = {
            "client_ids": [client_id],
            "aggregation": "weighted",
            "weight_factor": 0.3
        }
        
        response = requests.post(
            f"{base_url}/api/selective_train",
            json=training_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Selective training completed!")
            print(f"🔄 Round: {data['round']}")
            print(f"👥 Selected clients: {data['selected_clients']}")
            print(f"⚖️ Aggregation method: {data['aggregation_method']}")
            print(f"📊 Weight factor: {data['weight_factor']}")
            print(f"📦 Updates processed: {data['num_updates_processed']}")
            print(f"📦 New model version: {data['model_version']}")
        else:
            print(f"❌ Selective training failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Selective training error: {e}")
        return False
    
    # Test 5: Check selective training logs
    print("\n5️⃣ Checking selective training logs...")
    try:
        response = requests.get(f"{base_url}/api/selective_logs", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Logs accessible")
            print(f"📊 Total rounds: {data['total_rounds']}")
            print(f"📦 Current version: {data['current_version']}")
            if data['logs']:
                print(f"📋 Recent logs: {len(data['logs'])} entries")
                for i, log in enumerate(data['logs'][-3:], 1):
                    print(f"  {i}. Round {log['round']}: {log['aggregation_method']}")
        else:
            print(f"❌ Logs check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Logs error: {e}")
        return False
    
    print("\n✅ All selective training tests passed!")
    return True

if __name__ == '__main__':
    test_selective_training()
