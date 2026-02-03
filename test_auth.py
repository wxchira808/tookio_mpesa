#!/usr/bin/env python3
"""
Quick test script to verify M-Pesa authentication
Run: bench --site tookio-shop.local console < test_auth.py
"""

import frappe
from tookio_mpesa.utils import get_access_token, test_mpesa_credentials

# Test getting access token
print("=" * 60)
print("Testing M-Pesa Authentication")
print("=" * 60)

try:
    print("\n1. Testing access token retrieval...")
    token = get_access_token()
    print(f"✅ SUCCESS! Got access token: {token[:20]}...")
    
except Exception as e:
    print(f"❌ FAILED: {str(e)}")

print("\n" + "=" * 60)
print("2. Testing credential validation...")
print("=" * 60)

try:
    result = test_mpesa_credentials()
    print(f"\n✅ Settings loaded:")
    print(f"   Environment: {result.get('environment')}")
    print(f"   Has Consumer Key: {result.get('has_consumer_key')}")
    print(f"   Has Consumer Secret: {result.get('has_consumer_secret')}")
    
    if 'auth_test' in result:
        auth = result['auth_test']
        print(f"\n📡 Auth Test:")
        print(f"   Status: {auth.get('status_code')}")
        print(f"   Success: {auth.get('success')}")
        if auth.get('success'):
            print(f"   ✅ Authentication working!")
        else:
            print(f"   ❌ Auth failed: {auth.get('response_text', '')[:200]}")
            
except Exception as e:
    print(f"❌ FAILED: {str(e)}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
