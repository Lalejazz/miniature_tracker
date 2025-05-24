"""Data backup and migration utilities."""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


class DataBackupManager:
    """Handles backup and restore of user data."""
    
    def __init__(self, backup_dir: str = "backup"):
        """Initialize backup manager."""
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self) -> str:
        """Create a timestamped backup of all data files."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"data_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        backup_path.mkdir(exist_ok=True)
        
        # Define data files to backup
        data_files = [
            "data/users.json",
            "data/miniatures.json",
            "data/reset_tokens.json"
        ]
        
        backed_up_files = []
        
        for data_file in data_files:
            source_path = Path(__file__).parent.parent / data_file
            if source_path.exists():
                dest_path = backup_path / source_path.name
                
                # Copy file content
                with open(source_path, 'r') as src:
                    content = src.read()
                with open(dest_path, 'w') as dst:
                    dst.write(content)
                
                backed_up_files.append(data_file)
        
        # Create backup info file
        backup_info = {
            "timestamp": timestamp,
            "created_at": datetime.now().isoformat(),
            "files": backed_up_files,
            "backup_name": backup_name
        }
        
        info_path = backup_path / "backup_info.json"
        with open(info_path, 'w') as f:
            json.dump(backup_info, f, indent=2)
        
        print(f"✅ Backup created: {backup_path}")
        print(f"📁 Backed up files: {', '.join(backed_up_files)}")
        
        return str(backup_path)
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """List all available backups."""
        backups = []
        
        for backup_dir in self.backup_dir.iterdir():
            if backup_dir.is_dir():
                info_file = backup_dir / "backup_info.json"
                if info_file.exists():
                    try:
                        with open(info_file, 'r') as f:
                            backup_info = json.load(f)
                        backup_info["path"] = str(backup_dir)
                        backups.append(backup_info)
                    except json.JSONDecodeError:
                        continue
        
        return sorted(backups, key=lambda x: x["created_at"], reverse=True)
    
    def restore_backup(self, backup_name: str) -> bool:
        """Restore data from a specific backup."""
        backup_path = self.backup_dir / backup_name
        
        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_name}")
            return False
        
        info_file = backup_path / "backup_info.json"
        if not info_file.exists():
            print(f"❌ Invalid backup (missing info file): {backup_name}")
            return False
        
        try:
            with open(info_file, 'r') as f:
                backup_info = json.load(f)
        except json.JSONDecodeError:
            print(f"❌ Corrupted backup info: {backup_name}")
            return False
        
        # Restore each file
        data_dir = Path(__file__).parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        
        restored_files = []
        for filename in backup_info.get("files", []):
            source_file = backup_path / Path(filename).name
            dest_file = data_dir / Path(filename).name
            
            if source_file.exists():
                with open(source_file, 'r') as src:
                    content = src.read()
                with open(dest_file, 'w') as dst:
                    dst.write(content)
                restored_files.append(filename)
        
        print(f"✅ Backup restored: {backup_name}")
        print(f"📁 Restored files: {', '.join(restored_files)}")
        
        return True
    
    def get_user_count(self, backup_name: Optional[str] = None) -> int:
        """Get user count from current data or specific backup."""
        if backup_name:
            backup_path = self.backup_dir / backup_name
            users_file = backup_path / "users.json"
        else:
            users_file = Path(__file__).parent.parent / "data" / "users.json"
        
        if not users_file.exists():
            return 0
        
        try:
            with open(users_file, 'r') as f:
                users = json.load(f)
            return len(users) if isinstance(users, list) else 0
        except (json.JSONDecodeError, FileNotFoundError):
            return 0


def create_emergency_backup() -> str:
    """Create an emergency backup immediately."""
    backup_manager = DataBackupManager()
    return backup_manager.create_backup()


def main():
    """CLI interface for backup operations."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_backup.py [backup|list|restore|count]")
        sys.exit(1)
    
    command = sys.argv[1]
    backup_manager = DataBackupManager()
    
    if command == "backup":
        create_emergency_backup()
    
    elif command == "list":
        backups = backup_manager.list_backups()
        if not backups:
            print("📁 No backups found")
        else:
            print("📁 Available backups:")
            for backup in backups:
                user_count = backup_manager.get_user_count(backup["backup_name"])
                print(f"  - {backup['backup_name']} ({backup['created_at']}) - {user_count} users")
    
    elif command == "restore":
        if len(sys.argv) < 3:
            print("Usage: python data_backup.py restore <backup_name>")
            sys.exit(1)
        
        backup_name = sys.argv[2]
        backup_manager.restore_backup(backup_name)
    
    elif command == "count":
        current_count = backup_manager.get_user_count()
        print(f"👥 Current user count: {current_count}")
    
    else:
        print("Unknown command. Use: backup, list, restore, or count")


if __name__ == "__main__":
    main() 