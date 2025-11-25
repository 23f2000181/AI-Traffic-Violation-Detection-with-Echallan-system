# E-Challan System Integration Guide

## Quick Setup

The e-challan automation system is now ready! Here's how to set it up and test it:

### Step 1: Seed the Database with Mock Data

Run this command to populate the database with 10 sample vehicle owners and vehicles:

```bash
python backend\seed_data.py
```

This will create:
- 10 vehicle owners with names, phone numbers, and addresses
- 10 vehicles with license plates like MH01AB1234, DL02CD5678, etc.
- Database indexes for fast lookup

### Step 2: Restart the Backend Server

Since you have the backend running, you'll need to restart it to load the new services:

1. Stop the current backend (Ctrl+C in the terminal)
2. Start it again:
   ```bash
   python backend\app.py
   ```

### Step 3: Test the E-Challan System

#### Option 1: Upload an Image with a Known License Plate

1. Go to the Upload page in your browser
2. Upload an image that contains one of these license plates:
   - MH01AB1234 (Honda City - Owner: Rajesh Kumar)
   - DL02CD5678 (Royal Enfield - Owner: Priya Sharma)
   - KA03EF9012 (Maruti Swift - Owner: Amit Patel)
   - ... and 7 more

3. The system will:
   - Detect the license plate
   - Look up the vehicle in the database
   - Find the owner information
   - Generate an e-challan automatically
   - Send SMS notification (if Twilio is configured)

#### Option 2: Test API Endpoints Directly

**Lookup a vehicle:**
```bash
curl http://localhost:5000/api/vehicles/MH01AB1234
```

**Get all challans:**
```bash
curl http://localhost:5000/api/challans
```

**Get challan statistics:**
```bash
curl http://localhost:5000/api/challans/statistics
```

### Step 4: View Results

After uploading an image with a detected license plate:

1. **Results Page** will show:
   - Vehicle owner information
   - Generated challan number
   - Penalty amount
   - Notification status

2. **Challan History** (coming in frontend update):
   - List of all issued challans
   - Filter by status (issued, paid, pending)
   - Update challan status

## New API Endpoints Available

### Vehicle Management
- `GET /api/vehicles/<plate_number>` - Lookup vehicle
- `GET /api/vehicles` - List all vehicles
- `POST /api/vehicles` - Register new vehicle
- `GET /api/owners` - List all owners
- `POST /api/owners` - Register new owner

### Challan Management
- `GET /api/challans` - List all challans
- `GET /api/challans/<challan_no>` - Get specific challan
- `PUT /api/challans/<challan_no>/status` - Update status
- `POST /api/challans/<challan_no>/notify` - Resend notification
- `GET /api/challans/statistics` - Get statistics

## Penalty Structure

- Helmet Violation: ₹500
- Red Light Violation: ₹1000
- No License Plate: ₹2000
- Speeding: ₹1500

## SMS Notifications

If you have Twilio configured in your `.env` file, SMS notifications will be sent automatically to the vehicle owner's phone number when a challan is generated.

**SMS Format:**
```
Traffic Violation Alert!

Vehicle: MH01AB1234
Owner: Rajesh Kumar
Challan No: CH20251125001
Violations: Helmet Violation
Total Penalty: ₹500
Due Date: 25/12/2025

Please pay your fine before the due date to avoid additional charges.
```

## Next Steps

1. Run `python backend\seed_data.py` to populate database
2. Restart backend server
3. Upload test images
4. Check if challans are generated
5. View challan statistics

The frontend components for challan display will be added next!
