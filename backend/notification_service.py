import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import challan_service as challan_service_module

challan_service = challan_service_module.challan_service

# Twilio configuration
TWILIO_SID = os.getenv('TWILIO_SID')
TWILIO_TOKEN = os.getenv('TWILIO_TOKEN')
TWILIO_FROM = os.getenv('TWILIO_FROM')

# Initialize Twilio client if credentials are available
twilio_client = None
if TWILIO_SID and TWILIO_TOKEN:
    try:
        from twilio.rest import Client
        twilio_client = Client(TWILIO_SID, TWILIO_TOKEN)
        print("✅ Twilio client initialized")
    except Exception as e:
        print(f"⚠️  Twilio initialization failed: {e}")

class NotificationService:
    """Service for sending notifications (SMS/Email)"""
    
    def __init__(self):
        self.twilio_client = twilio_client
        self.challan_service = challan_service
    
    def format_challan_message(self, challan):
        """
        Format challan information into notification message
        
        Args:
            challan: Challan record
            
        Returns:
            str: Formatted message
        """
        violation_types = [v['type'].replace('_', ' ').title() for v in challan['violations']]
        violations_str = ', '.join(violation_types)
        
        due_date = challan['due_date'].strftime('%d/%m/%Y') if isinstance(challan['due_date'], datetime) else str(challan['due_date'])
        
        message = f"""Traffic Violation Alert!

Vehicle: {challan['vehicle_no']}
Owner: {challan['owner_name']}
Challan No: {challan['challan_no']}
Violations: {violations_str}
Total Penalty: ₹{challan['total_penalty']}
Due Date: {due_date}

Please pay your fine before the due date to avoid additional charges.
"""
        return message
    
    def send_sms(self, phone, message):
        """
        Send SMS notification via Twilio
        
        Args:
            phone: Phone number (with country code)
            message: Message text
            
        Returns:
            dict: Status and message ID
        """
        try:
            if not self.twilio_client:
                print("⚠️  Twilio not configured - SMS not sent")
                return {
                    'status': 'mock',
                    'message': 'Twilio not configured. SMS would be sent in production.',
                    'phone': phone
                }
            
            # Send SMS
            msg = self.twilio_client.messages.create(
                body=message,
                from_=TWILIO_FROM,
                to=phone
            )
            
            print(f"✅ SMS sent to {phone} - SID: {msg.sid}")
            
            return {
                'status': 'success',
                'sid': msg.sid,
                'phone': phone
            }
            
        except Exception as e:
            print(f"❌ Error sending SMS: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'phone': phone
            }
    
    def send_email(self, email, subject, body):
        """
        Send email notification
        
        Note: Email functionality is mocked for now.
        In production, integrate with SendGrid, AWS SES, or similar service.
        
        Args:
            email: Email address
            subject: Email subject
            body: Email body
            
        Returns:
            dict: Status
        """
        try:
            # Mock email sending
            print(f"📧 Email would be sent to: {email}")
            print(f"   Subject: {subject}")
            print(f"   Body: {body[:100]}...")
            
            return {
                'status': 'mock',
                'message': 'Email functionality not implemented. Would be sent in production.',
                'email': email
            }
            
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return {
                'status': 'failed',
                'error': str(e),
                'email': email
            }
    
    def send_challan_notification(self, challan, methods=['sms']):
        """
        Send challan notification via specified methods
        
        Args:
            challan: Challan record
            methods: List of notification methods ['sms', 'email']
            
        Returns:
            dict: Notification results
        """
        results = {}
        message = self.format_challan_message(challan)
        
        # Get owner phone from challan or lookup
        # For now, we'll assume phone is in the challan or need to lookup
        
        if 'sms' in methods:
            # Extract phone from owner info
            # This would need to be passed or looked up
            phone = challan.get('owner_phone', '')
            
            if phone:
                sms_result = self.send_sms(phone, message)
                results['sms'] = sms_result
                
                # Log notification
                self.challan_service.log_notification(
                    challan['challan_no'],
                    'sms',
                    sms_result['status'],
                    sms_result.get('message', '')
                )
            else:
                results['sms'] = {
                    'status': 'failed',
                    'error': 'No phone number available'
                }
        
        if 'email' in methods:
            email = challan.get('owner_email', '')
            
            if email:
                subject = f"E-Challan Notice - {challan['challan_no']}"
                email_result = self.send_email(email, subject, message)
                results['email'] = email_result
                
                # Log notification
                self.challan_service.log_notification(
                    challan['challan_no'],
                    'email',
                    email_result['status'],
                    email_result.get('message', '')
                )
            else:
                results['email'] = {
                    'status': 'failed',
                    'error': 'No email address available'
                }
        
        return results

# Global service instance
notification_service = NotificationService()
