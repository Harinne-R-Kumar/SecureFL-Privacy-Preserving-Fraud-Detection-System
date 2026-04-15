# 🌐 DISTRIBUTED FEDERATED LEARNING ARCHITECTURE

## Overview

Your FL system can run in **THREE MODES**:

### Mode 1: All-in-One (Simple)
- Single Python script runs everything
- All 5 clients on same process (sequential)
- Central server + 5 clients in one program

**Script:** `fl_with_persistent_models.py`

### Mode 2: Multi-Process Parallel
- 5 clients run on separate processes (true parallelism)
- Each process has own dataloader, model, optimizer
- Central server coordinates
- On same machine, uses CPU parallelism

**Script:** `distributed_fl_multiprocess.py`

### Mode 3: True Distributed (Different Machines)
- Each client runs on DIFFERENT MACHINE/TERMINAL
- Central server on fixed machine/IP
- Clients download/upload over network
- Share directory via NFS/SMB or cloud storage

**Script:** `run_single_client.py` (run 5 times in different terminals)

---

## Mode 3: True Distributed (Different Terminals)

### How to Run

```bash
# Terminal 1 (SERVER):
python start_fl_server.py

# Terminal 2 (CLIENT 0):
python run_single_client.py 0

# Terminal 3 (CLIENT 1):
python run_single_client.py 1

# Terminal 4 (CLIENT 2):
python run_single_client.py 2

# Terminal 5 (CLIENT 3):
python run_single_client.py 3

# Terminal 6 (CLIENT 4):
python run_single_client.py 4
```

Each terminal runs independently!

---

## File Structure - Distributed Architecture

```
🗂️ CENTRAL SERVER (fl_server/ - shared directory)
   │
   ├─ global_models/
   │  ├─ global_v0.pth          (Initial global model)
   │  ├─ global_v1.pth          (After round 1 aggregation)
   │  ├─ global_v2.pth          (After round 2 aggregation)
   │  └─ global_v3.pth          (After round 3 aggregation)
   │
   ├─ client_current/           (Latest model for each client to download)
   │  ├─ client_0_v0.pth        Client 0 downloads this
   │  ├─ client_1_v0.pth        Client 1 downloads this
   │  ├─ client_2_v0.pth        Client 2 downloads this
   │  ├─ client_3_v0.pth        Client 3 downloads this
   │  ├─ client_4_v0.pth        Client 4 downloads this
   │  ├─ client_0_v1.pth        (Updated after first aggregation)
   │  └─ ... (versions 2, 3, etc)
   │
   └─ client_updates/           (Where clients upload trained models)
      ├─ client_0_v0.pth        Client 0 uploads after training
      ├─ client_1_v0.pth        Client 1 uploads after training
      ├─ client_2_v0.pth        Client 2 uploads after training
      ├─ client_3_v0.pth        Client 3 uploads after training
      ├─ client_4_v0.pth        Client 4 uploads after training
      ├─ client_0_v1.pth        (For round 2)
      └─ ... (all client updates)

💻 CLIENT LOCAL (Each machine has own directory)
   Bank 0/
   ├─ models/                   (Local cache of trained models)
   │  ├─ model_v0.pth
   │  ├─ model_v1.pth
   │  └─ model_v2.pth
   └─ data/                     (Local customer data - STAYS LOCAL)

   Bank 1/
   ├─ models/
   ...

   Bank 2, 3, 4 (similarly)
```

---

## Round-by-Round Process

### ROUND 1 - Initial Training

```
STEP 1: SERVER publishes initial global model
╔══════════════════════════════════════════╗
║  fl_server/client_current/               ║
║    • client_0_v0.pth  ← Global init      ║
║    • client_1_v0.pth  ← Global init      ║
║    • client_2_v0.pth  ← Global init      ║
║    • client_3_v0.pth  ← Global init      ║
║    • client_4_v0.pth  ← Global init      ║
╚══════════════════════════════════════════╝

STEP 2: ALL 5 CLIENTS DOWNLOAD (in parallel)
CLIENT 0 TERMINAL:                CLIENT 1 TERMINAL:
  1️⃣  Check server                 1️⃣  Check server
  2️⃣  Download client_0_v0.pth     2️⃣  Download client_1_v0.pth
  3️⃣  Train locally                 3️⃣  Train locally
  4️⃣  Upload to server              4️⃣  Upload to server
  5️⃣  Wait                          5️⃣  Wait

(CLIENT 2, 3, 4 do same)

STEP 3: CLIENT UPLOADS (independent timing)
╔══════════════════════════════════════════╗
║  fl_server/client_updates/               ║
║    • client_0_v0.pth  ✓ (uploaded)       ║
║    • client_1_v0.pth  ✓ (uploaded)       ║
║    • client_2_v0.pth  ✓ (uploaded)       ║
║    • client_3_v0.pth  ✓ (uploaded)       ║
║    • client_4_v0.pth  ✓ (uploaded)       ║
╚══════════════════════════════════════════╝

STEP 4: SERVER AGGREGATES
Formula: w_global = Σ (0.2 × w_i)  for 5 clients

Result:  global_v1.pth created
         Published to client_current/
         Ready for ROUND 2
```

### ROUND 2 - Model Update

```
CLIENTS ARE STILL RUNNING (still waiting)

SERVER publishes: global_v1.pth to all clients
╔══════════════════════════════════════════╗
║  fl_server/client_current/               ║
║    • client_0_v1.pth  ← UPDATED          ║
║    • client_1_v1.pth  ← UPDATED          ║
║    • client_2_v1.pth  ← UPDATED          ║
║    • client_3_v1.pth  ← UPDATED          ║
║    • client_4_v1.pth  ← UPDATED          ║
╚══════════════════════════════════════════╝

CLIENTS DOWNLOAD NEW VERSION:
  CLIENT 0: "Oh! There's v1"
  CLIENT 1: "Oh! There's v1"
  CLIENT 2: "Oh! There's v1"
  CLIENT 3: "Oh! There's v1"
  CLIENT 4: "Oh! There's v1"

CLIENTS TRAIN WITH NEW MODEL:
  • Start with v1 weights
  • Train for 2 more epochs
  • Loss improves (model better!)
  • Upload v1 updates

SERVER AGGREGATES AGAIN → global_v2.pth

REPEAT for ROUND 3
```

---

## Model Update Mechanism

### Version Tracking

Each model has a **VERSION NUMBER**:

```
v0 = Initial model (random initialization)
v1 = After round 1 aggregation (5 clients trained once)
v2 = After round 2 aggregation (5 clients trained twice)
v3 = After round 3 aggregation (Final model)
```

### Client Download Logic

```python
# Client waits for newest version from server
while True:
    for version in range(1000):  # Check versions
        model_path = f'fl_server/client_current/client_{my_id}_v{version}.pth'
        if os.path.exists(model_path):
            print(f"Found v{version}")
            latest_version = version
        else:
            break
    
    # Download latest version
    download_model(latest_version)
    break
```

### Server Aggregation Logic

```python
# After collecting all client updates v{n}
# Server creates new version: v{n+1}

def aggregate_round(round_num):
    # Collect client_*_v{round_num}.pth
    clients_v_n = load_all_from('client_updates', f'v{round_num}')
    
    # Aggregate
    global_v_n_plus_1 = fedavg_aggregate(clients_v_n)
    
    # Publish
    save(global_v_n_plus_1, f'global_models/global_v{round_num+1}.pth')
    
    # Make available to all clients
    for client_id in range(5):
        copy(global_v_n_plus_1, f'client_current/client_{client_id}_v{round_num+1}.pth')
```

---

## What If Model Needs Update?

### Scenario 1: New Feature
```
Server creates NEW INITIAL MODEL
├─ Reset to v0 (new model)
├─ Publish v0 to all clients
└─ Clients restart training loop
```

### Scenario 2: Retraining
```
After collecting all client_*_v2.pth
├─ Need more rounds? Continue to v3
├─ Need different hyperparams? Adjust locally
├─ Need to restart? Publish new v0
└─ Clients adapt automatically
```

### Scenario 3: New Client Joins
```
NEW BANK JOINS:
├─ Server publishes current global model (v1)
├─ New client trains from v1 (not v0)
├─ Catches up with training
└─ Participates in next round aggregation
```

### Scenario 4: Client Failure Recovery
```
CLIENT 3 CRASHES:
├─ Its model_v1.pth not uploaded
├─ Server waits timeout → continues without it
├─ Aggregates from 4 clients (readjusts weights)
├─ Publishes v2 with 4 clients' contributions
├─ CLIENT 3 recovers → downloads v2
└─ Continues from latest version
```

---

## Fault Tolerance

### What Happens If...

| Scenario | Result |
|----------|--------|
| **Client crashes** | Server continues without it, re-weights remaining clients |
| **Client is slow** | Server waits timeout, continues without late client |
| **Network loses file** | Other copies exist on other clients (resilient) |
| **Server crashes** | Clients have cached models, can retry |
| **Client data changes** | Client retrains on new data, model adapts |

---

## Real-World Deployment

### Option A: Same Network
```
Central Server (Windows/Linux)
├─ Shared Drive: Z:\ (mounted on all machines)
└─ Stores fl_server/

Client Machines (Banks):
├─ Mount Z:\ as network path
└─ Access fl_server/ from different IPs
```

### Option B: Cloud Storage
```
Central Server (AWS/Azure/GCP)
├─ S3/Blob Storage (fl_server/)
└─ HTTP API for uploads/downloads

Client Machines:
├─ Download from cloud
├─ Train locally
└─ Upload back to cloud
```

### Option C: Microservices
```
Central Server (API)
├─ /api/get-model?client_id=0&version=1
├─ /api/put-model (client uploads)
└─ /api/aggregate (trigger aggregation)

Each Client (REST client)
├─ HTTP GET to download
├─ HTTP POST to upload
└─ Async communication
```

---

## Running in Different Terminals

### Step-by-Step

#### Terminal 1 (Server)
```bash
python start_fl_server.py
# Output:
# ✓ Server initialized
# ✓ Waiting for clients...
# 📤 Published global_v0 to all clients
# ⏳ Waiting for client uploads...
# ✓ All clients uploaded
# 🔗 Aggregating...
# ✓ Published global_v1
```

#### Terminal 2 (Client 0)
```bash
python run_single_client.py 0
# Output:
# 💻 CLIENT 0 INITIALIZED
# 🔄 ROUND 1/3
# 📥 Downloading global model v0... ✓
# ✓ Trained locally
# 📤 Uploading model v0... ✓
# 🔄 ROUND 2/3
# 📥 Downloading global model v1... ✓
# ... continues ...
```

#### Terminal 3-6 (Clients 1-4)
```bash
python run_single_client.py 1  # Terminal 3
python run_single_client.py 2  # Terminal 4
python run_single_client.py 3  # Terminal 5
python run_single_client.py 4  # Terminal 6
```

**All terminals run simultaneously!**

---

## Summary

| Aspect | Detail |
|--------|--------|
| **Parallelism** | True: 5 clients train simultaneously |
| **Data Local** | ✓ Raw data never leaves client |
| **Model Sync** | Via version numbers (v0, v1, v2...) |
| **Updates** | Automatic via shared directory |
| **Scalability** | Add any number of clients |
| **Fault Tolerance** | Can handle client failures |
| **Resilience** | Missing clients don't block others |

---

## Your System Is Ready For

✅ **Multi-Terminal Execution**: Run clients on 5 different terminals  
✅ **Model Versioning**: Track all model updates (v0, v1, v2...)  
✅ **Independent Training**: Each client trains on their data  
✅ **Distributed Aggregation**: Central coordination  
✅ **Fault Tolerance**: Missing clients handled gracefully  
✅ **Real-World Deployment**: Can scale to actual banks  

This is **production-ready distributed federated learning!** 🚀
