#!/bin/bash

# ============================================================================
# ADVANCED FEDERATED LEARNING - COMPLETE TEST SUITE
# ============================================================================
# This script contains all commands to test FedProx, FedOpt, and pFL features
# Copy & paste individual sections or run the workflows below
# ============================================================================

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}ADVANCED FL FEATURES TEST SUITE${NC}"
echo -e "${BLUE}=================================${NC}\n"

# ============================================================================
# QUICK SETUP - Run this first
# ============================================================================
echo -e "${GREEN}>>> QUICK SETUP <<<${NC}"
echo "Make sure Flask app is running:"
echo "  cd 'c:\\Users\\harin\\OneDrive\\Documents\\8th sem\\DPSA PROJ CAT2'"
echo "  python flask_app_advanced.py"
echo -e ""

# ============================================================================
# SECTION 1: SYSTEM STATUS
# ============================================================================
echo -e "${YELLOW}1. CHECK SYSTEM STATUS (All Features)${NC}"
echo -e "${BLUE}Command:${NC}"
echo "curl http://localhost:5000/api/advanced-fl/dashboard"
echo -e "${BLUE}Description:${NC} View complete system status and all features"
echo -e ""

# ============================================================================
# SECTION 2: FEDPROX - Non-IID Data Handling
# ============================================================================
echo -e "${YELLOW}2. FEDPROX - NON-IID DATA HANDLING${NC}"

echo -e "${BLUE}Get FedProx Information:${NC}"
echo "curl http://localhost:5000/api/fedprox/status"
echo -e ""

echo -e "${BLUE}Simulate FedProx (Standard):${NC}"
echo "curl -X POST http://localhost:5000/api/fedprox/simulate -H \"Content-Type: application/json\" -d '{\"rounds\": 5, \"mu\": 0.01}'"
echo -e ""

echo -e "${BLUE}Simulate FedProx (Stronger Regularization):${NC}"
echo "curl -X POST http://localhost:5000/api/fedprox/simulate -H \"Content-Type: application/json\" -d '{\"rounds\": 10, \"mu\": 0.05}'"
echo -e ""

echo -e "${BLUE}Simulate FedProx (Weaker Regularization):${NC}"
echo "curl -X POST http://localhost:5000/api/fedprox/simulate -H \"Content-Type: application/json\" -d '{\"rounds\": 10, \"mu\": 0.001}'"
echo -e ""

# ============================================================================
# SECTION 3: FEDOPT - Adaptive Optimization
# ============================================================================
echo -e "${YELLOW}3. FEDOPT - ADAPTIVE OPTIMIZATION${NC}"

echo -e "${BLUE}Get FedOpt Information:${NC}"
echo "curl http://localhost:5000/api/fedopt/status"
echo -e ""

echo -e "${BLUE}Compare FedAdam vs FedYogi vs FedAvg:${NC}"
echo "curl http://localhost:5000/api/fedopt/compare"
echo -e ""

# ============================================================================
# SECTION 4: PERSONALIZED FL - Per-Bank Models
# ============================================================================
echo -e "${YELLOW}4. PERSONALIZED FL - BANK-SPECIFIC MODELS${NC}"

echo -e "${BLUE}Check Personalized FL Status:${NC}"
echo "curl http://localhost:5000/api/personalized-fl/status"
echo -e ""

echo -e "${BLUE}Get Performance Summary (All 5 Banks):${NC}"
echo "curl http://localhost:5000/api/personalized-fl/all-clients"
echo -e ""

echo -e "${BLUE}Get Bank 0 Model Details:${NC}"
echo "curl http://localhost:5000/api/personalized-fl/client/0"
echo -e ""

echo -e "${BLUE}Get Bank 1 Model Details:${NC}"
echo "curl http://localhost:5000/api/personalized-fl/client/1"
echo -e ""

echo -e "${BLUE}Get Bank 2 Model Details:${NC}"
echo "curl http://localhost:5000/api/personalized-fl/client/2"
echo -e ""

echo -e "${BLUE}Get Bank 3 Model Details:${NC}"
echo "curl http://localhost:5000/api/personalized-fl/client/3"
echo -e ""

echo -e "${BLUE}Get Bank 4 Model Details:${NC}"
echo "curl http://localhost:5000/api/personalized-fl/client/4"
echo -e ""

echo -e "${BLUE}Adapt Bank 0 Model:${NC}"
echo "curl -X POST http://localhost:5000/api/personalized-fl/adapt -H \"Content-Type: application/json\" -d '{\"client_id\": 0, \"accuracy\": 0.92, \"f1_score\": 0.85, \"data_size\": 15000}'"
echo -e ""

echo -e "${BLUE}Adapt Bank 1 Model:${NC}"
echo "curl -X POST http://localhost:5000/api/personalized-fl/adapt -H \"Content-Type: application/json\" -d '{\"client_id\": 1, \"accuracy\": 0.90, \"f1_score\": 0.82, \"data_size\": 18000}'"
echo -e ""

echo -e "${BLUE}Adapt Bank 2 Model:${NC}"
echo "curl -X POST http://localhost:5000/api/personalized-fl/adapt -H \"Content-Type: application/json\" -d '{\"client_id\": 2, \"accuracy\": 0.88, \"f1_score\": 0.80, \"data_size\": 12000}'"
echo -e ""

# ============================================================================
# SECTION 5: FRAUD PREDICTIONS
# ============================================================================
echo -e "${YELLOW}5. FRAUD PREDICTIONS${NC}"

echo -e "${BLUE}Predict Legitimate Transaction:${NC}"
echo "curl -X POST http://localhost:5000/predict -H \"Content-Type: application/json\" -d '{\"amount\": 500, \"time\": 14, \"type\": 0, \"device\": 0, \"location\": 0, \"prev_fraud\": 0, \"age\": 365, \"trans_24h\": 3, \"payment\": 0}'"
echo -e ""

echo -e "${BLUE}Predict Fraudulent Transaction:${NC}"
echo "curl -X POST http://localhost:5000/predict -H \"Content-Type: application/json\" -d '{\"amount\": 5000, \"time\": 3, \"type\": 1, \"device\": 1, \"location\": 1, \"prev_fraud\": 2, \"age\": 90, \"trans_24h\": 15, \"payment\": 1}'"
echo -e ""

# ============================================================================
# SECTION 6: COMPLETE WORKFLOW
# ============================================================================
echo -e "${YELLOW}6. RECOMMENDED COMPLETE WORKFLOW${NC}"

echo -e "${BLUE}Step 1: Check System${NC}"
echo "curl http://localhost:5000/api/advanced-fl/dashboard"
echo ""

echo -e "${BLUE}Step 2: Test FedProx (Non-IID Handling)${NC}"
echo "curl -X POST http://localhost:5000/api/fedprox/simulate -H \"Content-Type: application/json\" -d '{\"rounds\": 10, \"mu\": 0.01}'"
echo ""

echo -e "${BLUE}Step 3: Compare FedOpt Optimizers${NC}"
echo "curl http://localhost:5000/api/fedopt/compare"
echo ""

echo -e "${BLUE}Step 4: View All Banks${NC}"
echo "curl http://localhost:5000/api/personalized-fl/all-clients"
echo ""

echo -e "${BLUE}Step 5: Adapt Each Bank (5 commands)${NC}"
for i in {0..4}; do
  acc=$(echo "0.85 + $i * 0.015" | bc -l)
  f1=$(echo "0.80 + $i * 0.015" | bc -l)
  size=$((10000 + $i * 3000))
  echo "curl -X POST http://localhost:5000/api/personalized-fl/adapt -H \"Content-Type: application/json\" -d '{\"client_id\": $i, \"accuracy\": $acc, \"f1_score\": $f1, \"data_size\": $size}'"
done
echo ""

# ============================================================================
# SECTION 7: PYTHON EQUIVALENT COMMANDS
# ============================================================================
echo -e "${YELLOW}7. PYTHON EQUIVALENT COMMANDS${NC}"

echo -e "${BLUE}Test using Python (instead of curl):${NC}"
echo 'python -c "
import requests
import json

# System status
resp = requests.get(\"http://localhost:5000/api/advanced-fl/dashboard\")
print(\"System Status:\", json.dumps(resp.json(), indent=2))

# FedProx
resp = requests.post(\"http://localhost:5000/api/fedprox/simulate\",
    json={\"rounds\": 5, \"mu\": 0.01})
print(\"FedProx Results:\", json.dumps(resp.json(), indent=2))

# FedOpt Comparison
resp = requests.get(\"http://localhost:5000/api/fedopt/compare\")
print(\"FedOpt Comparison:\", json.dumps(resp.json(), indent=2))

# All clients
resp = requests.get(\"http://localhost:5000/api/personalized-fl/all-clients\")
print(\"All Clients:\", json.dumps(resp.json(), indent=2))
\"'
echo -e ""

# ============================================================================
# SECTION 8: COPY-PASTE READY COMMANDS
# ============================================================================
echo -e "${YELLOW}8. COPY-PASTE READY COMMANDS${NC}"

echo -e "${BLUE}Windows PowerShell Format:${NC}"
cat << 'EOF'
# Test System Status
$resp = Invoke-WebRequest -Uri "http://localhost:5000/api/advanced-fl/dashboard" -Method Get
$resp.Content | ConvertFrom-Json | ConvertTo-Json

# Test FedProx
$body = @{"rounds"=5; "mu"=0.01} | ConvertTo-Json
$resp = Invoke-WebRequest -Uri "http://localhost:5000/api/fedprox/simulate" -Method Post -Body $body -ContentType "application/json"
$resp.Content | ConvertFrom-Json | ConvertTo-Json

# Test FedOpt
$resp = Invoke-WebRequest -Uri "http://localhost:5000/api/fedopt/compare" -Method Get
$resp.Content | ConvertFrom-Json | ConvertTo-Json

# View All Banks
$resp = Invoke-WebRequest -Uri "http://localhost:5000/api/personalized-fl/all-clients" -Method Get
$resp.Content | ConvertFrom-Json | ConvertTo-Json

# Adapt Bank 0
$body = @{"client_id"=0; "accuracy"=0.92; "f1_score"=0.85; "data_size"=15000} | ConvertTo-Json
$resp = Invoke-WebRequest -Uri "http://localhost:5000/api/personalized-fl/adapt" -Method Post -Body $body -ContentType "application/json"
$resp.Content | ConvertFrom-Json | ConvertTo-Json
EOF

echo -e ""
echo -e "${BLUE}===== END OF TEST SUITE =====${NC}"
echo -e ""
echo -e "${GREEN}✓ Save this file and run individual commands${NC}"
echo -e "${GREEN}✓ Or copy sections to your terminal${NC}"
echo -e "${GREEN}✓ All commands assume Flask app is running on localhost:5000${NC}"
