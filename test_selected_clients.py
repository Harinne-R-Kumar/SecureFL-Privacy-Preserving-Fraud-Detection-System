#!/usr/bin/env python3
"""
TEST SELECTED CLIENTS FUNCTIONALITY
Quick test to verify enhanced endpoints are working
"""

import requests
import json

def test_selected_clients():
    """Test selected clients functionality"""
    
    base_url = "http://127.0.0.1:5000"
    
    print("🧪 Testing Selected Clients Functionality")
    print("="*50)
    
    # Test 1: Register a client first
    print("\n1️⃣ Registering test client...")
    try:
        response = requests.post(
            f"{base_url}/api/client-management/register",
            json={
                "client_name": "TestBank",
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
    
    # Test 2: Select clients for training
    print("\n2️⃣ Selecting clients for training...")
    try:
        response = requests.post(
            f"{base_url}/api/client-management/select",
            json={
                "method": "weighted",
                "num_clients": 3
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Clients selected: {data['selected_clients']}")
            print(f"📊 Selection method: {data['selection_method']}")
            print(f"👥 Total eligible: {data['total_eligible']}")
        else:
            print(f"❌ Selection failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Selection error: {e}")
        return False
    
    # Test 3: Check management dashboard
    print("\n3️⃣ Checking management dashboard...")
    try:
        response = requests.get(
            f"{base_url}/api/management/dashboard",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard accessible")
            print(f"📊 System status: {data['system_status']}")
            print(f"👥 Total clients: {data['client_management']['total_registered']}")
            print(f"🟢 Active clients: {data['client_management']['active_clients']}")
            print(f"🚫 Blocked clients: {data['security']['blocked_clients']}")
        else:
            print(f"❌ Dashboard failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False
    
    # Test 4: Check queue status
    print("\n4️⃣ Checking aggregation queue...")
    try:
        response = requests.get(
            f"{base_url}/api/aggregation/queue-status",
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Queue status accessible")
            print(f"📊 Queue size: {data['queue_size']}")
            print(f"⏳ Pending updates: {data['pending_updates']}")
            print(f"🔄 Aggregation in progress: {data['aggregation_in_progress']}")
            print(f"📦 Current version: {data['current_version']}")
        else:
            print(f"❌ Queue status failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Queue status error: {e}")
        return False
    
    print("\n✅ All selected clients tests passed!")
    return True

if __name__ == '__main__':
    test_selected_clients()
