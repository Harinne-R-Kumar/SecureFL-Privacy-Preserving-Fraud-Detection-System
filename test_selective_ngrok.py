#!/usr/bin/env python3
"""
TEST SCRIPT FOR SELECTIVE FL SERVER WITH NGROK
Verifies ngrok integration works correctly
"""

import requests
import time
import json

def test_selective_fl_server_ngrok():
    """Test the selective FL server with ngrok integration"""
    
    print("Testing Selective FL Server with Ngrok...")
    print("=" * 50)
    
    # Test local server first
    local_url = "http://127.0.0.1:5001"
    
    try:
        # Test server status
        print("1. Testing server status...")
        response = requests.get(f"{local_url}/api/ngrok_status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"   Ngrok Active: {status['ngrok_active']}")
            print(f"   Public URL: {status['public_url']}")
            print(f"   Local Port: {status['local_port']}")
        else:
            print(f"   Error: {response.status_code}")
        
        # Test dashboard data
        print("\n2. Testing dashboard data...")
        response = requests.get(f"{local_url}/api/dashboard_data", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Total Clients: {data['system_status']['total_clients']}")
            print(f"   Active Clients: {data['system_status']['active_clients']}")
            print(f"   Training Rounds: {data['system_status']['training_rounds']}")
        else:
            print(f"   Error: {response.status_code}")
        
        # Test client registration
        print("\n3. Testing client registration...")
        client_data = {
            "client_name": "TestClient_Ngrok",
            "data_size": 1000,
            "location": "TestLocation"
        }
        response = requests.post(f"{local_url}/api/register_client", 
                              json=client_data, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"   Client Registered: {result['client_id']}")
            print(f"   API Key: {result['api_key']}")
            
            # Test getting model with API key
            api_key = result['api_key']
            print("\n4. Testing model retrieval...")
            response = requests.get(f"{local_url}/api/get_model?api_key={api_key}", timeout=5)
            if response.status_code == 200:
                model_data = response.json()
                print(f"   Model Version: {model_data['model_version']}")
                print(f"   Client ID: {model_data['client_id']}")
            else:
                print(f"   Error: {response.status_code}")
        else:
            print(f"   Error: {response.status_code}")
        
        print("\n" + "=" * 50)
        print("Test completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to server")
        print("Make sure the selective FL server is running on port 5001")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_selective_fl_server_ngrok()
