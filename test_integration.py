#!/usr/bin/env python3
"""
Test script for Finance Assistant Home Assistant Integration
"""

import asyncio
import aiohttp
import json
import sys

# Test configuration
TEST_CONFIG = {
    "host": "192.168.1.113",
    "port": 8080,
    "api_key": "your-api-key-for-home-assistant",  # Default from env
    "ssl": False
}

async def test_api_connection():
    """Test basic API connection"""
    print("🔍 Testing API connection...")
    
    base_url = f"http://{TEST_CONFIG['host']}:{TEST_CONFIG['port']}"
    headers = {"X-API-Key": TEST_CONFIG["api_key"]}
    
    try:
        async with aiohttp.ClientSession() as session:
            # Test queries endpoint
            url = f"{base_url}/api/ha/queries/"
            async with session.get(url, headers=headers) as response:
                print(f"📊 Queries endpoint: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   Found {len(data)} queries")
                    for query in data:
                        print(f"   - {query.get('name', 'Unknown')} ({query.get('output_type', 'Unknown')})")
                else:
                    print(f"   Error: {response.status}")
                    return False
            
            # Test sensor endpoint (if queries exist)
            if response.status == 200 and data:
                query_id = data[0]["id"]
                url = f"{base_url}/api/ha/sensor/{query_id}/"
                async with session.get(url, headers=headers) as response:
                    print(f"📈 Sensor endpoint: {response.status}")
                    if response.status == 200:
                        sensor_data = await response.json()
                        print(f"   Sensor data: {sensor_data}")
                    else:
                        print(f"   Error: {response.status}")
            
            # Test calendar endpoint (if queries exist)
            if response.status == 200 and data:
                query_id = data[0]["id"]
                url = f"{base_url}/api/ha/calendar/{query_id}/"
                async with session.get(url, headers=headers) as response:
                    print(f"📅 Calendar endpoint: {response.status}")
                    if response.status == 200:
                        calendar_data = await response.json()
                        print(f"   Calendar data: {len(calendar_data)} events")
                    else:
                        print(f"   Error: {response.status}")
            
            return True
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

async def test_integration_components():
    """Test integration components"""
    print("\n🔧 Testing integration components...")
    
    # Test coordinator
    try:
        from custom_components.finance_assistant.coordinator import FinanceAssistantDataUpdateCoordinator
        
        # Mock Home Assistant
        class MockHass:
            def __init__(self):
                self.data = {}
        
        hass = MockHass()
        coordinator = FinanceAssistantDataUpdateCoordinator(hass, TEST_CONFIG)
        
        print("✅ Coordinator created successfully")
        
        # Test validation
        try:
            await coordinator.async_validate_input()
            print("✅ API validation successful")
        except Exception as e:
            print(f"❌ API validation failed: {e}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Component test error: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    print("🚀 Finance Assistant Integration Test")
    print("=" * 50)
    
    # Check if API key is provided
    if len(sys.argv) > 1:
        TEST_CONFIG["api_key"] = sys.argv[1]
        print(f"🔑 Using API key: {TEST_CONFIG['api_key'][:10]}...")
    else:
        print(f"🔑 Using default API key: {TEST_CONFIG['api_key']}")
    
    print(f"🌐 Testing connection to: {TEST_CONFIG['host']}:{TEST_CONFIG['port']}")
    
    # Run tests
    loop = asyncio.get_event_loop()
    
    # Test API connection
    api_success = loop.run_until_complete(test_api_connection())
    
    # Test integration components
    component_success = loop.run_until_complete(test_integration_components())
    
    # Results
    print("\n" + "=" * 50)
    print("📋 Test Results:")
    print(f"   API Connection: {'✅ PASS' if api_success else '❌ FAIL'}")
    print(f"   Components: {'✅ PASS' if component_success else '❌ FAIL'}")
    
    if api_success and component_success:
        print("\n🎉 All tests passed! Integration is ready for use.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 