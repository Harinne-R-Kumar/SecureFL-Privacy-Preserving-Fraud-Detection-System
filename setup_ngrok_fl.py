#!/usr/bin/env python3
"""
SETUP SCRIPT FOR NGROK FEDERATED LEARNING
Automates the setup process for the federated learning system
"""

import os
import sys
import subprocess
import platform
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("❌ Python 3.7+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements_ngrok.txt"
        ])
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def check_ngrok():
    """Check if ngrok is installed and accessible"""
    try:
        result = subprocess.run(['ngrok', 'version'], 
                               capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ ngrok found: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("❌ ngrok not found")
    print("💡 Please download and install ngrok from: https://ngrok.com/download")
    print("💡 Make sure ngrok is in your system PATH")
    return False

def check_existing_files():
    """Check if required files exist"""
    required_files = [
        'flask_app_advanced.py',
        'federated_learning_training.py',
        'centralized_model_balanced.pth',
        'preprocessed_data_balanced.pkl'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def create_start_script():
    """Create a convenient start script"""
    script_content = '''@echo off
echo ========================================
echo FEDERATED LEARNING SERVER STARTUP
echo ========================================
echo.

echo Checking prerequisites...
python setup_ngrok_fl.py --check-only
if errorlevel 1 (
    echo.
    echo ❌ Setup failed. Please fix the issues above.
    pause
    exit /b 1
)

echo.
echo 🚀 Starting Federated Learning Server with Ngrok...
echo.
python ngrok_server.py

pause
'''
    
    with open('start_fl_server.bat', 'w') as f:
        f.write(script_content)
    
    print("✅ Created start_fl_server.bat")

def create_client_script():
    """Create a convenient client connection script"""
    script_content = '''@echo off
echo ========================================
echo FEDERATED LEARNING CLIENT
echo ========================================
echo.

if "%1"=="" (
    echo Usage: %0 [SERVER_URL] [CLIENT_NAME] [DATA_SIZE]
    echo Example: %0 https://abc123.ngrok.io MyBank 5000
    echo.
    set /p SERVER_URL="Enter server URL: "
) else (
    set SERVER_URL=%1
)

if "%2"=="" (
    set CLIENT_NAME=MyClient
) else (
    set CLIENT_NAME=%2
)

if "%3"=="" (
    set DATA_SIZE=1000
) else (
    set DATA_SIZE=%3
)

echo.
echo 🌐 Connecting to: %SERVER_URL%
echo 👤 Client Name: %CLIENT_NAME%
echo 📊 Data Size: %DATA_SIZE%
echo.

python fl_client.py --server "%SERVER_URL%" --name "%CLIENT_NAME%" --data-size %DATA_SIZE%

pause
'''
    
    with open('connect_client.bat', 'w') as f:
        f.write(script_content)
    
    print("✅ Created connect_client.bat")

def main():
    """Main setup function"""
    import argparse
    parser = argparse.ArgumentParser(description='Setup Ngrok Federated Learning')
    parser.add_argument('--check-only', action='store_true', 
                       help='Only check prerequisites, don\'t install')
    
    args = parser.parse_args()
    
    print("="*60)
    print("🔧 NGROK FEDERATED LEARNING SETUP")
    print("="*60)
    
    # Check prerequisites
    checks_passed = True
    
    checks_passed &= check_python_version()
    
    if not args.check_only:
        checks_passed &= install_requirements()
    
    checks_passed &= check_ngrok()
    checks_passed &= check_existing_files()
    
    if not checks_passed:
        print("\n❌ Setup failed. Please fix the issues above.")
        return False
    
    if not args.check_only:
        # Create convenience scripts
        create_start_script()
        create_client_script()
        
        print("\n" + "="*60)
        print("✅ SETUP COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("1. Start the server:")
        print("   run: start_fl_server.bat")
        print("   OR: python ngrok_server.py")
        print("\n2. Connect clients:")
        print("   run: connect_client.bat [SERVER_URL] [NAME] [DATA_SIZE]")
        print("   OR: python fl_client.py --server https://your-ngrok-url.ngrok.io")
        print("\n3. Open dashboard:")
        print("   Navigate to the ngrok URL provided by the server")
        print("\n💡 Example client command:")
        print("   python fl_client.py --server https://abc123.ngrok.io --name BankA --data-size 5000")
        
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
