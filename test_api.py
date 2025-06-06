#!/usr/bin/env python3
"""
Test script for the Food Volume Estimation API
"""

import requests
import base64
import json
import sys
from io import BytesIO
from PIL import Image
import numpy as np

def create_test_image(width=100, height=100, color=(255, 0, 0)):
    """Create a simple test image"""
    # Create a simple colored rectangle
    img = Image.new('RGB', (width, height), color)
    
    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return img_str

def test_health_check(base_url):
    """Test the health check endpoint"""
    print("🏥 Testing health check...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_prediction(base_url, food_type="apple", img_width=200, img_height=150):
    """Test the prediction endpoint"""
    print(f"🍎 Testing prediction for {food_type}...")
    
    # Create test image
    test_img = create_test_image(img_width, img_height)
    
    payload = {
        "img": test_img,
        "food_type": food_type,
        "plate_diameter": 24.0
    }
    
    try:
        response = requests.post(
            f"{base_url}/predict",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   Food type: {result['food_type_match']}")
            print(f"   Weight: {result['weight_grams']} grams")
            print(f"   Volumes: {result['volumes_ml']} ml")
            print(f"   Density: {result['density_g_per_ml']} g/ml")
            print(f"   Image shape: {result['image_shape']}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_invalid_requests(base_url):
    """Test error handling"""
    print("🚫 Testing error handling...")
    
    # Test empty request
    try:
        response = requests.post(f"{base_url}/predict", json={})
        print(f"   Empty request - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing empty request: {e}")
    
    # Test invalid image
    try:
        response = requests.post(
            f"{base_url}/predict",
            json={"img": "invalid_base64", "food_type": "apple"}
        )
        print(f"   Invalid image - Status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error testing invalid image: {e}")

def main():
    """Main test function"""
    if len(sys.argv) != 2:
        print("Usage: python test_api.py <API_URL>")
        print("Example: python test_api.py https://your-service-url.run.app")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print("🧪 Food Volume Estimation API Test Suite")
    print("=" * 50)
    print(f"Testing API at: {base_url}")
    print()
    
    # Run tests
    tests_passed = 0
    total_tests = 0
    
    # Health check
    total_tests += 1
    if test_health_check(base_url):
        tests_passed += 1
        print("   ✅ Health check passed")
    else:
        print("   ❌ Health check failed")
    print()
    
    # Test different food types
    food_types = ["apple", "banana", "rice", "chicken", "pasta", "salad", "unknown"]
    
    for food_type in food_types:
        total_tests += 1
        if test_prediction(base_url, food_type):
            tests_passed += 1
            print(f"   ✅ {food_type} prediction passed")
        else:
            print(f"   ❌ {food_type} prediction failed")
        print()
    
    # Test error handling
    test_invalid_requests(base_url)
    print()
    
    # Results
    print("📊 Test Results")
    print("-" * 20)
    print(f"Passed: {tests_passed}/{total_tests}")
    print(f"Success rate: {(tests_passed/total_tests)*100:.1f}%")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main() 