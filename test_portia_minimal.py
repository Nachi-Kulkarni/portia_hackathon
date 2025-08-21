#!/usr/bin/env python3
"""
Minimal Portia test to verify basic functionality
"""
import sys
import os

# Add environment variables for testing
os.environ.setdefault('PORTIA_CONFIG__OPENAI_API_KEY', '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')
os.environ.setdefault('PORTIA_CONFIG__PORTIA_API_KEY', 'prt-Lqh8JxPh.5f1Z3iRipZ6xgsGPCaNgdbPj0DuVN5Ar')
os.environ.setdefault('PORTIA_CONFIG__DEFAULT_MODEL', 'gpt-5-mini')
os.environ.setdefault('PORTIA_CONFIG__OPENAI_MODEL', 'gpt-5-mini')

def test_basic_portia():
    """Test basic Portia configuration and initialization"""
    try:
        print("🧪 Testing Basic Portia Functionality")
        print("=" * 40)
        
        # Test imports
        print("📦 Testing imports...")
        from portia import Portia, Config
        print("✅ Portia imports successful")
        
        # Test configuration
        print("⚙️  Testing configuration...")
        config = Config.from_default()
        print(f"✅ Config created: {type(config).__name__}")
        
        # Test Portia initialization
        print("🚀 Testing Portia initialization...")
        portia = Portia(config=config)
        print("✅ Portia instance created successfully")
        
        # Test basic plan creation
        print("📋 Testing plan creation...")
        plan = portia.plan("Simple test: What is 2+2?")
        print(f"✅ Plan created with ID: {plan.id}")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_portia()
    sys.exit(0 if success else 1)