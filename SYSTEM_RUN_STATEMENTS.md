# SYSTEM RUN STATEMENTS - COMPLETE COMMANDS

## 🚀 QUICK START (Copy-Paste Ready)

---

## MODE 1: ALL-IN-ONE (Simplest)
**Run everything in a single script - perfect for demo**

```powershell
python fl_with_persistent_models.py
```

**What happens:**
- ✅ 5 clients train sequentially
- ✅ Models saved to `client_models/` folder
- ✅ Central aggregated model created
- ✅ Takes ~30 seconds
- ✅ View results in `client_models/` folder

**For Linux/Mac:**
```bash
python fl_with_persistent_models.py
```

---

## MODE 2: PARALLEL (Multi-Process)
**5 clients train simultaneously on same machine**

```powershell
python distributed_fl_multiprocess.py
```

**What happens:**
- ✅ 5 processes run in parallel
- ✅ Faster than MODE 1
- ✅ Uses `fl_server/` directory for coordination
- ✅ Shows realistic parallelism
- ✅ Takes ~20 seconds

**For Linux/Mac:**
```bash
python distributed_fl_multiprocess.py
```

---

## MODE 3: DISTRIBUTED (Real-Time - Multiple Terminals)
**Each client runs independently - most realistic**

### Step 1: Start Server (Terminal 1)
```powershell
python START_FL_SERVER.py
```

**Expected output:**
```
✅ FEDERATED LEARNING REAL-TIME SERVER
🚀 Starting Flask server...
📌 SERVER RUNNING ON: http://127.0.0.1:5000
🟢 SERVER STATUS: READY
ℹ️ Server is now LISTENING for connections...
* Running on http://127.0.0.1:5000
```

### Step 2: Start 5 Clients (Terminals 2-6)

**Terminal 2 - Client 0:**
```powershell
python run_single_client.py 0
```

**Terminal 3 - Client 1:**
```powershell
python run_single_client.py 1
```

**Terminal 4 - Client 2:**
```powershell
python run_single_client.py 2
```

**Terminal 5 - Client 3:**
```powershell
python run_single_client.py 3
```

**Terminal 6 - Client 4:**
```powershell
python run_single_client.py 4
```

**Watch clients train in real-time!**

---

## MONITORING & TESTING

### While System is Running

**Check Dashboard (Any Terminal):**
```powershell
curl http://127.0.0.1:5000/api/advanced-fl/dashboard
```

**Check All Clients Status:**
```powershell
curl http://127.0.0.1:5000/api/personalized-fl/all-clients
```

**Check Specific Client (e.g., Client 0):**
```powershell
curl http://127.0.0.1:5000/api/personalized-fl/client/0
```

**Watch Real-Time Updates (Every 2 seconds):**
```powershell
while ($true) {
  Write-Host "=== $(Get-Date) ==="
  curl http://127.0.0.1:5000/api/personalized-fl/all-clients | python -m json.tool
  Start-Sleep -Seconds 2
}
```

**Browser Access:**
```
http://127.0.0.1:5000/
```

---

## ADDITIONAL TESTING COMMANDS

### Test FedProx (Non-IID Handling)
```powershell
curl -X POST http://127.0.0.1:5000/api/fedprox/simulate `
  -H "Content-Type: application/json" `
  -d '{"rounds": 5, "mu": 0.01}'
```

### Test FedOpt (Adaptive Optimization)
```powershell
curl http://127.0.0.1:5000/api/fedopt/compare
```

### Test Personalized FL (Adapt Model)
```powershell
curl -X POST http://127.0.0.1:5000/api/personalized-fl/adapt `
  -H "Content-Type: application/json" `
  -d @"
{
  "client_id": 1,
  "accuracy": 0.93,
  "f1_score": 0.87,
  "data_size": 7758
}
"@
```

### Get FL Architecture Info
```powershell
curl http://127.0.0.1:5000/api/fl/architecture
```

### Get FedAvg Explanation
```powershell
curl http://127.0.0.1:5000/api/fl/fedavg-explanation
```

---

## COMPARISON TABLE

| Mode | Command | Terminals | Time | Best For |
|------|---------|-----------|------|----------|
| **1: All-In-One** | `python fl_with_persistent_models.py` | 1 | ~30s | Demo/Learning |
| **2: Parallel** | `python distributed_fl_multiprocess.py` | 1 | ~20s | Testing |
| **3: Distributed** | Server + 5 clients | 6 | ~2min | Real-time/Presentation |

---

## FOR YOUR PRESENTATION

### Demo Command Sequence (Copy-Paste Order)

**Terminal 1:**
```powershell
python START_FL_SERVER.py
```

**Wait for "SERVER STATUS: READY"**

**Terminal 2:**
```powershell
python run_single_client.py 0
```

**Terminal 3:**
```powershell
python run_single_client.py 1
```

**Terminal 4:**
```powershell
python run_single_client.py 2
```

**While running, open in browser (Terminal 7):**
```powershell
# Open dashboard
start http://127.0.0.1:5000/api/advanced-fl/dashboard

# Or check status every 2 seconds
while ($true) {
  curl http://127.0.0.1:5000/api/personalized-fl/all-clients
  start-sleep -seconds 2
}
```

---

## QUICK REFERENCE BY TASK

### Just Want to See It Work Immediately?
```powershell
python fl_with_persistent_models.py
```

### Want Real-Time Updates?
```powershell
# Terminal 1
python START_FL_SERVER.py

# Terminal 2-6 (run each in separate terminal)
python run_single_client.py 0
python run_single_client.py 1
python run_single_client.py 2
python run_single_client.py 3
python run_single_client.py 4
```

### Want Parallel Performance Test?
```powershell
python distributed_fl_multiprocess.py
```

### Want to Check Model Files?
```powershell
# After running any mode, check files created
Get-ChildItem .\client_models\
ls -la client_models/
```

### Want to Test API Endpoints?
```powershell
# While server is running
curl http://127.0.0.1:5000/

# Or with Python
python -c "import requests; print(requests.get('http://127.0.0.1:5000/api/advanced-fl/dashboard').json())"
```

---

## LINUX/MAC EQUIVALENTS

### Start Server
```bash
python START_FL_SERVER.py
```

### Start Clients
```bash
python run_single_client.py 0 &
python run_single_client.py 1 &
python run_single_client.py 2 &
python run_single_client.py 3 &
python run_single_client.py 4 &
```

### Monitor in Real-Time
```bash
watch -n 2 'curl -s http://127.0.0.1:5000/api/personalized-fl/all-clients | python -m json.tool'
```

### Stop All Clients
```bash
pkill -f run_single_client.py
```

---

## EXPECTED OUTPUT

### Mode 1 (All-In-One)
```
Round 1: Training 5 clients locally...
✓ Client 0 completed training
✓ Client 1 completed training
✓ Client 2 completed training
✓ Client 3 completed training
✓ Client 4 completed training
Round 1 Average Loss: 0.6297
Aggregating using FedAvg...
✓ Global model v1 created

Round 2: Training 5 clients locally...
... (continues for 3 rounds)

✓ Training Complete!
✓ Models saved to client_models/
✓ Central model: centralized_model_aggregated.pth
```

### Mode 3 (Distributed)
```
Terminal 1 (Server):
* Running on http://127.0.0.1:5000
ℹ️ Server is now LISTENING for connections...

Terminal 2 (Client 0):
[10:30:15] Downloading model v0...
[10:30:16] Training epoch 1/3...
[10:30:20] Training epoch 2/3...
[10:30:24] Training epoch 3/3...
[10:30:28] Uploading model to server...
[10:30:29] Uploaded! Waiting for next round...

Terminal 3 (Client 1):
[10:30:16] Downloading model v0...
[10:30:17] Training epoch 1/3...
... (similar pattern)

Terminal Browser:
Dashboard shows:
- Global Model: v1
- Client Updates: 2/5 complete
- Last Update: 2 seconds ago
```

---

## FILE OUTPUTS

### After Mode 1 or 2
```
client_models/
├── client_0_model.pth          (~13 KB)
├── client_1_model.pth          (~13 KB)
├── client_2_model.pth          (~13 KB)
├── client_3_model.pth          (~13 KB)
├── client_4_model.pth          (~13 KB)
└── centralized_model_aggregated.pth  (~13 KB)

fl_server/
├── global_models/
│   ├── global_v0.pth
│   ├── global_v1.pth
│   ├── global_v2.pth
│   └── global_v3.pth
└── client_updates/
    ├── client_0_v0.pth
    ├── client_1_v0.pth
    ...
```

### Check Files
```powershell
# View what was created
Get-ChildItem -Recurse client_models/
Get-ChildItem -Recurse fl_server/

# Check file sizes
(Get-ChildItem client_models/ | Measure-Object -Property Length -Sum).Sum / 1KB
```

---

## TROUBLESHOOTING

### Server Won't Start?
```powershell
# Kill any existing Flask processes
$proc = Get-Process -Name python -ErrorAction SilentlyContinue
if ($proc) { $proc | Stop-Process -Force }

# Try again
python START_FL_SERVER.py
```

### Port 5000 Already in Use?
```powershell
# Find what's using port 5000
Get-NetTCPConnection -LocalPort 5000

# Kill it
Stop-Process -Id <PID> -Force

# Then start server
python START_FL_SERVER.py
```

### Clients Can't Connect?
```powershell
# Check server is running
curl http://127.0.0.1:5000/api/personalized-fl/status

# Check firewall
# Windows: Ensure Python can access network in firewall settings
```

---

## FULL PRESENTATION SETUP

```powershell
# Terminal 1 - START SERVER
python START_FL_SERVER.py

# Wait 3 seconds...
Start-Sleep -Seconds 3

# Terminal 2 - START CLIENTS (all at once)
python run_single_client.py 0 &
python run_single_client.py 1 &
python run_single_client.py 2 &
python run_single_client.py 3 &
python run_single_client.py 4 &

# Terminal 3 - MONITOR DASHBOARD
# Open in browser
start http://127.0.0.1:5000/api/advanced-fl/dashboard

# Or watch updates
while ($true) {
  Write-Host "=== Update $(Get-Date) ==="
  curl http://127.0.0.1:5000/api/personalized-fl/all-clients | python -m json.tool
  start-sleep -seconds 3
}
```

---

## 🎯 RECOMMENDATIONS

### For Quick Demo (2 minutes)
```powershell
python fl_with_persistent_models.py
```

### For Midsem Presentation (15 minutes)
```powershell
# Terminal 1
python START_FL_SERVER.py

# Terminal 2-6
python run_single_client.py 0
python run_single_client.py 1
python run_single_client.py 2
python run_single_client.py 3
python run_single_client.py 4

# Show:
# 1. Clients training in parallel
# 2. Models appearing in client_models/
# 3. Dashboard updating in real-time
# 4. Loss decreasing over rounds
```

### For Testing Performance
```powershell
python distributed_fl_multiprocess.py
```

---

**System ready! Pick your mode and run!** ✅
