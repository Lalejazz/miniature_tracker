#!/usr/bin/env python3
"""
Script to check users in file storage.
"""
import json

def check_file_users():
    """Check users in the file storage."""
    try:
        with open('data/users.json', 'r') as f:
            users = json.load(f)
        
        print('=== Users in File Storage ===')
        print(f'Total users in file: {len(users)}')
        print()
        
        for i, user in enumerate(users, 1):
            print(f'{i}. Email: {user["email"]}')
            print(f'   Username: {user["username"]}')
            print(f'   Created: {user["created_at"]}')
            print(f'   Active: {user.get("is_active", True)}')
            print()
            
    except FileNotFoundError:
        print("users.json file not found")
    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_file_users() 