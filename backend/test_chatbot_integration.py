#!/usr/bin/env python3
"""
Test script for chatbot integration
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USERNAME = f"testuser_{int(time.time())}"
TEST_PASSWORD = "testpass123"

def test_chatbot_integration():
    print("🧪 Testing Chatbot Integration with LangChain & LlamaIndex")
    print("=" * 60)
    
    # Step 1: Create a test user
    print("1. Creating test user...")
    signup_response = requests.post(
        f"{BASE_URL}/signup",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    
    if signup_response.status_code == 200:
        print("✅ User created successfully")
    else:
        print(f"❌ Failed to create user: {signup_response.text}")
        return
    
    # Step 2: Login to get token
    print("2. Logging in...")
    login_response = requests.post(
        f"{BASE_URL}/login",
        json={"username": TEST_USERNAME, "password": TEST_PASSWORD}
    )
    
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        print("✅ Login successful")
    else:
        print(f"❌ Failed to login: {login_response.text}")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Step 3: Test chatbot endpoint
    print("3. Testing chatbot...")
    
    test_messages = [
        "Hello, who is the CEO of the company?",
        "What services does the company provide?",
        "Tell me about Sarah Johnson",
        "What are the recent projects?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📤 Message {i}: {message}")
        
        chat_response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": message},
            headers=headers
        )
        
        if chat_response.status_code == 200:
            response_data = chat_response.json()
            print(f"🤖 Bot Response: {response_data['response']}")
        else:
            print(f"❌ Chat failed: {chat_response.text}")
        
        time.sleep(1)  # Small delay between messages
    
    # Step 4: Test chat history
    print("\n4. Testing chat history...")
    history_response = requests.get(f"{BASE_URL}/chat/history", headers=headers)
    
    if history_response.status_code == 200:
        history = history_response.json()["history"]
        print(f"✅ Chat history retrieved: {len(history)} messages")
    else:
        print(f"❌ Failed to get history: {history_response.text}")
    
    # Step 5: Test clear chat
    print("5. Testing clear chat...")
    clear_response = requests.post(f"{BASE_URL}/chat/clear", headers=headers)
    
    if clear_response.status_code == 200:
        print("✅ Chat cleared successfully")
    else:
        print(f"❌ Failed to clear chat: {clear_response.text}")
    
    print("\n🎉 Chatbot integration test completed!")

if __name__ == "__main__":
    try:
        test_chatbot_integration()
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to the server. Make sure the FastAPI app is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 