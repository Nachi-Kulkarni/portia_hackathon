#!/usr/bin/env python3
"""
Complete final test script to verify Portia SDK works fully with actual API keys
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_portia_complete():
    """Complete test of Portia with actual API keys"""
    try:
        print("Complete Portia SDK Test with Real API Keys")
        print("=" * 45)
        
        # Import Portia
        from portia import Portia, Config
        
        # Get API keys from environment
        portia_api_key = os.getenv('PORTIA_CONFIG__PORTIA_API_KEY')
        openai_api_key = os.getenv('PORTIA_CONFIG__OPENAI_API_KEY')
        
        if not portia_api_key or not openai_api_key:
            print("❌ Missing API keys in environment")
            return False
            
        print(f"Portia API Key: {portia_api_key[:10]}...{portia_api_key[-4:]}")
        print(f"OpenAI API Key: {openai_api_key[:10]}...{openai_api_key[-4:]}")
        
        # Create config with real keys
        config = Config(
            portia_api_key=portia_api_key,
            openai_api_key=openai_api_key,
            llm_provider="openai",
            default_model="gpt-4.1",
            openai_model="gpt-4.1"
        )
        print("✅ Successfully created Config with real keys")
        
        # Initialize Portia
        portia = Portia(config=config)
        print("✅ Successfully initialized Portia with real keys")
        
        # Try a very simple plan to test full functionality
        print("Creating a simple test plan...")
        plan = portia.plan("What is the capital of France?")
        print(f"✅ Successfully created plan with ID: {plan.id}")
        
        # Print plan details
        print(f"Plan has {len(plan.steps)} steps")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_portia_complete()
    
    if success:
        print("\n🎉 COMPLETE SUCCESS!")
        print("Portia SDK is fully working with Python 3.11 and real API keys!")
        print("The compatibility issue has been successfully resolved.")
        print("\nSummary:")
        print("  ✅ Import statements (fixed the 'override' decorator issue)")
        print("  ✅ Config object creation with real keys")
        print("  ✅ Portia instance initialization with real keys")
        print("  ✅ Plan creation with real LLM API calls")
    else:
        print("\n❌ Test failed. Check the errors above.")
        sys.exit(1)