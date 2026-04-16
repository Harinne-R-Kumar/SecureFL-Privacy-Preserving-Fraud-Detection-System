#!/usr/bin/env python3
"""
CONNECTION TEST FOR LOCAL SERVER
=============================

Test if server is properly responding on localhost:5000
"""

import requests
import time

def test_server_connection():
    """Test server connection with different endpoints"""
    server_url = "http://127.0.0.1:5000"
    
    print("Testing server connection...")
    print(f"Server URL: {server_url}")
    
    # Test 1: Basic connection
    try:
        print("\n1. Testing basic connection...")
        response = requests.get(f"{server_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ Server is responding")
        else:
            print(f"   ✗ Server returned: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        return False
    
    # Test 2: API endpoint
    try:
        print("\n2. Testing API endpoint...")
        response = requests.get(f"{server_url}/api/stats", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✓ API endpoint is working")
        else:
            print(f"   ✗ API returned: {response.status_code}")
    except Exception as e:
        print(f"   ✗ API connection failed: {e}")
        return False
    
    # Test 3: Client registration endpoint
    try:
        print("\n3. Testing client registration endpoint...")
        response = requests.post(f"{server_url}/api/client/register", 
                            json={"client_name": "TestClient", "data_size": 1000}, 
                            timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✓ Registration endpoint working")
            print(f"   Client ID: {data['client_id']}")
        else:
            print(f"   ✗ Registration failed: {response.text}")
    except Exception as e:
        print(f"   ✗ Registration connection failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("="*50)
    print("SERVER CONNECTION TEST")
    print("="*50)
    
    success = test_server_connection()
    
    if success:
        print("\n" + "="*50)
        print("✓ ALL TESTS PASSED - Server is working correctly!")
        print("You can now run your federated learning client.")
    else:
        print("\n" + "="*50)
        print("✗ CONNECTION TESTS FAILED")
        print("Possible issues:")
        print("1. Server crashed - restart with: python START_FL_SERVER.py")
        print("2. Firewall blocking connection")
        print("3. Port 5000 in use by another application")
        print("4. Server not properly started")
        
    print("\n" + "="*50)
