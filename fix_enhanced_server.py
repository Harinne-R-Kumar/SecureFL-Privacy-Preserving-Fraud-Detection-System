#!/usr/bin/env python3
"""
FIXED ENHANCED FEDERATED LEARNING SERVER
Quick fixes for the import and initialization issues
"""

import sys
import os
import subprocess
import time
import threading
import requests
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import our new management modules
from client_manager import ClientManager
from aggregation_manager import AggregationManager

def start_ngrok():
    """Start ngrok tunnel and return public URL"""
    try:
        # Kill existing ngrok processes
        subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'], capture_output=True)
        time.sleep(2)
        
        # Start ngrok
        cmd = f'ngrok http 5000 --log=stdout'
        ngrok_process = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for ngrok to start
        time.sleep(5)
        
        # Get public URL
        response = requests.get('http://127.0.0.1:4040/api/tunnels')
        if response.status_code == 200:
            tunnels = response.json()['tunnels']
            if tunnels:
                return tunnels[0]['public_url']
    except:
        pass
    return None

def integrate_with_existing_app(app, client_manager, aggregation_manager):
    """Integrate new management modules with existing Flask app"""
    
    # Store managers in app config
    app.config['CLIENT_MANAGER'] = client_manager
    app.config['AGGREGATION_MANAGER'] = aggregation_manager
    
    # Enhanced endpoints that work with existing system
    from flask import request, jsonify
    import uuid
    
    @app.route('/api/client-management/register', methods=['POST'])
    def enhanced_register_client():
        """Enhanced client registration with scoring"""
        try:
            data = request.get_json()
            client_id = str(uuid.uuid4())
            
            client_info = {
                'client_name': data.get('client_name', f'Client_{client_id[:8]}'),
                'data_size': data.get('data_size', 1000),
                'location': data.get('location', 'Unknown'),
                'api_key': data.get('api_key', '')
            }
            
            # Register with client manager
            success = client_manager.register_client(client_id, client_info)
            if not success:
                return jsonify({
                    'error': 'Registration failed - maximum clients reached'
                }), 400
            
            return jsonify({
                'status': 'registered',
                'client_id': client_id,
                'message': 'Client registered successfully with scoring system',
                'server_info': {
                    'global_model_version': aggregation_manager.current_version,
                    'trust_score': client_manager.client_scores[client_id]['trust_score'],
                    'initial_weight': client_manager.client_scores[client_id]['contribution_score'],
                    'next_steps': [
                        f'GET /api/client/model?client_id={client_id}',
                        'Train locally on your data',
                        f'POST /api/client-management/update (enhanced)',
                        f'GET /api/client-management/status/{client_id} (track your score)'
                    ]
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/client-management/update', methods=['POST'])
    def enhanced_client_update():
        """Enhanced client update with scoring and smart aggregation"""
        try:
            data = request.get_json()
            client_id = data.get('client_id')
            
            if not client_id:
                return jsonify({'error': 'client_id required'}), 400
            
            if not client_manager.is_client_selected(client_id):
                return jsonify({
                    'error': 'Client not selected for training',
                    'message': 'This client is not currently selected for federated learning',
                    'selected_clients': client_manager.get_selected_clients()
                }), 403
            
            # Update client score
            metrics = data.get('metrics', {})
            accuracy = metrics.get('accuracy', 0.0)
            data_size = client_manager.client_scores[client_id]['data_size']
            
            client_manager.update_client_score(client_id, accuracy, data_size)
            client_manager.update_client_activity(client_id)
            
            # Queue for smart aggregation
            client_scores = client_manager.client_scores
            result = aggregation_manager.queue_update(client_id, data.get('weights', []), metrics, client_scores)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/client-management/status/<client_id>', methods=['GET'])
    def get_enhanced_client_status(client_id):
        """Get detailed client status with scores"""
        try:
            status = client_manager.get_client_status(client_id)
            if not status:
                return jsonify({'error': 'Client not found'}), 404
            
            # Add contribution history
            contributions = aggregation_manager.get_client_contributions(client_id)
            status.update(contributions)
            
            return jsonify(status)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/aggregation/queue-status', methods=['GET'])
    def get_aggregation_queue_status():
        """Get aggregation queue status"""
        try:
            return jsonify(aggregation_manager.get_queue_status())
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/management/dashboard', methods=['GET'])
    def get_management_dashboard():
        """Enhanced management dashboard"""
        try:
            client_stats = client_manager.get_statistics()
            aggregation_stats = aggregation_manager.get_queue_status()
            
            return jsonify({
                'system_status': 'ENHANCED_MODE',
                'client_management': client_stats,
                'aggregation_status': aggregation_stats,
                'model_control': {
                    'current_version': aggregation_manager.current_version,
                    'total_versions': len(aggregation_manager.model_versions),
                    'last_aggregation': aggregation_manager.aggregation_logs[-1] if aggregation_manager.aggregation_logs else None
                },
                'security': {
                    'blocked_clients': len(client_manager.blocked_clients),
                    'rejected_updates': len(aggregation_manager.rejected_updates),
                    'deviation_threshold': aggregation_manager.deviation_threshold
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 400

def main():
    """Main function to run enhanced server"""
    try:
        from flask_app_advanced import app
        
        print("\n" + "="*80)
        print("🚀 FIXED ENHANCED FEDERATED LEARNING SERVER")
        print("   Selective Client Control + Smart Aggregation + Version Control")
        print("="*80)
        
        # Initialize managers
        client_manager = ClientManager()
        
        # Load existing model with proper imports
        try:
            import torch
            import torch.nn as nn
            import pickle
            
            # Try to load existing model
            if os.path.exists('centralized_model_balanced.pth'):
                model_data = torch.load('centralized_model_balanced.pth', map_location='cpu')
                if isinstance(model_data, dict):
                    # It's a state dict
                    from flask_app_advanced import PredictionModel
                    model = PredictionModel(input_size=9)
                    model.load_state_dict(model_data)
                else:
                    # It's already a model
                    model = model_data
                
                aggregation_manager = AggregationManager(model)
                print("✅ Loaded existing model for enhanced aggregation")
            else:
                print("⚠️ No existing model found - using default")
                from flask_app_advanced import PredictionModel
                model = PredictionModel(input_size=9)
                aggregation_manager = AggregationManager(model)
                
        except Exception as e:
            print(f"⚠️ Error loading model: {e}")
            from flask_app_advanced import PredictionModel
            model = PredictionModel(input_size=9)
            aggregation_manager = AggregationManager(model)
        
        # Start ngrok
        print("🌐 Starting ngrok tunnel...")
        ngrok_url = start_ngrok()
        
        # Integrate enhanced functionality
        integrate_with_existing_app(app, client_manager, aggregation_manager)
        
        print("\n" + "="*80)
        print("🔥 FIXED ENHANCED SERVER FEATURES ACTIVATED")
        print("="*80)
        print("\n📊 SERVER RUNNING ON:")
        print(f"   Local: http://127.0.0.1:5000")
        if ngrok_url:
            print(f"   Public: {ngrok_url} ** EXTERNAL CLIENTS CAN CONNECT!")
        else:
            print("   Public: ngrok not available - local only")
        print("   Status: LISTENING for client connections\n")
        
        print("🎯 ENHANCED ENDPOINTS:")
        print("   ORIGINAL ENDPOINTS (still work):")
        print("   1. Dashboard: http://127.0.0.1:5000")
        print("   2. Predict: POST /predict")
        print("   3. Stats: GET /api/stats")
        print("   4. Security: GET /security")
        print("   5. Advanced FL: GET /api/advanced-fl/dashboard\n")
        
        print("   🆕 ENHANCED CLIENT MANAGEMENT:")
        print("   6. Enhanced Register: POST /api/client-management/register")
        print("   7. Enhanced Update: POST /api/client-management/update")
        print("   8. Client Status: GET /api/client-management/status/<client_id>")
        print("   9. Queue Status: GET /api/aggregation/queue-status")
        print("   10. Management Dashboard: GET /api/management/dashboard\n")
        
        if ngrok_url:
            print("   🌍 EXTERNAL CLIENTS CAN CONNECT NOW:")
            print(f"   Share this URL: {ngrok_url}")
            print("   Enhanced clients run:")
            print(f"   python enhanced_client.py --server {ngrok_url} --name MyBank --data-size 5000")
        
        print("\n⚙️ ENHANCED CONFIGURATION:")
        print("   - Client Selection: Intelligent weighted selection")
        print("   - Aggregation: Smart queue-based with bad update detection")
        print("   - Version Control: Automatic versioning with rollback")
        print("   - Trust Scoring: Multi-factor client evaluation")
        print("   - Thread Safety: Lock-based concurrent update handling")
        print("   - Bad Update Detection: Deviation-based rejection")
        print("   - Hybrid Mode: Real-time + batch aggregation options")
        
        print("\n🟢 FIXED ENHANCED SERVER STATUS: READY")
        print("-"*80)
        print("To stop: Press Ctrl+C")
        print("="*80 + "\n")
        
        # Start Flask server
        app.run(
            debug=True,
            host='127.0.0.1',
            port=5000,
            use_reloader=False,
            threaded=True
        )

    except KeyboardInterrupt:
        print("\n\n⛔ Enhanced server stopped by user (Ctrl+C)")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
