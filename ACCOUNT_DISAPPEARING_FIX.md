# Account Disappearing Issue - Root Cause & Solution

## 🚨 Problem Description

Users are reporting that their accounts disappear and they can re-subscribe with the same email. This is a **critical data persistence issue**.

## 🔍 Root Cause Analysis

### The Issue
The application uses **file-based JSON storage** (`backend/data/users.json`) in an **ephemeral container environment**:

1. **Ephemeral File System**: Platforms like Railway, Render, and Heroku use containers that reset on every deployment/restart
2. **No Persistent Volume**: JSON files are stored in the container's temporary file system
3. **Container Restarts**: Every deployment, scaling event, or crash resets the file system to its initial state
4. **Data Loss**: User accounts stored in JSON files get deleted when containers restart

### Evidence Found
- ✅ JSON files exist locally: `backend/data/users.json`, `backend/data/miniatures.json`
- ✅ No persistent storage configuration in deployment files
- ✅ File-based `UserDB` class initializes empty files if they don't exist
- ✅ No database backup/restore mechanisms in place

## 🛠️ Solution Implemented

### 1. Database Abstraction Layer (`backend/app/database.py`)
Created a new database interface that supports both:
- **FileDatabase**: For local development (existing behavior)
- **PostgreSQLDatabase**: For production with persistent storage

```python
def get_database() -> DatabaseInterface:
    """Auto-selects database based on DATABASE_URL environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if database_url and database_url.startswith("postgresql"):
        return PostgreSQLDatabase(database_url)
    else:
        return FileDatabase()
```

### 2. Data Backup System (`backend/app/data_backup.py`)
- **Automatic Backups**: Create timestamped backups before any migration
- **Restore Capability**: Restore from any backup if needed
- **CLI Interface**: Easy backup management

### 3. Migration Tools (`backend/app/migration.py`)
- **Safe Migration**: Migrate existing users from JSON to PostgreSQL
- **Verification**: Verify migration success
- **Rollback**: Restore from backup if migration fails

## 🚀 Deployment Steps

### Immediate Fix (Emergency Backup)
```bash
cd backend
python -m app.data_backup backup
```

### Production Setup

#### Option 1: PostgreSQL Database (Recommended)
1. **Add PostgreSQL to your hosting platform**:
   - Railway: Add PostgreSQL plugin
   - Render: Add PostgreSQL database
   - Heroku: Add Heroku Postgres addon

2. **Set Environment Variable**:
   ```bash
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

3. **Install Dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

4. **Migrate Existing Data**:
   ```bash
   python -m app.migration migrate
   python -m app.migration verify
   ```

#### Option 2: Persistent Volume (Alternative)
If you prefer to keep JSON files, mount a persistent volume:
- Railway: Use volume mounts
- Render: Use persistent disks
- Map `/app/backend/data` to persistent storage

## 📋 Verification Steps

### Check Current User Count
```bash
python -m app.data_backup count
```

### List Available Backups
```bash
python -m app.data_backup list
```

### Verify Database Connection
```bash
# Set DATABASE_URL first
python -c "
import asyncio
from app.database import get_database
async def test():
    db = get_database()
    await db.initialize()
    users = await db.get_all_users()
    print(f'Database connected. Users: {len(users)}')
asyncio.run(test())
"
```

## 🔧 Configuration Changes

### Environment Variables
Add to your deployment platform:
```bash
DATABASE_URL=postgresql://user:password@host:port/database
```

### Dependencies Updated
Added to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies ...
    "asyncpg>=0.29.0",  # PostgreSQL async driver
]
```

## 🛡️ Prevention Measures

### 1. Automated Backups
Set up daily backups in production:
```bash
# Add to cron or deployment script
python -m app.data_backup backup
```

### 2. Health Checks
Monitor user count to detect data loss:
```bash
python -m app.data_backup count
```

### 3. Database Monitoring
- Monitor PostgreSQL connection health
- Set up alerts for connection failures
- Regular database backups via hosting platform

## 🚨 Emergency Recovery

If accounts disappear again:

1. **Check Latest Backup**:
   ```bash
   python -m app.data_backup list
   ```

2. **Restore from Backup**:
   ```bash
   python -m app.data_backup restore <backup_name>
   ```

3. **Verify Restoration**:
   ```bash
   python -m app.data_backup count
   ```

## 📊 Impact Assessment

### Before Fix
- ❌ User accounts lost on every deployment
- ❌ No data persistence
- ❌ Users can re-register with same email
- ❌ No backup/recovery system

### After Fix
- ✅ Persistent PostgreSQL storage
- ✅ Automatic backup system
- ✅ Migration tools for existing data
- ✅ Rollback capability
- ✅ Environment-based database selection

## 🔄 Rollback Plan

If issues occur after deployment:

1. **Immediate Rollback**:
   ```bash
   python -m app.migration rollback
   ```

2. **Remove DATABASE_URL** (falls back to file storage)

3. **Restore from Backup**:
   ```bash
   python -m app.data_backup restore <backup_name>
   ```

## 📝 Next Steps

1. **Deploy PostgreSQL database** on your hosting platform
2. **Set DATABASE_URL** environment variable
3. **Run migration** to move existing users
4. **Set up automated backups** for ongoing protection
5. **Monitor user count** to ensure data persistence

## 🔗 Related Files

- `backend/app/database.py` - New database abstraction layer
- `backend/app/data_backup.py` - Backup and restore utilities
- `backend/app/migration.py` - Migration tools
- `backend/pyproject.toml` - Updated dependencies
- `backend/app/user_crud.py` - Original file-based implementation (kept for reference)

---

**Priority**: 🔴 **CRITICAL** - Deploy immediately to prevent further data loss 