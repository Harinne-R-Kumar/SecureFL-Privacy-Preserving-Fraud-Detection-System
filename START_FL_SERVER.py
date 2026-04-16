#!/usr/bin/env python3
"""
FEDERATED LEARNING - REAL-TIME SERVER
======================================

This server enables REAL-TIME federated learning where clients can:
1. Update their models at any time
2. Changes cascade to global model immediately
3. Other clients get new global model next round

Run this FIRST, then run clients in different terminals.
"""

import sys
import os
import subprocess
import time
import threading
import requests

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

try:
    from flask_app_advanced import app
    
    # Start ngrok in background
    print("** Starting ngrok tunnel...")
    ngrok_url = start_ngrok()
    
    print("\n" + "="*80)
    print("** FEDERATED LEARNING REAL-TIME SERVER - NGROK ENABLED")
    print("="*80)
    print("\n** Starting Flask server for real-time federated learning...\n")
    
    print("** SERVER RUNNING ON:")
    print("   Local: http://127.0.0.1:5000")
    if ngrok_url:
        print(f"   Public: {ngrok_url} ** EXTERNAL CLIENTS CAN CONNECT!")
    else:
        print("   Public: ngrok not available - local only")
    print("   Status: LISTENING for client connections\n")
    
    print("** KEY ENDPOINTS (for testing):")
    print("   1. Dashboard: http://127.0.0.1:5000")
    if ngrok_url:
        print(f"   1. Public Dashboard: {ngrok_url}")
    print("   2. Status: http://127.0.0.1:5000/api/advanced-fl/dashboard")
    if ngrok_url:
        print(f"   2. Public Status: {ngrok_url}/api/advanced-fl/dashboard")
    print("   3. Personalized FL: http://127.0.0.1:5000/api/personalized-fl/status\n")
    
    print("   CLIENT PARTICIPATION ENDPOINTS:")
    print("   4. Client Registration: POST /api/client/register")
    print("   5. Get Global Model: GET /api/client/model?client_id=UUID")
    print("   6. Submit Update: POST /api/client/update")
    print("   7. Client Status: GET /api/client/status")
    print("   8. Model Updates: GET /api/client/updates\n")
    
    if ngrok_url:
        print("   EXTERNAL CLIENTS CAN CONNECT NOW:")
        print(f"   Share this URL: {ngrok_url}")
        print("   External users run:")
        print(f"   python fl_client.py --server {ngrok_url} --name MyBank --data-size 5000\n")
    
    print("   LOCAL CLIENT TESTING:")
    print("   Open another terminal and run:")
    print("   → python run_single_client.py 0  (Client 0)")
    print("   → python run_single_client.py 1  (Client 1)")
    print("   → etc...\n")
    
    print("📊 HOW REAL-TIME UPDATES WORK:")
    print("   1. Client 1 trains and uploads model → server receives")
    print("   2. Server aggregates with other clients")
    print("   3. New global model available → all clients download")
    print("   4. Client 1 gets improved model → everyone benefits ✓\n")
    
    print("⚙️  CONFIGURATION:")
    print(f"   - Debug Mode: ON (auto-reload disabled)")
    print(f"   - Port: 5000")
    print(f"   - Host: 127.0.0.1 (localhost)")
    print(f"   - Server Type: WSGI\n")
    
    print("🟢 SERVER STATUS: READY\n")
    print("-"*80)
    print("To stop: Press Ctrl+C\n")
    print("="*80 + "\n")
    
    # ✓ Keep this explicitly in FOREGROUND
    print("ℹ️  Server is now LISTENING for connections...\n")
    sys.stdout.flush()  # Force print immediately
    
    # Start Flask server - this should block and keep running
    app.run(
        debug=True,
        host='127.0.0.1',
        port=5000,
        use_reloader=False,
        threaded=True  # Important: allows concurrent client connections
    )

except KeyboardInterrupt:
    print("\n\n⛔ Server stopped by user (Ctrl+C)")
    sys.exit(0)
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
