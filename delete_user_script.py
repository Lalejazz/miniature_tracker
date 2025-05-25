#!/usr/bin/env python3
"""
Script to delete users from the Miniature Tracker database.
Usage: python delete_user_script.py
"""

import asyncio
import sys
from uuid import UUID
from pathlib import Path

# Add the backend directory to the path
sys.path.append(str(Path(__file__).parent / "backend"))

from app.user_crud import UserDB


async def list_users():
    """List all users in the database."""
    user_db = UserDB()
    users = await user_db.get_all_users()
    
    if not users:
        print("No users found in the database.")
        return []
    
    print("\n📋 Users in database:")
    print("-" * 80)
    print(f"{'ID':<38} {'Email':<30} {'Username':<20} {'Active'}")
    print("-" * 80)
    
    for user in users:
        active_status = "✅ Yes" if user.is_active else "❌ No"
        print(f"{user.id:<38} {user.email:<30} {user.username:<20} {active_status}")
    
    return users


async def delete_user_by_email(email: str):
    """Delete a user by email address."""
    user_db = UserDB()
    
    # Find user by email
    user = await user_db.get_user_by_email(email)
    if not user:
        print(f"❌ User with email '{email}' not found.")
        return False
    
    print(f"\n🔍 Found user:")
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Username: {user.username}")
    print(f"   Active: {'Yes' if user.is_active else 'No'}")
    
    # Confirm deletion
    confirm = input(f"\n⚠️  Are you sure you want to delete user '{user.email}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled.")
        return False
    
    # Delete the user
    success = await user_db.delete_user(user.id)
    
    if success:
        print(f"✅ User '{user.email}' deleted successfully!")
        return True
    else:
        print(f"❌ Failed to delete user '{user.email}'.")
        return False


async def delete_user_by_id(user_id: str):
    """Delete a user by ID."""
    user_db = UserDB()
    
    try:
        uuid_obj = UUID(user_id)
    except ValueError:
        print(f"❌ Invalid UUID format: {user_id}")
        return False
    
    # Find user by ID
    user = await user_db.get_user_by_id(uuid_obj)
    if not user:
        print(f"❌ User with ID '{user_id}' not found.")
        return False
    
    print(f"\n🔍 Found user:")
    print(f"   ID: {user.id}")
    print(f"   Email: {user.email}")
    print(f"   Username: {user.username}")
    print(f"   Active: {'Yes' if user.is_active else 'No'}")
    
    # Confirm deletion
    confirm = input(f"\n⚠️  Are you sure you want to delete user '{user.email}'? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Deletion cancelled.")
        return False
    
    # Delete the user
    success = await user_db.delete_user(uuid_obj)
    
    if success:
        print(f"✅ User '{user.email}' deleted successfully!")
        return True
    else:
        print(f"❌ Failed to delete user '{user.email}'.")
        return False


async def main():
    """Main function."""
    print("🗑️  Miniature Tracker - User Deletion Tool")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. List all users")
        print("2. Delete user by email")
        print("3. Delete user by ID")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            await list_users()
            
        elif choice == "2":
            email = input("\nEnter user email to delete: ").strip()
            if email:
                await delete_user_by_email(email)
            else:
                print("❌ Email cannot be empty.")
                
        elif choice == "3":
            user_id = input("\nEnter user ID to delete: ").strip()
            if user_id:
                await delete_user_by_id(user_id)
            else:
                print("❌ User ID cannot be empty.")
                
        elif choice == "4":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1) 