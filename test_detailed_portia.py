#!/usr/bin/env python3
"""
Detailed test to check environment variables and Portia configuration
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_environment_and_config():
    """Test environment variables and Portia configuration"""
    try:
        print("Checking environment variables...")
        
        # Check all relevant environment variables
        env_vars = [
            'PORTIA_CONFIG__PORTIA_API_KEY',
            'PORTIA_CONFIG__OPENAI_API_KEY', 
            'PORTIA_CONFIG__DEFAULT_MODEL',
            'PORTIA_CONFIG__OPENAI_MODEL',
            'DEMO_MODE'
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value:
                # Show first 10 and last 4 characters for sensitive keys
                if 'KEY' in var and len(value) > 14:
                    display_value = f"{value[:10]}...{value[-4:]}"
                else:
                    display_value = value
                print(f"  {var}: {display_value}")
            else:
                print(f"  {var}: Not set")
        
        print("\nTesting Portia SDK import...")
        
        # Import Portia
        from portia import Portia, Config
        
        print("✅ Portia imported successfully")
        
        # Try creating config with explicit parameters
        print("\nTesting config creation with explicit parameters...")
        portia_key = os.getenv('PORTIA_CONFIG__PORTIA_API_KEY')
        openai_key = os.getenv('PORTIA_CONFIG__OPENAI_API_KEY')
        default_model = os.getenv('PORTIA_CONFIG__DEFAULT_MODEL', 'gpt-4.1')
        
        if portia_key and openai_key:
            config = Config(
                portia_api_key=portia_key,
                openai_api_key=openai_key,
                default_model=default_model,
                openai_model=default_model,
                llm_provider="openai"
            )
            print("✅ Config created successfully with explicit parameters")
            print(f"Config type: {type(config)}")
            
            # Test Portia initialization
            portia = Portia(config=config)
            print("✅ Portia initialized successfully")
            
            return True
        else:
            print("❌ Missing required API keys")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_environment_and_config()
    
    if success:
        print("\n🎉 Environment and Portia test passed!")
    else:
        print("\n❌ Environment and Portia test failed!")
        sys.exit(1)