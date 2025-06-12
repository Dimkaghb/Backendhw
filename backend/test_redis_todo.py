#!/usr/bin/env python3
"""
Test script for Redis todo creation
"""

from celery_app import create_redis_todo_task

def test_redis_todo_creation():
    """Test creating a Redis todo manually"""
    print("🧪 Testing Redis todo creation...")
    
    try:
        # Call the task directly (not through Celery)
        result = create_redis_todo_task()
        print(f"✅ Success! Result: {result}")
        return True
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_redis_todo_creation()
    if success:
        print("\n🎉 Redis todo creation test passed!")
    else:
        print("\n💥 Redis todo creation test failed!") 