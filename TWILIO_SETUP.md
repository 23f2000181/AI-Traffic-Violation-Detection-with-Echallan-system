# Twilio SMS Configuration Guide

## Setup Twilio for E-Challan SMS Notifications

### Step 1: Get Your Twilio Credentials

If you already have a Twilio account:
1. Go to https://console.twilio.com
2. Find your **Account SID** and **Auth Token** on the dashboard
3. Get your **Twilio Phone Number** (the number that will send SMS)

### Step 2: Update Your .env File

Edit your `.env` file in the project root (`d:\Codes\Miniproj\.env`) and add/update these lines:

```env
# MongoDB
MONGO_URI=mongodb://localhost:27017

# Twilio Configuration
TWILIO_SID=your_account_sid_here
TWILIO_TOKEN=your_auth_token_here
TWILIO_FROM=+1234567890
```

**Replace with your actual values:**
- `TWILIO_SID` - Your Twilio Account SID (starts with "AC...")
- `TWILIO_TOKEN` - Your Twilio Auth Token
- `TWILIO_FROM` - Your Twilio phone number (with country code, e.g., +1234567890)

### Step 3: Verify Phone Number Format

Make sure your friend's phone number in the database is in international format:
- ✅ Correct: `+919627677684` (with + and country code)
- ❌ Wrong: `9627677684` (missing + and country code)

You've already set it correctly in seed_data.py: `+919627677684`

### Step 4: Test the System

After updating `.env`:

1. **Restart the backend server** (important - it needs to reload the .env):
   ```bash
   # Stop current server (Ctrl+C)
   python app.py
   ```

2. **Upload an image** with license plate `TD10195`

3. **Check the SMS** - Your friend should receive:
   ```
   Traffic Violation Alert!
   
   Vehicle: TD10195
   Owner: Rajesh Kumar
   Challan No: CH20251125...
   Violations: Helmet Violation
   Total Penalty: ₹500
   Due Date: 25/12/2025
   
   Please pay your fine before the due date to avoid additional charges.
   ```

### Step 5: Check Logs

The backend will show:
- ✅ If Twilio is configured: "✅ SMS sent to +919627677684 - SID: SM..."
- ⚠️ If not configured: "⚠️ Twilio not configured - SMS not sent"

## Example .env File

```env
MONGO_URI=mongodb://localhost:27017
TWILIO_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_TOKEN=your_auth_token_here
TWILIO_FROM=+15551234567
```

## Troubleshooting

**"Twilio not configured" message:**
- Check that TWILIO_SID, TWILIO_TOKEN, and TWILIO_FROM are set in .env
- Restart the backend server after updating .env

**SMS not received:**
- Verify phone number format: `+919627677684`
- Check Twilio console for delivery status
- Ensure Twilio account has credits
- Check if number is verified (for trial accounts)

**Trial Account Limitations:**
- Twilio trial accounts can only send to verified phone numbers
- You need to verify your friend's number in Twilio console first
- Or upgrade to a paid account

## Without Twilio

If you don't configure Twilio, the system will still work but show:
```
⚠️ Twilio not configured - SMS not sent
📧 Email would be sent to: rajesh.kumar@example.com
```

The challan will still be generated and saved to the database!
