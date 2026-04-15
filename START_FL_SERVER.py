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

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from flask_app_advanced import app
    print("\n" + "="*80)
    print("✅ FEDERATED LEARNING REAL-TIME SERVER")
    print("="*80)
    print("\n🚀 Starting Flask server for real-time federated learning...\n")
    
    print("📌 SERVER RUNNING ON:")
    print("   → Address: http://127.0.0.1:5000")
    print("   → Status: LISTENING for client connections\n")
    
    print("🌐 KEY ENDPOINTS (for testing):")
    print("   1. Dashboard: http://127.0.0.1:5000")
    print("   2. Status: http://127.0.0.1:5000/api/advanced-fl/dashboard")
    print("   3. Personalized FL: http://127.0.0.1:5000/api/personalized-fl/status\n")
    
    print("💻 TO TEST CLIENT MODEL UPDATES IN REAL-TIME:")
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
