# Selective FL Server with Ngrok - Quick Start Guide

## Overview
The Selective Federated Learning Server now includes ngrok tunneling support, allowing external clients to connect from anywhere in the world.

## Features Added
- **Ngrok Tunneling**: Automatic tunnel creation for external access
- **Public URL Generation**: Dynamic public URL for client connections
- **Status Monitoring**: Real-time ngrok tunnel status
- **Graceful Shutdown**: Proper cleanup of ngrok processes

## Prerequisites
1. Install ngrok: https://ngrok.com/download
2. Add ngrok to your system PATH
3. Ensure port 5001 is available

## Quick Start

### 1. Start the Server
```bash
python selective_fl_server.py
```

### 2. Server Output
```
======================================================================
CLOUD SELECTIVE FEDERATED LEARNING SERVER - NGROK ENABLED
======================================================================
Features:
   Cloud-based client management
   Persistent client storage
   Remote model upload
   Selective client participation
   Weighted aggregation control
   Dynamic training rounds
   Real-time monitoring
   API authentication
   Asynchronous updates
   Ngrok tunneling for external access

Starting ngrok tunnel...
Ngrok tunnel established: https://random-string.ngrok.io

======================================================================
SERVER INFORMATION:
======================================================================
Local Server: http://127.0.0.1:5001
Admin Dashboard: http://127.0.0.1:5001
Client Portal: http://127.0.0.1:5001/client-portal

Public URLs (via ngrok):
Main Dashboard: https://random-string.ngrok.io
Client Portal: https://random-string.ngrok.io/client-portal
API Status: https://random-string.ngrok.io/api/ngrok_status

External clients can connect using: https://random-string.ngrok.io
```

### 3. External Client Connection
External clients can now connect using the public ngrok URL:

#### Register a Client
```bash
curl -X POST https://random-string.ngrok.io/api/register_client \
  -H "Content-Type: application/json" \
  -d '{"client_name": "ExternalClient", "data_size": 1000, "location": "Remote"}'
```

#### Get Global Model
```bash
curl https://random-string.ngrok.io/api/get_model?api_key=YOUR_API_KEY
```

#### Submit Model Update
```bash
curl -X POST https://random-string.ngrok.io/api/submit_update \
  -H "Content-Type: application/json" \
  -H "X-API-Key: YOUR_API_KEY" \
  -d '{"weights": [...], "metrics": {"accuracy": 0.95}}'
```

## API Endpoints

### Ngrok-Specific
- `GET /api/ngrok_status` - Get ngrok tunnel status and public URL

### Standard Endpoints (Accessible via ngrok)
- `POST /api/register_client` - Register new client
- `GET /api/get_model` - Get global model (requires API key)
- `POST /api/submit_update` - Submit model update (requires API key)
- `GET /api/client_status` - Get client status
- `GET /api/dashboard_data` - Get real-time dashboard data

## Testing the Implementation

### Run the Test Script
```bash
python test_selective_ngrok.py
```

This script will:
1. Test ngrok status endpoint
2. Test dashboard data retrieval
3. Test client registration
4. Test model retrieval

## Troubleshooting

### Ngrok Fails to Start
1. Ensure ngrok is installed and in PATH
2. Check if port 5001 is available
3. Verify internet connection
4. Try running `ngrok http 5001` manually

### Connection Issues
1. Check firewall settings
2. Verify ngrok tunnel is active: `curl http://127.0.0.1:5001/api/ngrok_status`
3. Restart the server if needed

### API Key Issues
1. Use the API key returned during client registration
2. Include API key in headers: `X-API-Key: YOUR_API_KEY`

## Security Notes
- Ngrok provides a public URL - consider authentication
- API keys are required for sensitive operations
- Monitor connected clients via the dashboard
- Consider using ngrok's reserved domains for production

## Advanced Usage

### Custom Ngrok Configuration
The NgrokManager class can be customized:
```python
# In selective_fl_server.py
ngrok_manager = NgrokManager(port=5001)  # Change port as needed
```

### Monitoring
Access the dashboard at:
- Local: http://127.0.0.1:5001
- Public: https://your-ngrok-url.ngrok.io

The dashboard shows:
- Connected clients
- Training progress
- Model updates
- Aggregation logs

## Integration with Existing Clients
Existing clients can connect by simply updating the server URL from:
- `http://127.0.0.1:5001` 
- To: `https://your-ngrok-url.ngrok.io`

All API endpoints remain the same, just the base URL changes.
