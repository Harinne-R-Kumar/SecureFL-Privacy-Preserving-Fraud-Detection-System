# 🌐 Federated Learning with Ngrok - External Client System

Transform your local Flask fraud detection system into a globally accessible federated learning platform where external users can connect as clients and contribute to model training.

## 🚀 Quick Start

### 1. Setup the System
```bash
# Run the setup script
python setup_ngrok_fl.py

# Or manually install requirements
pip install -r requirements_ngrok.txt
```

### 2. Start the Server
```bash
# Option 1: Use the convenience script
start_fl_server.bat

# Option 2: Run directly
python ngrok_server.py
```

### 3. Connect Clients
```bash
# Option 1: Use the convenience script
connect_client.bat https://your-ngrok-url.ngrok.io MyBank 5000

# Option 2: Run directly
python fl_client.py --server https://your-ngrok-url.ngrok.io --name MyBank --data-size 5000
```

## 📋 Prerequisites

### Required Software
- **Python 3.7+** - Core runtime environment
- **ngrok** - Tunnel service for exposing local server to internet
  - Download from: https://ngrok.com/download
  - Add to system PATH

### Required Files
- `flask_app_advanced.py` - Main Flask application
- `federated_learning_training.py` - FL training logic
- `centralized_model_balanced.pth` - Pre-trained model
- `preprocessed_data_balanced.pkl` - Training data

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client A      │    │   Client B      │    │   Client C      │
│  (Bank A)       │    │  (Bank B)       │    │  (Bank C)       │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          └──────────────────────┼──────────────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │     Ngrok Tunnel         │
                    │   (https://xxx.ngrok.io) │
                    └─────────────┬─────────────┘
                                 │
                    ┌─────────────┴─────────────┐
                    │   Flask Server (Local)    │
                    │  - Client Management      │
                    │  - Model Aggregation      │
                    │  - Real-time Dashboard    │
                    └───────────────────────────┘
```

## 📡 Server Features

### Core Functionality
- **Client Registration**: Automatic client onboarding
- **Model Distribution**: Serve global model to clients
- **Update Aggregation**: Collect and aggregate client updates
- **Real-time Monitoring**: Live dashboard of system status
- **Heartbeat Management**: Track client connectivity

### API Endpoints
```
POST /api/client/register     # Register new client
GET  /api/client/model        # Get global model
POST /api/client/update       # Submit model update
POST /api/client/heartbeat    # Send heartbeat
GET  /api/server/status       # Server status
GET  /api/server/clients     # Connected clients
```

### Dashboard Features
- **Live Statistics**: Active clients, model version, updates
- **Client Management**: View connected clients and their status
- **API Documentation**: Built-in endpoint guide
- **Real-time Updates**: Auto-refreshing interface

## 👥 Client Features

### Client Capabilities
- **Automatic Registration**: Self-registration with server
- **Local Training**: Train on local data without sharing
- **Model Updates**: Submit trained model weights
- **Continuous Operation**: Automated training cycles
- **Heartbeat System**: Maintain connection status

### Client Workflow
1. **Register** with server using unique client ID
2. **Download** global model weights
3. **Train** locally on private data
4. **Submit** model updates to server
5. **Repeat** training cycle continuously

## 🔧 Configuration Options

### Server Configuration
```python
# In ngrok_server.py
ngrok_server = NgrokServer(
    flask_app=app,
    port=5000,              # Local port
    heartbeat_interval=30,   # Client timeout (seconds)
    training_interval=60     # Training cycle (seconds)
)
```

### Client Configuration
```bash
# Command line options
python fl_client.py \
    --server https://abc123.ngrok.io \  # Server URL
    --name MyBank \                     # Client name
    --data-size 5000 \                  # Training data size
    --single                            # Single training cycle (optional)
```

## 📊 Monitoring & Analytics

### Server Dashboard
- **Active Clients**: Real-time client count
- **Model Version**: Current global model version
- **Total Updates**: Number of client updates received
- **System Uptime**: Server running time
- **Client List**: Detailed client information

### Client Metrics
- **Training Accuracy**: Model performance on local data
- **F1 Score**: Fraud detection quality
- **Loss Values**: Training convergence
- **Update Frequency**: Contribution timeline

## 🔒 Security & Privacy

### Privacy Guarantees
- **Data Localization**: Raw data never leaves client
- **Weight-only Sharing**: Only model weights transmitted
- **Differential Privacy**: Optional noise injection
- **Secure Aggregation**: Protected model updates

### Security Features
- **Client Authentication**: Unique client IDs
- **Connection Validation**: Verified client connections
- **Timeout Management**: Automatic client disconnection
- **Request Validation**: Input sanitization

## 🚀 Advanced Usage

### Multiple Client Setup
```bash
# Terminal 1: Start server
python ngrok_server.py

# Terminal 2: Client A
python fl_client.py --server https://xxx.ngrok.io --name BankA --data-size 5000

# Terminal 3: Client B  
python fl_client.py --server https://xxx.ngrok.io --name BankB --data-size 3000

# Terminal 4: Client C
python fl_client.py --server https://xxx.ngrok.io --name BankC --data-size 8000
```

### Custom Data Integration
To use real data instead of mock data, modify the `generate_mock_data()` method in `fl_client.py`:

```python
def load_real_data(self, filepath):
    """Load your real transaction data"""
    # Your data loading logic here
    # Return: features (torch.Tensor), labels (torch.Tensor)
    pass
```

### Model Customization
Modify the `FraudDetectionModel` class in `fl_client.py` for custom architectures:

```python
class CustomFraudModel(nn.Module):
    def __init__(self, input_size=9):
        super().__init__()
        # Your custom model architecture
        self.layers = nn.Sequential(
            # ... your layers
        )
```

## 🛠️ Troubleshooting

### Common Issues

#### ngrok Not Found
```bash
# Download ngrok
# Windows: Download exe and add to PATH
# Mac: brew install ngrok
# Linux: snap install ngrok
```

#### Connection Refused
```bash
# Check if server is running
curl http://localhost:5000/api/server/status

# Check ngrok tunnels
curl http://127.0.0.1:4040/api/tunnels
```

#### Client Registration Fails
- Verify server URL is correct
- Check internet connection
- Ensure ngrok tunnel is active
- Verify server is accessible

#### Model Update Fails
- Check client authentication
- Verify model weight format
- Check server logs for errors
- Ensure client is still connected

### Debug Mode
Enable debug logging:
```python
# In ngrok_server.py
logging.basicConfig(level=logging.DEBUG)

# In fl_client.py  
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Optimization

### Server Optimization
- Use Redis for client state management (large scale)
- Implement rate limiting for API endpoints
- Add database persistence for model updates
- Use WebSocket for real-time updates

### Client Optimization
- Batch multiple training samples
- Implement incremental learning
- Use GPU acceleration if available
- Optimize data preprocessing

## 🔄 Continuous Deployment

### Production Setup
1. **Server Hosting**: Deploy on cloud platform (AWS, GCP, Azure)
2. **Domain Setup**: Use custom domain instead of ngrok
3. **SSL Certificate**: Implement HTTPS encryption
4. **Load Balancing**: Handle multiple concurrent clients
5. **Monitoring**: Add comprehensive logging and metrics

### Scaling Considerations
- **Horizontal Scaling**: Multiple server instances
- **Database**: Persistent storage for models and metadata
- **Message Queue**: Asynchronous client communication
- **Caching**: Redis for frequently accessed data

## 📚 API Reference

### Server APIs

#### Register Client
```bash
POST /api/client/register
Content-Type: application/json

{
    "client_name": "MyBank",
    "data_size": 5000,
    "location": "US-East"
}
```

#### Get Global Model
```bash
GET /api/client/model?client_id=UUID
```

#### Submit Update
```bash
POST /api/client/update
Content-Type: application/json

{
    "client_id": "UUID",
    "weights": [0.1, 0.2, ...],
    "metrics": {
        "accuracy": 0.95,
        "f1_score": 0.87,
        "loss": 0.12
    }
}
```

### Client APIs
The client script handles all API interactions automatically. Manual API calls are optional for testing.

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install development dependencies
3. Run tests with `python -m pytest`
4. Submit pull requests

### Feature Requests
- Custom model architectures
- Advanced aggregation algorithms
- Enhanced security features
- Performance monitoring tools

## 📄 License

This project extends the existing federated learning system with ngrok integration for external client access.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review server and client logs
3. Verify network connectivity
4. Test with minimal setup first

---

**🎉 Ready to start your federated learning network?**

1. Run `python setup_ngrok_fl.py`
2. Start server with `python ngrok_server.py`
3. Connect clients with `python fl_client.py`
4. Monitor at your ngrok URL!

Your fraud detection model is now globally accessible and ready for collaborative training! 🌍
