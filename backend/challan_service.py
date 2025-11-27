import os
import sys
from datetime import datetime, timedelta

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as Config_module
import database as db_module

Config = Config_module.Config
db = db_module.db

class ChallanService:
    """Service for e-challan generation and management"""
    
    # Penalty amounts (in INR)
    PENALTIES = {
        "helmet_violation": 500,
        "triple_riding_violation": 1000,
        "red_light_violation": 1000,
        "no_license_plate": 2000,
        "speeding": 1500,
        "default": 500
    }
    
    def __init__(self):
        self.db = db
    
    def generate_challan_number(self):
        """Generate unique challan number"""
        timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
        count = self.db.db.challans.count_documents({})
        return f"CH{timestamp}{count:03d}"
    
    def calculate_penalty(self, violations):
        """
        Calculate total penalty based on violations
        
        Args:
            violations: List of violation types
            
        Returns:
            int: Total penalty amount
        """
        total = 0
        for violation in violations:
            violation_type = violation.get('type', 'default')
            total += self.PENALTIES.get(violation_type, self.PENALTIES['default'])
        
        return total
    
    def generate_challan(self, violation_data, vehicle_info):
        """
        Generate e-challan from violation data
        
        Args:
            violation_data: Violation record from detection
            vehicle_info: Vehicle and owner information
            
        Returns:
            dict: Generated challan
        """
        try:
            # Extract violations
            violations = []
            
            # Helmet violations
            for hv in violation_data.get('detection_results', {}).get('helmet_violations', []):
                violations.append({
                    'type': 'helmet_violation',
                    'penalty': self.PENALTIES['helmet_violation'],
                    'confidence': hv.get('confidence', 0)
                })
            
            # Triple riding violations
            for trv in violation_data.get('detection_results', {}).get('triple_riding_violations', []):
                violations.append({
                    'type': 'triple_riding_violation',
                    'penalty': self.PENALTIES['triple_riding_violation'],
                    'confidence': trv.get('confidence', 0),
                    'person_count': trv.get('person_count', 0)
                })
            
            # Red light violations
            for rv in violation_data.get('detection_results', {}).get('red_light_violations', []):
                violations.append({
                    'type': 'red_light_violation',
                    'penalty': self.PENALTIES['red_light_violation'],
                    'confidence': rv.get('confidence', 0)
                })
            
            # Calculate total penalty
            total_penalty = sum(v['penalty'] for v in violations)
            
            # Generate challan
            challan = {
                'challan_no': self.generate_challan_number(),
                'vehicle_no': vehicle_info['vehicle']['vehicle_no'],
                'owner_id': vehicle_info['owner']['owner_id'],
                'owner_name': vehicle_info['owner']['name'],
                'violation_id': str(violation_data.get('_id', '')),
                'violations': violations,
                'total_penalty': total_penalty,
                'status': 'issued',
                'issued_at': datetime.utcnow(),
                'due_date': datetime.utcnow() + timedelta(days=30),
                'paid_at': None,
                'notification_sent': False,
                'notification_log': []
            }
            
            # Save to database
            result = self.db.db.challans.insert_one(challan)
            challan['_id'] = str(result.inserted_id)
            
            print(f"✅ Challan generated: {challan['challan_no']} - Amount: ₹{total_penalty}")
            
            return challan
            
        except Exception as e:
            print(f"❌ Error generating challan: {e}")
            raise
    
    def get_challan(self, challan_no):
        """Get challan by challan number"""
        try:
            challan = self.db.db.challans.find_one({"challan_no": challan_no})
            if challan:
                challan['_id'] = str(challan['_id'])
            return challan
        except Exception as e:
            print(f"❌ Error getting challan: {e}")
            return None
    
    def get_all_challans(self, page=1, page_size=50, filters=None):
        """Get all challans with pagination and filters"""
        try:
            query = {}
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query['status'] = filters['status']
                if filters.get('vehicle_no'):
                    query['vehicle_no'] = filters['vehicle_no']
            
            skip = (page - 1) * page_size
            total = self.db.db.challans.count_documents(query)
            
            challans = list(
                self.db.db.challans
                .find(query)
                .sort("issued_at", -1)
                .skip(skip)
                .limit(page_size)
            )
            
            # Convert ObjectId to string
            for c in challans:
                c['_id'] = str(c['_id'])
            
            return {
                'challans': challans,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        except Exception as e:
            print(f"❌ Error getting challans: {e}")
            raise
    
    def update_challan_status(self, challan_no, status):
        """Update challan status"""
        try:
            update_data = {'status': status}
            
            if status == 'paid':
                update_data['paid_at'] = datetime.utcnow()
            
            result = self.db.db.challans.update_one(
                {"challan_no": challan_no},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Challan status updated: {challan_no} -> {status}")
                return True
            
            return False
        except Exception as e:
            print(f"❌ Error updating challan status: {e}")
            return False
    
    def log_notification(self, challan_no, method, status, message=""):
        """Log notification attempt"""
        try:
            log_entry = {
                'method': method,
                'sent_at': datetime.utcnow(),
                'status': status,
                'message': message
            }
            
            self.db.db.challans.update_one(
                {"challan_no": challan_no},
                {
                    "$set": {"notification_sent": status == 'success'},
                    "$push": {"notification_log": log_entry}
                }
            )
            
            print(f"📝 Notification logged: {challan_no} - {method} - {status}")
            
        except Exception as e:
            print(f"❌ Error logging notification: {e}")
    
    def get_challan_statistics(self):
        """Get challan statistics for dashboard"""
        try:
            total_challans = self.db.db.challans.count_documents({})
            total_issued = self.db.db.challans.count_documents({"status": "issued"})
            total_paid = self.db.db.challans.count_documents({"status": "paid"})
            total_pending = self.db.db.challans.count_documents({"status": "pending"})
            
            # Calculate total penalties
            pipeline = [
                {
                    '$group': {
                        '_id': None,
                        'total_penalties': {'$sum': '$total_penalty'},
                        'paid_penalties': {
                            '$sum': {
                                '$cond': [
                                    {'$eq': ['$status', 'paid']},
                                    '$total_penalty',
                                    0
                                ]
                            }
                        }
                    }
                }
            ]
            
            result = list(self.db.db.challans.aggregate(pipeline))
            penalties = result[0] if result else {'total_penalties': 0, 'paid_penalties': 0}
            
            return {
                'total_challans': total_challans,
                'issued': total_issued,
                'paid': total_paid,
                'pending': total_pending,
                'total_penalties': penalties.get('total_penalties', 0),
                'paid_penalties': penalties.get('paid_penalties', 0),
                'pending_penalties': penalties.get('total_penalties', 0) - penalties.get('paid_penalties', 0)
            }
        except Exception as e:
            print(f"❌ Error getting challan statistics: {e}")
            raise

# Global service instance
challan_service = ChallanService()
