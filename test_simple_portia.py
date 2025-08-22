#!/usr/bin/env python3
"""
Simple test to verify Portia SDK works with patched files and environment variables
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_portia_basic():
    """Test basic Portia functionality"""
    try:
        print("Testing Portia SDK import and configuration...")
        
        # Import Portia
        from portia import Portia, Config
        
        print("✅ Portia imported successfully")
        
        # Test configuration with environment variables
        config = Config.from_default()
        print("✅ Config created successfully")
        print(f"Config type: {type(config)}")
        
        # Test Portia initialization
        portia = Portia(config=config)
        print("✅ Portia initialized successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_portia_basic()
    
    if success:
        print("\n🎉 Basic Portia test passed!")
    else:
        print("\n❌ Basic Portia test failed!")
        sys.exit(1)