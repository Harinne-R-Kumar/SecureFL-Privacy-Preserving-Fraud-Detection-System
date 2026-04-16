# 🚀 Quick Start Guide - Ngrok Federated Learning

## ⚡ 5-Minute Setup

### 1. Install ngrok (One-time setup)
```bash
# Download from: https://ngrok.com/download
# For Windows: Download ngrok.exe and add to PATH
# Or use chocolatey: choco install ngrok
```

### 2. Install Python dependencies
```bash
python setup_ngrok_fl.py
```

### 3. Start the server
```bash
python ngrok_server.py
```

### 4. Connect clients (in separate terminals)
```bash
# Client 1
python fl_client.py --server https://YOUR_NGROK_URL.ngrok.io --name BankA --data-size 5000

# Client 2  
python fl_client.py --server https://YOUR_NGROK_URL.ngrok.io --name BankB --data-size 3000
```

### 5. Monitor at your ngrok URL
Open the ngrok URL in your browser to see the live dashboard!

## 🎯 What You Get

✅ **Global Access**: Your Flask app accessible from anywhere  
✅ **Multi-Client Support**: Multiple users can connect simultaneously  
✅ **Real-time Dashboard**: Live monitoring of federated learning  
✅ **Privacy-Preserving**: No raw data shared, only model updates  
✅ **Easy Setup**: Automated scripts and clear documentation  

## 📊 Server Dashboard Features

- **Live Statistics**: Active clients, model version, total updates
- **Client Management**: View all connected clients and their status
- **API Documentation**: Built-in guide for client integration
- **Real-time Updates**: Auto-refreshing interface every 5 seconds

## 🤖 Client Features

- **Automatic Registration**: Self-registration with unique IDs
- **Local Training**: Train on private data without sharing
- **Continuous Operation**: Automated training cycles every 60 seconds
- **Heartbeat System**: Maintain connection with server

## 🔧 Troubleshooting

### ngrok Issues
```bash
# Test ngrok installation
ngrok version

# Check ngrok status
curl http://127.0.0.1:4040/api/tunnels
```

### Connection Issues
```bash
# Test local server
curl http://localhost:5000/api/server/status

# Test ngrok tunnel
curl https://YOUR_NGROK_URL.ngrok.io/api/server/status
```

## 📈 Success Indicators

✅ Server starts and shows ngrok URL  
✅ Dashboard accessible at ngrok URL  
✅ Clients can register successfully  
✅ Model updates are submitted and logged  
✅ Real-time statistics update automatically  

## 🎉 You're Ready!

Your federated learning system is now:
- **Globally accessible** via ngrok
- **Multi-client ready** for collaborative training
- **Privacy-preserving** with secure model aggregation
- **Real-time monitored** with live dashboard
- **Production-ready** with comprehensive error handling

Start your federated learning network today! 🌍
