#!/usr/bin/env python3
"""
TEST ENHANCED FEDERATED LEARNING SYSTEM
Tests integration between enhanced server and client modules
"""

import requests
import json
import time
import threading
from datetime import datetime

def test_enhanced_system(server_url="http://127.0.0.1:5000"):
    """Test complete enhanced federated learning system"""
    
    print("🧪 Testing Enhanced Federated Learning System")
    print("="*60)
    
    # Test 1: Enhanced Client Registration
    print("\n1️⃣ Testing Enhanced Client Registration...")
    
    registration_payload = {
        'client_name': 'TestClient_Enhanced',
        'data_size': 1500,
        'location': 'Test Location'
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/client-management/register",
            json=registration_payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            client_id = data['client_id']
            print(f"✅ Enhanced registration successful!")
            print(f"🆔 Client ID: {client_id}")
            print(f"📊 Trust Score: {data['server_info']['trust_score']:.3f}")
            print(f"⚖️ Weight Factor: {data['server_info']['initial_weight']:.3f}")
        else:
            print(f"❌ Registration failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 2: Get Global Model
    print(f"\n2️⃣ Testing Enhanced Model Download...")
    
    try:
        response = requests.get(
            f"{server_url}/api/client/model",
            params={'client_id': client_id},
            timeout=10
        )
        
        if response.status_code == 200:
            model_data = response.json()
            print(f"✅ Model download successful!")
            print(f"📦 Model Version: {model_data['model_version']}")
            print(f"📊 Parameters: {model_data['metadata']['model_parameters']}")
        else:
            print(f"❌ Model download failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Model download error: {e}")
        return False
    
    # Test 3: Enhanced Client Update
    print(f"\n3️⃣ Testing Enhanced Client Update...")
    
    # Mock training metrics
    mock_weights = [0.1234, -0.5678, 0.2345] * 100  # Mock trained weights
    mock_metrics = {
        'accuracy': 0.87,
        'f1_score': 0.82,
        'precision': 0.85,
        'recall': 0.79,
        'final_loss': 0.12,
        'training_samples': 1500,
        'epochs': 3
    }
    
    update_payload = {
        'client_id': client_id,
        'weights': mock_weights,
        'metrics': mock_metrics
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/client-management/update",
            json=update_payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Enhanced update successful!")
            print(f"🔄 Status: {data['status']}")
            print(f"📦 New Global Version: {data['new_global_model_version']}")
            print(f"📊 Total Updates: {data['total_updates']}")
            print(f"🎯 Your Contributions: {data['your_contributions']}")
        else:
            print(f"❌ Update failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update error: {e}")
        return False
    
    # Test 4: Aggregation Queue Status
    print(f"\n4️⃣ Testing Aggregation Queue Status...")
    
    try:
        response = requests.get(
            f"{server_url}/api/aggregation/queue-status",
            timeout=10
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Queue status retrieved!")
            print(f"📊 Queue Size: {status['queue_size']}")
            print(f"⏳ Pending Updates: {status['pending_updates']}")
            print(f"🔄 Aggregation in Progress: {status['aggregation_in_progress']}")
            print(f"📦 Current Version: {status['current_version']}")
        else:
            print(f"❌ Queue status failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Queue status error: {e}")
        return False
    
    # Test 5: Enhanced Client Status
    print(f"\n5️⃣ Testing Enhanced Client Status...")
    
    try:
        response = requests.get(
            f"{server_url}/api/client-management/status/{client_id}",
            timeout=10
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Enhanced status retrieved!")
            print(f"📊 Accuracy: {status.get('accuracy', 0):.4f}")
            print(f"⚖️ Trust Score: {status.get('trust_score', 0):.3f}")
            print(f"🎯 Contribution Score: {status.get('contribution_score', 0):.3f}")
            print(f"📈 Updates Contributed: {status.get('updates_contributed', 0)}")
        else:
            print(f"❌ Status check failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Status check error: {e}")
        return False
    
    # Test 6: Management Dashboard
    print(f"\n6️⃣ Testing Management Dashboard...")
    
    try:
        response = requests.get(
            f"{server_url}/api/management/dashboard",
            timeout=10
        )
        
        if response.status_code == 200:
            dashboard = response.json()
            print(f"✅ Management dashboard retrieved!")
            print(f"📊 System Status: {dashboard['system_status']}")
            print(f"👥 Total Clients: {dashboard['client_management']['total_registered']}")
            print(f"🟢 Active Clients: {dashboard['client_management']['active_clients']}")
            print(f"🚫 Blocked Clients: {dashboard['security']['blocked_clients']}")
            print(f"📦 Current Model Version: {dashboard['model_control']['current_version']}")
        else:
            print(f"❌ Dashboard retrieval failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        return False
    
    # Test 7: Model Versioning
    print(f"\n7️⃣ Testing Model Versioning...")
    
    try:
        response = requests.get(
            f"{server_url}/api/model/versions",
            timeout=10
        )
        
        if response.status_code == 200:
            versions = response.json()
            print(f"✅ Version history retrieved!")
            print(f"📦 Current Version: {versions['current_version']}")
            print(f"📚 Total Versions: {versions['total_versions']}")
            print(f"📋 Recent Versions: {[v['version'] for v in versions['versions'][-3:]]}")
        else:
            print(f"❌ Version history failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Version history error: {e}")
        return False
    
    print(f"\n✅ Enhanced System Test Complete!")
    print(f"🌐 Server: {server_url}")
    print(f"🆔 Test Client ID: {client_id}")
    print("="*60)
    
    return True

def test_concurrent_updates(server_url="http://127.0.0.1:5000", num_clients=3):
    """Test concurrent client updates"""
    
    print(f"\n🔄 Testing {num_clients} Concurrent Updates...")
    print("-"*40)
    
    def simulate_client_update(client_num):
        """Simulate a client update"""
        # Register client
        reg_payload = {
            'client_name': f'ConcurrentClient_{client_num}',
            'data_size': 1000,
            'location': f'Location_{client_num}'
        }
        
        reg_response = requests.post(
            f"{server_url}/api/client-management/register",
            json=reg_payload,
            timeout=10
        )
        
        if reg_response.status_code != 200:
            print(f"❌ Client {client_num} registration failed")
            return None
        
        client_id = reg_response.json()['client_id']
        
        # Get model
        model_response = requests.get(
            f"{server_url}/api/client/model",
            params={'client_id': client_id},
            timeout=10
        )
        
        if model_response.status_code != 200:
            print(f"❌ Client {client_num} model download failed")
            return None
        
        # Submit update
        update_payload = {
            'client_id': client_id,
            'weights': [0.1 + client_num * 0.01] * 100,  # Different weights per client
            'metrics': {
                'accuracy': 0.8 + client_num * 0.02,
                'f1_score': 0.75 + client_num * 0.03,
                'training_samples': 1000
            }
        }
        
        update_response = requests.post(
            f"{server_url}/api/client-management/update",
            json=update_payload,
            timeout=30
        )
        
        if update_response.status_code == 200:
            data = update_response.json()
            print(f"✅ Client {client_num} update submitted: {data['status']}")
        else:
            print(f"❌ Client {client_num} update failed: {update_response.text}")
        
        return client_id
    
    # Start concurrent updates
    threads = []
    for i in range(num_clients):
        thread = threading.Thread(target=simulate_client_update, args=(i+1,))
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # Check final aggregation status
    time.sleep(2)
    
    try:
        response = requests.get(
            f"{server_url}/api/aggregation/queue-status",
            timeout=10
        )
        
        if response.status_code == 200:
            status = response.json()
            print(f"\n📊 Final Aggregation Status:")
            print(f"📦 Current Version: {status['current_version']}")
            print(f"📊 Queue Size: {status['queue_size']}")
            print(f"⏳ Pending Updates: {status['pending_updates']}")
    except:
        pass
    
    print(f"\n✅ Concurrent Update Test Complete!")
    print("="*40)

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test Enhanced Federated Learning System')
    parser.add_argument('--server', default='http://127.0.0.1:5000', help='Server URL')
    parser.add_argument('--concurrent', type=int, default=0, help='Test concurrent updates')
    
    args = parser.parse_args()
    
    print("🧪 Enhanced Federated Learning System Test Suite")
    print(f"🌐 Target Server: {args.server}")
    print("="*60)
    
    # Basic functionality tests
    if test_enhanced_system(args.server):
        print("\n✅ All basic tests passed!")
        
        # Concurrent update test
        if args.concurrent > 0:
            test_concurrent_updates(args.server, args.concurrent)
        
        print(f"\n🎉 Enhanced System Test Complete!")
        print("🚀 Ready for production deployment!")
    else:
        print(f"\n❌ Some tests failed!")
        print("🔧 Check server logs and configuration")

if __name__ == '__main__':
    main()
