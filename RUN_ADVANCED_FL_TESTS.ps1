# ============================================================================
# ADVANCED FEDERATED LEARNING - COMPLETE TEST SUITE (PowerShell)
# ============================================================================
# Windows Users: Run this in PowerShell
# Copy & paste individual sections or run the workflows below
# ============================================================================

function Print-Section {
    param([string]$title)
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "=" -NoNewline -ForegroundColor Cyan
    Write-Host $title -ForegroundColor Yellow
    Write-Host "=" -ForegroundColor Cyan
}

function Print-Command {
    param([string]$cmd, [string]$desc)
    Write-Host "`n[COMMAND]" -ForegroundColor Green
    Write-Host $cmd -ForegroundColor White -BackgroundColor Black
    if ($desc) {
        Write-Host "[Description]: $desc" -ForegroundColor Cyan
    }
}

# ============================================================================
# STARTUP
# ============================================================================
clear
Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Magenta
Write-Host "║  ADVANCED FL FEATURES - TEST SUITE        ║" -ForegroundColor Magenta
Write-Host "║  (FedProx, FedOpt, Personalized FL)       ║" -ForegroundColor Magenta
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Magenta

Write-Host "`n✓ Prerequisites:" -ForegroundColor Green
Write-Host "  1. Flask app running: python flask_app_advanced.py"
Write-Host "  2. On: http://localhost:5000"
Write-Host "`nReady? Press Enter to continue..." -ForegroundColor Yellow
# Read-Host

# ============================================================================
# FUNCTION: Test API Endpoint
# ============================================================================
function Test-Endpoint {
    param(
        [string]$endpoint,
        [string]$method = "GET",
        [hashtable]$body = $null,
        [string]$description = ""
    )
    
    $uri = "http://localhost:5000$endpoint"
    
    try {
        $params = @{
            Uri = $uri
            Method = $method
            ContentType = "application/json"
        }
        
        if ($body) {
            $params["Body"] = ($body | ConvertTo-Json)
        }
        
        $response = Invoke-WebRequest @params
        $json = $response.Content | ConvertFrom-Json
        
        Write-Host "`n✓ SUCCESS" -ForegroundColor Green
        if ($description) {
            Write-Host "   $description"
        }
        Write-Host "   Response:" -ForegroundColor Cyan
        $json | ConvertTo-Json | Write-Host -ForegroundColor White
        
        return $json
    } catch {
        Write-Host "`n✗ FAILED" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        return $null
    }
}

# ============================================================================
# MENU
# ============================================================================
function Show-Menu {
    Write-Host "`n╔════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  SELECT TEST SECTION                       ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host "
    1. Check System Status
    2. FedProx (Non-IID Handling)
    3. FedOpt (Adaptive Optimization)
    4. Personalized FL (Bank Models)
    5. Run Complete Workflow
    6. Make Fraud Predictions
    7. Copy Command Examples
    8. Exit
    
" -ForegroundColor Yellow
}

# ============================================================================
# SECTION 1: System Status
# ============================================================================
function Test-SystemStatus {
    clear
    Print-Section "SYSTEM STATUS - All Features"
    
    Test-Endpoint -endpoint "/api/advanced-fl/dashboard" -description "Complete system overview"
}

# ============================================================================
# SECTION 2: FedProx
# ============================================================================
function Test-FedProx {
    clear
    Print-Section "FEDPROX - Non-IID Data Handling"
    
    Write-Host "`n1. Get FedProx Information:" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedprox/status" -description "FedProx configuration and benefits"
    
    Write-Host "`n2. Simulate FedProx Training (5 rounds, standard):" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedprox/simulate" -method "POST" `
        -body @{"rounds"=5; "mu"=0.01} `
        -description "Non-IID convergence simulation"
    
    Write-Host "`n3. Simulate FedProx Training (10 rounds, stronger regularization):" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedprox/simulate" -method "POST" `
        -body @{"rounds"=10; "mu"=0.05} `
        -description "Stronger model stability"
    
    Press-Enter
}

# ============================================================================
# SECTION 3: FedOpt
# ============================================================================
function Test-FedOpt {
    clear
    Print-Section "FEDOPT - Adaptive Optimization"
    
    Write-Host "`n1. Get FedOpt Information:" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedopt/status" -description "FedAdam and FedYogi details"
    
    Write-Host "`n2. Compare Optimizers:" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedopt/compare" -description "FedAdam vs FedYogi vs FedAvg"
    
    Press-Enter
}

# ============================================================================
# SECTION 4: Personalized FL
# ============================================================================
function Test-PersonalizedFL {
    clear
    Print-Section "PERSONALIZED FL - Bank-Specific Models"
    
    Write-Host "`n1. Personalized FL Status:" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/personalized-fl/status" -description "System overview"
    
    Write-Host "`n2. All Banks Performance:" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/personalized-fl/all-clients" -description "Summary across all 5 banks"
    
    Write-Host "`n3. Individual Bank Details:" -ForegroundColor Green
    for ($i = 0; $i -lt 5; $i++) {
        Write-Host "`   Bank $i:" -ForegroundColor Cyan
        Test-Endpoint -endpoint "/api/personalized-fl/client/$i" -description "Bank-specific model info"
    }
    
    Write-Host "`n4. Adapt Bank Models:" -ForegroundColor Green
    for ($i = 0; $i -lt 5; $i++) {
        $acc = 0.85 + ($i * 0.02)
        $f1 = 0.80 + ($i * 0.02)
        $size = 10000 + ($i * 3000)
        Write-Host "`   Adapting Bank $i..." -ForegroundColor Cyan
        Test-Endpoint -endpoint "/api/personalized-fl/adapt" -method "POST" `
            -body @{"client_id"=$i; "accuracy"=$acc; "f1_score"=$f1; "data_size"=$size}
    }
    
    Write-Host "`n5. View Updated Banks:" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/personalized-fl/all-clients" -description "Updated performance summary"
    
    Press-Enter
}

# ============================================================================
# SECTION 5: Complete Workflow
# ============================================================================
function Test-CompleteWorkflow {
    clear
    Print-Section "COMPLETE WORKFLOW - Step by Step"
    
    Write-Host "`nStep 1: System Status" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/advanced-fl/dashboard" -description "Verify all features active"
    Write-Host "Press Enter to continue..." -ForegroundColor Yellow
    Read-Host > $null
    
    Write-Host "`nStep 2: FedProx Simulation" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedprox/simulate" -method "POST" `
        -body @{"rounds"=10; "mu"=0.01}
    Write-Host "Press Enter to continue..." -ForegroundColor Yellow
    Read-Host > $null
    
    Write-Host "`nStep 3: Compare Optimizers" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/fedopt/compare"
    Write-Host "Press Enter to continue..." -ForegroundColor Yellow
    Read-Host > $null
    
    Write-Host "`nStep 4: All Banks Summary" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/personalized-fl/all-clients"
    Write-Host "Press Enter to continue..." -ForegroundColor Yellow
    Read-Host > $null
    
    Write-Host "`nStep 5: Adapt All Banks" -ForegroundColor Green
    for ($i = 0; $i -lt 5; $i++) {
        $acc = 0.85 + ($i * 0.02)
        $f1 = 0.80 + ($i * 0.02)
        $size = 10000 + ($i * 3000)
        Write-Host "Bank $i..." -ForegroundColor Cyan -NoNewline
        Test-Endpoint -endpoint "/api/personalized-fl/adapt" -method "POST" `
            -body @{"client_id"=$i; "accuracy"=$acc; "f1_score"=$f1; "data_size"=$size} `
            -description "Adapted" | Out-Null
        Write-Host " ✓" -ForegroundColor Green
    }
    
    Write-Host "`nStep 6: Final Summary" -ForegroundColor Green
    Test-Endpoint -endpoint "/api/personalized-fl/all-clients"
    
    Press-Enter
}

# ============================================================================
# SECTION 6: Fraud Predictions
# ============================================================================
function Test-Predictions {
    clear
    Print-Section "FRAUD PREDICTIONS"
    
    Write-Host "`n1. Legitimate Transaction:" -ForegroundColor Green
    Test-Endpoint -endpoint "/predict" -method "POST" `
        -body @{
            "amount"=500
            "time"=14
            "type"=0
            "device"=0
            "location"=0
            "prev_fraud"=0
            "age"=365
            "trans_24h"=3
            "payment"=0
        }
    
    Write-Host "`n2. Suspicious Transaction:" -ForegroundColor Green
    Test-Endpoint -endpoint "/predict" -method "POST" `
        -body @{
            "amount"=2500
            "time"=3
            "type"=1
            "device"=1
            "location"=1
            "prev_fraud"=1
            "age"=180
            "trans_24h"=10
            "payment"=1
        }
    
    Write-Host "`n3. Highly Fraudulent Transaction:" -ForegroundColor Green
    Test-Endpoint -endpoint "/predict" -method "POST" `
        -body @{
            "amount"=5000
            "time"=2
            "type"=1
            "device"=2
            "location"=1
            "prev_fraud"=3
            "age"=90
            "trans_24h"=15
            "payment"=1
        }
    
    Press-Enter
}

# ============================================================================
# SECTION 7: Display Command Examples
# ============================================================================
function Show-CommandExamples {
    clear
    Print-Section "COPY-PASTE READY COMMANDS"
    
    $code = @'
# ===== FEDPROX =====
$body = @{"rounds"=5; "mu"=0.01} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/fedprox/simulate" `
    -Method Post -Body $body -ContentType "application/json" | 
    Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

# ===== FEDOPT COMPARISON =====
Invoke-WebRequest -Uri "http://localhost:5000/api/fedopt/compare" -Method Get |
    Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

# ===== PERSONALIZED FL - ALL CLIENTS =====
Invoke-WebRequest -Uri "http://localhost:5000/api/personalized-fl/all-clients" -Method Get |
    Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

# ===== ADAPT BANK 0 =====
$body = @{"client_id"=0; "accuracy"=0.92; "f1_score"=0.85; "data_size"=15000} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/api/personalized-fl/adapt" `
    -Method Post -Body $body -ContentType "application/json" |
    Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json

# ===== FRAUD PREDICTION =====
$body = @{
    "amount"=2500
    "time"=3
    "type"=1
    "device"=1
    "location"=1
    "prev_fraud"=1
    "age"=180
    "trans_24h"=10
    "payment"=1
} | ConvertTo-Json
Invoke-WebRequest -Uri "http://localhost:5000/predict" `
    -Method Post -Body $body -ContentType "application/json" |
    Select-Object -ExpandProperty Content | ConvertFrom-Json | ConvertTo-Json
'@
    
    Write-Host $code -ForegroundColor White -BackgroundColor Black
    
    Write-Host "`n✓ Commands copied above. Paste into PowerShell to run." -ForegroundColor Green
    Press-Enter
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================
function Press-Enter {
    Write-Host "`nPress Enter to return to menu..." -ForegroundColor Yellow
    Read-Host > $null
}

# ============================================================================
# MAIN LOOP
# ============================================================================
do {
    Show-Menu
    $choice = Read-Host "Enter selection (1-8)"
    
    switch ($choice) {
        "1" { Test-SystemStatus }
        "2" { Test-FedProx }
        "3" { Test-FedOpt }
        "4" { Test-PersonalizedFL }
        "5" { Test-CompleteWorkflow }
        "6" { Test-Predictions }
        "7" { Show-CommandExamples }
        "8" {
            Write-Host "`nExiting... Goodbye!" -ForegroundColor Green
            exit
        }
        default {
            Write-Host "Invalid selection. Please try again." -ForegroundColor Red
        }
    }
} while ($true)
