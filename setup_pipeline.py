#!/usr/bin/env python3
"""
Setup script for Qalqalah Detection Pipeline
Installs dependencies and verifies setup
"""

import subprocess
import sys
import importlib

def install_package(package):
    """Install a package using pip"""
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        return True
    except subprocess.CalledProcessError:
        return False

def check_package(package_name):
    """Check if a package is installed"""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def main():
    print("🚀 Setting up Qalqalah Detection Pipeline...")
    print("=" * 50)
    
    # Core packages
    core_packages = [
        "librosa",
        "numpy", 
        "scikit-learn",
        "joblib",
        "pydub"
    ]
    
    # ASR packages
    asr_packages = [
        "torch",
        "torchaudio"
    ]
    
    # Optional packages
    optional_packages = [
        "whisperx",
        "stable-ts"
    ]
    
    print("📦 Installing core packages...")
    for package in core_packages:
        if not check_package(package):
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
        else:
            print(f"✅ {package} already installed")
    
    print("\n🎤 Installing ASR packages...")
    for package in asr_packages:
        if not check_package(package):
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}")
        else:
            print(f"✅ {package} already installed")
    
    print("\n🔧 Installing optional packages...")
    for package in optional_packages:
        if not check_package(package):
            print(f"Installing {package}...")
            if install_package(package):
                print(f"✅ {package} installed successfully")
            else:
                print(f"⚠️ Failed to install {package} (optional)")
        else:
            print(f"✅ {package} already installed")
    
    # Special handling for NeMo
    print("\n🤖 Installing NeMo ASR...")
    if not check_package("nemo"):
        print("Installing nemo_toolkit[asr]...")
        if install_package("nemo_toolkit[asr]"):
            print("✅ NeMo ASR installed successfully")
        else:
            print("❌ Failed to install NeMo ASR")
    else:
        print("✅ NeMo ASR already installed")
    
    print("\n" + "=" * 50)
    print("🎯 Setup Complete!")
    print("\n📋 Next steps:")
    print("1. Make sure you have the trained model file: falaq_word_model.pkl")
    print("2. Test the pipeline with: python complete_qalqalah_pipeline.py")
    print("3. For better alignment accuracy, install WhisperX: pip install whisperx")
    print("\n⚠️ Note: If you encounter issues with NeMo, try:")
    print("   pip install nemo_toolkit[asr] --extra-index-url https://pypi.ngc.nvidia.com")

if __name__ == "__main__":
    main() 