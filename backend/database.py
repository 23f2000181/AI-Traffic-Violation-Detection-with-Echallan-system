from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure
from bson import ObjectId
from datetime import datetime
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as Config_module
Config = Config_module.Config

class Database:
    """MongoDB database operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client[Config.DATABASE_NAME]
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            self.setup_indexes()
        except ConnectionFailure as e:
            print(f"❌ MongoDB connection failed: {e}")
            raise
    
    def setup_indexes(self):
        """Create indexes for better query performance"""
        try:
            # Violations collection indexes
            self.db.violations.create_index([("timestamp", DESCENDING)])
            self.db.violations.create_index([("status", 1)])
            print("✅ Database indexes created")
        except Exception as e:
            print(f"⚠️ Error creating indexes: {e}")
    
    # Violation Operations
    
    def create_violation(self, violation_data):
        """Create a new violation record"""
        try:
            violation_data['timestamp'] = datetime.utcnow()
            result = self.db.violations.insert_one(violation_data)
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error creating violation: {e}")
            raise
    
    def get_violation(self, violation_id):
        """Get a specific violation by ID"""
        try:
            return self.db.violations.find_one({"_id": ObjectId(violation_id)})
        except Exception as e:
            print(f"❌ Error getting violation: {e}")
            return None
    
    def get_violations(self, page=1, page_size=50, filters=None):
        """Get paginated violations with optional filters"""
        try:
            query = {}
            
            # Apply filters
            if filters:
                if filters.get('status'):
                    query['status'] = filters['status']
                if filters.get('date_from'):
                    query['timestamp'] = {'$gte': filters['date_from']}
                if filters.get('date_to'):
                    if 'timestamp' in query:
                        query['timestamp']['$lte'] = filters['date_to']
                    else:
                        query['timestamp'] = {'$lte': filters['date_to']}
            
            # Calculate skip
            skip = (page - 1) * page_size
            
            # Get total count
            total = self.db.violations.count_documents(query)
            
            # Get violations
            violations = list(
                self.db.violations
                .find(query)
                .sort("timestamp", DESCENDING)
                .skip(skip)
                .limit(page_size)
            )
            
            # Convert ObjectId to string
            for v in violations:
                v['_id'] = str(v['_id'])
            
            return {
                'violations': violations,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        except Exception as e:
            print(f"❌ Error getting violations: {e}")
            raise
    
    def delete_violation(self, violation_id):
        """Delete a violation by ID"""
        try:
            result = self.db.violations.delete_one({"_id": ObjectId(violation_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"❌ Error deleting violation: {e}")
            return False
    
    def get_statistics(self):
        """Get violation statistics for dashboard"""
        try:
            # Total violations
            total_violations = self.db.violations.count_documents({})
            
            # Violations by type
            pipeline = [
                {
                    '$project': {
                        'license_plate_count': {'$size': {'$ifNull': ['$detection_results.license_plates', []]}},
                        'helmet_count': {'$size': {'$ifNull': ['$detection_results.helmet_violations', []]}},
                        'red_light_count': {'$size': {'$ifNull': ['$detection_results.red_light_violations', []]}}
                    }
                },
                {
                    '$group': {
                        '_id': None,
                        'total_license_plates': {'$sum': '$license_plate_count'},
                        'total_helmet_violations': {'$sum': '$helmet_count'},
                        'total_red_light_violations': {'$sum': '$red_light_count'}
                    }
                }
            ]
            
            result = list(self.db.violations.aggregate(pipeline))
            stats = result[0] if result else {
                'total_license_plates': 0,
                'total_helmet_violations': 0,
                'total_red_light_violations': 0
            }
            
            # Recent violations (last 10)
            recent = list(
                self.db.violations
                .find({}, {'timestamp': 1, 'status': 1, 'detection_results': 1})
                .sort("timestamp", DESCENDING)
                .limit(10)
            )
            
            for v in recent:
                v['_id'] = str(v['_id'])
            
            return {
                'total_violations': total_violations,
                'license_plates': stats.get('total_license_plates', 0),
                'helmet_violations': stats.get('total_helmet_violations', 0),
                'red_light_violations': stats.get('total_red_light_violations', 0),
                'recent_violations': recent
            }
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            raise
    
    # Configuration Operations
    
    def get_config(self):
        """Get system configuration"""
        try:
            config = self.db.system_config.find_one({})
            if config:
                config['_id'] = str(config['_id'])
            return config
        except Exception as e:
            print(f"❌ Error getting config: {e}")
            return None
    
    def update_config(self, config_data):
        """Update system configuration"""
        try:
            result = self.db.system_config.update_one(
                {},
                {'$set': config_data},
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"❌ Error updating config: {e}")
            return False

# Global database instance
db = Database()
