#!/usr/bin/env python3
"""
NGROK SERVER FOR FEDERATED LEARNING
Exposes Flask app to internet for external clients to connect
"""

import os
import sys
import time
import threading
import requests
import json
from datetime import datetime
from flask import Flask
import subprocess
import signal
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NgrokServer:
    def __init__(self, flask_app, port=5000):
        self.flask_app = flask_app
        self.port = port
        self.ngrok_process = None
        self.public_url = None
        self.connected_clients = {}
        self.client_heartbeats = {}
        
    def start_ngrok(self):
        """Start ngrok tunnel"""
        try:
            # Kill existing ngrok processes
            subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'], capture_output=True)
            time.sleep(2)
            
            # Start ngrok
            cmd = f'ngrok http {self.port} --log=stdout'
            self.ngrok_process = subprocess.Popen(
                cmd.split(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for ngrok to start and get public URL
            time.sleep(5)
            
            # Get public URL from ngrok API
            try:
                response = requests.get('http://127.0.0.1:4040/api/tunnels')
                if response.status_code == 200:
                    tunnels = response.json()['tunnels']
                    if tunnels:
                        self.public_url = tunnels[0]['public_url']
                        logger.info(f"🌐 Public URL: {self.public_url}")
                        return True
            except Exception as e:
                logger.error(f"Failed to get ngrok URL: {e}")
                
        except Exception as e:
            logger.error(f"Failed to start ngrok: {e}")
            
        return False
    
    def stop_ngrok(self):
        """Stop ngrok tunnel"""
        if self.ngrok_process:
            self.ngrok_process.terminate()
            self.ngrok_process = None
        subprocess.run(['taskkill', '/f', '/im', 'ngrok.exe'], capture_output=True)
    
    def register_client(self, client_id, client_info):
        """Register a new client"""
        self.connected_clients[client_id] = {
            **client_info,
            'registered_at': datetime.now().isoformat(),
            'status': 'active'
        }
        self.client_heartbeats[client_id] = time.time()
        logger.info(f"✅ Client {client_id} registered: {client_info}")
    
    def update_client_heartbeat(self, client_id):
        """Update client heartbeat"""
        if client_id in self.connected_clients:
            self.client_heartbeats[client_id] = time.time()
    
    def get_active_clients(self):
        """Get list of active clients (heartbeat within last 30 seconds)"""
        current_time = time.time()
        active_clients = {}
        
        for client_id, heartbeat_time in self.client_heartbeats.items():
            if current_time - heartbeat_time < 30:  # 30 second timeout
                active_clients[client_id] = self.connected_clients[client_id]
            else:
                # Mark as inactive
                if client_id in self.connected_clients:
                    self.connected_clients[client_id]['status'] = 'inactive'
        
        return active_clients
    
    def start_flask_server(self):
        """Start Flask server in a separate thread"""
        def run_server():
            self.flask_app.run(
                host='127.0.0.1',
                port=self.port,
                debug=False,
                use_reloader=False
            )
        
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()
        time.sleep(2)  # Wait for server to start
        return server_thread

def create_enhanced_flask_app():
    """Create enhanced Flask app with client management"""
    from flask import Flask, request, jsonify, render_template_string
    import uuid
    import json
    from datetime import datetime
    
    app = Flask(__name__, template_folder='templates')
    
    # Store for federated learning state
    app.config['CLIENTS'] = {}
    app.config['MODEL_UPDATES'] = []
    app.config['GLOBAL_MODEL_VERSION'] = 0
    
    @app.route('/')
    def index():
        """Main landing page"""
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Federated Learning Server - Ngrok Enabled</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; margin: 0; background: #f0f2f5; }
                .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
                .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
                .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .stat-card { background: #f8f9ff; padding: 20px; border-radius: 8px; text-align: center; border-left: 4px solid #667eea; }
                .stat-number { font-size: 32px; font-weight: bold; color: #667eea; }
                .stat-label { color: #666; margin-top: 5px; }
                .btn { background: #667eea; color: white; padding: 12px 24px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; margin: 5px; }
                .btn:hover { background: #5a6fd8; }
                .client-list { max-height: 400px; overflow-y: auto; }
                .client-item { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 8px; border-left: 4px solid #4caf50; }
                .status-active { color: #4caf50; font-weight: bold; }
                .status-inactive { color: #f44336; font-weight: bold; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🌐 Federated Learning Server</h1>
                    <p>Privacy-Preserving Fraud Detection with External Clients</p>
                    <p><strong>Public URL:</strong> <span id="public-url">Loading...</span></p>
                </div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="stat-number" id="active-clients">0</div>
                        <div class="stat-label">Active Clients</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="total-updates">0</div>
                        <div class="stat-label">Model Updates</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="model-version">0</div>
                        <div class="stat-label">Model Version</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="uptime">0s</div>
                        <div class="stat-label">Server Uptime</div>
                    </div>
                </div>

                <div class="card">
                    <h2>📡 API Endpoints for External Clients</h2>
                    <div style="background: #f5f5f5; padding: 15px; border-radius: 6px; font-family: monospace; font-size: 12px;">
                        <strong>Register Client:</strong> POST /api/client/register<br>
                        <strong>Get Global Model:</strong> GET /api/client/model<br>
                        <strong>Submit Update:</strong> POST /api/client/update<br>
                        <strong>Heartbeat:</strong> POST /api/client/heartbeat<br>
                        <strong>Server Status:</strong> GET /api/server/status
                    </div>
                </div>

                <div class="card">
                    <h2>👥 Connected Clients</h2>
                    <div id="client-list" class="client-list">
                        <p>Loading clients...</p>
                    </div>
                </div>

                <div class="card">
                    <h2>🚀 Quick Start for Clients</h2>
                    <ol>
                        <li>Register your client: <code>curl -X POST [SERVER_URL]/api/client/register -H "Content-Type: application/json" -d '{"client_name": "MyClient", "data_size": 1000}'</code></li>
                        <li>Get global model: <code>curl [SERVER_URL]/api/client/model?client_id=YOUR_ID</code></li>
                        <li>Train locally on your data</li>
                        <li>Submit updates: <code>curl -X POST [SERVER_URL]/api/client/update -H "Content-Type: application/json" -d '{"client_id": "YOUR_ID", "weights": [...], "metrics": {...}}'</code></li>
                    </ol>
                </div>
            </div>

            <script>
                function updateStats() {
                    fetch('/api/server/status')
                        .then(response => response.json())
                        .then(data => {
                            document.getElementById('active-clients').textContent = data.active_clients;
                            document.getElementById('total-updates').textContent = data.total_updates;
                            document.getElementById('model-version').textContent = data.model_version;
                            document.getElementById('public-url').textContent = data.public_url || 'Local Only';
                        });
                    
                    fetch('/api/server/clients')
                        .then(response => response.json())
                        .then(data => {
                            const clientList = document.getElementById('client-list');
                            if (data.clients.length === 0) {
                                clientList.innerHTML = '<p>No clients connected yet</p>';
                            } else {
                                clientList.innerHTML = data.clients.map(client => `
                                    <div class="client-item">
                                        <strong>${client.client_name}</strong> (ID: ${client.client_id})<br>
                                        <span class="status-${client.status}">${client.status.toUpperCase()}</span><br>
                                        <small>Data Size: ${client.data_size} | Registered: ${new Date(client.registered_at).toLocaleString()}</small>
                                    </div>
                                `).join('');
                            }
                        });
                }

                // Update stats every 5 seconds
                setInterval(updateStats, 5000);
                updateStats(); // Initial load
            </script>
        </body>
        </html>
        """)
    
    @app.route('/api/server/status')
    def server_status():
        """Get server status"""
        return jsonify({
            'status': 'running',
            'public_url': getattr(app, 'ngrok_url', None),
            'active_clients': len([c for c in app.config['CLIENTS'].values() if c.get('status') == 'active']),
            'total_clients': len(app.config['CLIENTS']),
            'total_updates': len(app.config['MODEL_UPDATES']),
            'model_version': app.config['GLOBAL_MODEL_VERSION'],
            'uptime': 'Running'
        })
    
    @app.route('/api/server/clients')
    def server_clients():
        """Get list of connected clients"""
        return jsonify({
            'clients': list(app.config['CLIENTS'].values())
        })
    
    @app.route('/api/client/register', methods=['POST'])
    def register_client():
        """Register a new client"""
        try:
            data = request.get_json()
            client_id = str(uuid.uuid4())
            
            client_info = {
                'client_id': client_id,
                'client_name': data.get('client_name', f'Client_{client_id[:8]}'),
                'data_size': data.get('data_size', 0),
                'location': data.get('location', 'Unknown'),
                'registered_at': datetime.now().isoformat(),
                'status': 'active',
                'last_heartbeat': datetime.now().isoformat(),
                'updates_contributed': 0
            }
            
            app.config['CLIENTS'][client_id] = client_info
            
            logger.info(f"New client registered: {client_info['client_name']} ({client_id})")
            
            return jsonify({
                'status': 'registered',
                'client_id': client_id,
                'message': 'Client registered successfully',
                'server_info': {
                    'model_version': app.config['GLOBAL_MODEL_VERSION'],
                    'next_steps': [
                        'GET /api/client/model?client_id=' + client_id,
                        'Train locally on your data',
                        'POST /api/client/update with your model weights'
                    ]
                }
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/client/heartbeat', methods=['POST'])
    def client_heartbeat():
        """Update client heartbeat"""
        try:
            data = request.get_json()
            client_id = data.get('client_id')
            
            if client_id in app.config['CLIENTS']:
                app.config['CLIENTS'][client_id]['last_heartbeat'] = datetime.now().isoformat()
                app.config['CLIENTS'][client_id]['status'] = 'active'
                return jsonify({'status': 'heartbeat_received'})
            else:
                return jsonify({'error': 'Client not found'}), 404
                
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/client/model')
    def get_global_model():
        """Get current global model for client"""
        try:
            client_id = request.args.get('client_id')
            
            if not client_id:
                return jsonify({'error': 'client_id required'}), 400
            
            if client_id not in app.config['CLIENTS']:
                return jsonify({'error': 'Client not registered'}), 404
            
            # For now, return a mock model structure
            # In production, this would return actual model weights
            model_info = {
                'model_version': app.config['GLOBAL_MODEL_VERSION'],
                'model architecture': 'PredictionModel(input_size=9)',
                'weights_url': f'/api/client/weights?client_id={client_id}',
                'metadata': {
                    'training_rounds': 5,
                    'last_updated': datetime.now().isoformat(),
                    'contributors': len(app.config['MODEL_UPDATES'])
                }
            }
            
            return jsonify(model_info)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    @app.route('/api/client/update', methods=['POST'])
    def submit_client_update():
        """Submit model update from client"""
        try:
            data = request.get_json()
            client_id = data.get('client_id')
            
            if not client_id:
                return jsonify({'error': 'client_id required'}), 400
            
            if client_id not in app.config['CLIENTS']:
                return jsonify({'error': 'Client not registered'}), 404
            
            # Store the update
            update_info = {
                'client_id': client_id,
                'client_name': app.config['CLIENTS'][client_id]['client_name'],
                'weights': data.get('weights', []),
                'metrics': data.get('metrics', {}),
                'timestamp': datetime.now().isoformat(),
                'model_version': app.config['GLOBAL_MODEL_VERSION']
            }
            
            app.config['MODEL_UPDATES'].append(update_info)
            app.config['CLIENTS'][client_id]['updates_contributed'] += 1
            app.config['CLIENTS'][client_id]['last_heartbeat'] = datetime.now().isoformat()
            
            # Update global model version
            app.config['GLOBAL_MODEL_VERSION'] += 1
            
            logger.info(f"Received update from {app.config['CLIENTS'][client_id]['client_name']}")
            
            return jsonify({
                'status': 'update_received',
                'new_model_version': app.config['GLOBAL_MODEL_VERSION'],
                'message': 'Model update received and will be aggregated',
                'total_updates': len(app.config['MODEL_UPDATES'])
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 400
    
    return app

def main():
    """Main function to start the ngrok-enabled server"""
    logger.info("🚀 Starting Federated Learning Server with Ngrok...")
    
    # Import the original Flask app
    try:
        from flask_app_advanced import app as original_app
        logger.info("✓ Loaded original Flask app")
    except ImportError:
        logger.error("❌ Could not import flask_app_advanced")
        return
    
    # Create enhanced app
    enhanced_app = create_enhanced_flask_app()
    
    # Initialize ngrok server
    ngrok_server = NgrokServer(enhanced_app, port=5000)
    
    # Start Flask server
    logger.info("📡 Starting Flask server...")
    flask_thread = ngrok_server.start_flask_server()
    
    # Start ngrok
    logger.info("🌐 Starting ngrok tunnel...")
    if ngrok_server.start_ngrok():
        enhanced_app.ngrok_url = ngrok_server.public_url
        logger.info(f"✅ Server is live at: {ngrok_server.public_url}")
        
        print("\n" + "="*70)
        print("🌐 FEDERATED LEARNING SERVER - NGROK ENABLED")
        print("="*70)
        print(f"🔗 Public URL: {ngrok_server.public_url}")
        print(f"📊 Dashboard: {ngrok_server.public_url}/")
        print(f"📡 API Status: {ngrok_server.public_url}/api/server/status")
        print("\n👥 CLIENT INSTRUCTIONS:")
        print(f"1. Register: curl -X POST {ngrok_server.public_url}/api/client/register \\")
        print('   -H "Content-Type: application/json" \\')
        print('   -d \'{"client_name": "MyClient", "data_size": 1000}\'')
        print(f"\n2. Get Model: curl {ngrok_server.public_url}/api/client/model?client_id=YOUR_ID")
        print(f"\n3. Submit Update: curl -X POST {ngrok_server.public_url}/api/client/update \\")
        print('   -H "Content-Type: application/json" \\')
        print('   -d \'{"client_id": "YOUR_ID", "weights": [...], "metrics": {...}}\'')
        print("\n" + "="*70)
        
        try:
            # Keep the server running
            while True:
                time.sleep(10)
                # Clean up inactive clients
                active_clients = ngrok_server.get_active_clients()
                logger.info(f"Active clients: {len(active_clients)}")
                
        except KeyboardInterrupt:
            logger.info("\n🛑 Shutting down server...")
            ngrok_server.stop_ngrok()
            logger.info("✅ Server stopped")
            
    else:
        logger.error("❌ Failed to start ngrok tunnel")
        logger.info("💡 Make sure ngrok is installed and in your PATH")
        logger.info("💡 Download from: https://ngrok.com/download")

if __name__ == '__main__':
    main()
