# Render PostgreSQL Setup Guide

## ✅ Current Status
- [x] Code changes committed and pushed
- [x] Dependencies updated (asyncpg added)
- [x] Emergency backup created (3 users protected)
- [ ] PostgreSQL database created on Render
- [ ] DATABASE_URL environment variable set
- [ ] Deployment completed
- [ ] Data migration executed

## Step 1: Create PostgreSQL Database on Render

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** button (top right)
3. **Select "PostgreSQL"**

### Database Configuration:
```
Name: miniature-tracker-db
Database: miniature_tracker
User: (leave default)
Region: Oregon (US West) - same as your web service
PostgreSQL Version: 16 (latest)
Plan: Free (1GB storage, 1 month retention)
```

4. **Click "Create Database"**
5. **Wait 1-2 minutes** for provisioning

## Step 2: Get Database Connection URL

After creation, on the database dashboard:

1. **Copy "Internal Database URL"** (preferred for Render services)
   - Format: `postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com/miniature_tracker`
   - This URL allows your web service to connect securely within Render's network

## Step 3: Add Environment Variable

1. **Go to your Web Service** (miniature-tracker)
2. **Click "Environment" tab**
3. **Add Environment Variable**:
   - **Key**: `DATABASE_URL`
   - **Value**: [paste the Internal Database URL from Step 2]
4. **Click "Save Changes"**

This will automatically trigger a redeploy.

## Step 4: Monitor Deployment

1. **Watch the "Logs" tab** during deployment
2. **Look for**:
   - ✅ "Starting deployment"
   - ✅ "Build successful" 
   - ✅ "Deploy successful"
   - ✅ Database connection messages

## Step 5: Test Database Connection

After deployment, test the connection by visiting your app:
- Your app should still work (now using PostgreSQL)
- No users should be lost (file storage still active until migration)

## Step 6: Migrate Existing Data

**Important**: Run this from your local machine after confirming PostgreSQL is working:

### Set DATABASE_URL locally for migration:
```bash
# Export the same DATABASE_URL that you set in Render
export DATABASE_URL="postgresql://user:password@dpg-xxxxx-a.oregon-postgres.render.com/miniature_tracker"
```

### Run Migration Commands:
```bash
cd backend

# Test database connection
python -c "
import asyncio
from app.database import get_database
async def test():
    db = get_database()
    await db.initialize()
    users = await db.get_all_users()
    print(f'✅ Database connected. Users: {len(users)}')
asyncio.run(test())
"

# Migrate users from file to PostgreSQL
python -m app.migration migrate

# Verify migration success
python -m app.migration verify
```

## Step 7: Verification

After migration:

### Check User Count:
```bash
python -m app.data_backup count
```

### Verify Users in Database:
```bash
python -c "
import asyncio
from app.database import PostgreSQLDatabase
import os
async def check():
    db = PostgreSQLDatabase(os.getenv('DATABASE_URL'))
    await db.initialize()
    users = await db.get_all_users()
    print(f'📊 PostgreSQL Users: {len(users)}')
    for user in users:
        print(f'  - {user.email}')
asyncio.run(check())
"
```

## 🚨 Emergency Recovery

If anything goes wrong:

### Rollback Migration:
```bash
python -m app.migration rollback
```

### Restore from Backup:
```bash
python -m app.data_backup list
python -m app.data_backup restore data_backup_20250524_151523
```

### Remove DATABASE_URL:
- Go to Render → Web Service → Environment
- Delete the `DATABASE_URL` variable
- App will fall back to file storage

## 🎉 Success Indicators

After completing all steps:
- ✅ Users can log in without issues
- ✅ No "account disappearing" reports
- ✅ Data persists across deployments
- ✅ PostgreSQL shows all migrated users

## 📋 Checklist

- [ ] PostgreSQL database created on Render
- [ ] DATABASE_URL added to web service environment
- [ ] Deployment completed successfully  
- [ ] Database connection tested
- [ ] Users migrated from file to PostgreSQL
- [ ] Migration verified
- [ ] User accounts persist across restarts

---

**Next**: After completing this setup, your account disappearing issue will be permanently resolved! 🎯 