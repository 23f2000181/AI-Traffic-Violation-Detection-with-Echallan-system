# MongoDB Connection Fix

## The Problem
Your `.env` file has MongoDB configured to port **27018**, but MongoDB Compass typically runs on port **27017**.

## Quick Fix

### Option 1: Check MongoDB Compass Connection String
1. Open **MongoDB Compass**
2. Look at your connection string at the top
3. It probably shows: `mongodb://localhost:27017`

### Option 2: Update Your .env File

Edit your `.env` file in the project root and change:

**FROM:**
```
MONGO_URI=mongodb://localhost:27018
```

**TO:**
```
MONGO_URI=mongodb://localhost:27017
```

## How to Find Your MongoDB Port

1. **Open MongoDB Compass**
2. Look at the connection string - it will show the port number
3. Common ports:
   - `27017` - Default MongoDB port
   - `27018` - Sometimes used for replica sets
   - `27019` - Sometimes used for config servers

## After Fixing

1. Save your `.env` file
2. Restart the backend:
   ```bash
   python backend\app.py
   ```

## If You're Using a Different Port

If your MongoDB is actually running on a different port (not 27017), you can:

1. Keep your `.env` file as is
2. Or check which port MongoDB is actually running on:
   - Open MongoDB Compass
   - Check the connection string
   - Use that port in your `.env` file

## Current Default

The backend is now configured to use `mongodb://localhost:27017` by default if no `.env` is found or if MONGO_URI is not set.
