import os
import sys
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config as Config_module
import database as db_module

Config = Config_module.Config
db = db_module.db

class VehicleService:
    """Service for vehicle and owner management"""
    
    def __init__(self):
        self.db = db
    
    def lookup_vehicle(self, plate_number):
        """
        Lookup vehicle by license plate number
        
        Args:
            plate_number: License plate (e.g., "MH01AB1234")
            
        Returns:
            dict: Vehicle and owner information, or None if not found
        """
        try:
            # Normalize plate number (uppercase, remove spaces)
            plate_number = plate_number.upper().replace(" ", "")
            
            # Find vehicle
            vehicle = self.db.db.vehicles.find_one({"vehicle_no": plate_number})
            
            if not vehicle:
                print(f"⚠️  Vehicle not found: {plate_number}")
                return None
            
            # Find owner
            owner = self.db.db.owners.find_one({"owner_id": vehicle["owner_id"]})
            
            if not owner:
                print(f"⚠️  Owner not found for vehicle: {plate_number}")
                return None
            
            # Combine vehicle and owner info
            result = {
                "vehicle": {
                    "vehicle_no": vehicle["vehicle_no"],
                    "vehicle_type": vehicle.get("vehicle_type", "unknown"),
                    "model": vehicle.get("model", ""),
                    "color": vehicle.get("color", "")
                },
                "owner": {
                    "owner_id": owner["owner_id"],
                    "name": owner["name"],
                    "phone": owner["phone"],
                    "email": owner.get("email", ""),
                    "address": owner.get("address", "")
                }
            }
            
            print(f"✅ Vehicle found: {plate_number} - Owner: {owner['name']}")
            return result
            
        except Exception as e:
            print(f"❌ Error looking up vehicle: {e}")
            return None
    
    def get_owner_info(self, owner_id):
        """Get owner details by owner ID"""
        try:
            owner = self.db.db.owners.find_one({"owner_id": owner_id})
            if owner:
                owner['_id'] = str(owner['_id'])
            return owner
        except Exception as e:
            print(f"❌ Error getting owner info: {e}")
            return None
    
    def register_vehicle(self, vehicle_data):
        """Register a new vehicle"""
        try:
            vehicle_data['created_at'] = datetime.utcnow()
            result = self.db.db.vehicles.insert_one(vehicle_data)
            print(f"✅ Vehicle registered: {vehicle_data['vehicle_no']}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error registering vehicle: {e}")
            raise
    
    def register_owner(self, owner_data):
        """Register a new owner"""
        try:
            owner_data['created_at'] = datetime.utcnow()
            owner_data['updated_at'] = datetime.utcnow()
            result = self.db.db.owners.insert_one(owner_data)
            print(f"✅ Owner registered: {owner_data['name']}")
            return str(result.inserted_id)
        except Exception as e:
            print(f"❌ Error registering owner: {e}")
            raise
    
    def get_all_vehicles(self, page=1, page_size=50):
        """Get all vehicles with pagination"""
        try:
            skip = (page - 1) * page_size
            total = self.db.db.vehicles.count_documents({})
            
            vehicles = list(
                self.db.db.vehicles
                .find({})
                .skip(skip)
                .limit(page_size)
            )
            
            # Convert ObjectId to string
            for v in vehicles:
                v['_id'] = str(v['_id'])
            
            return {
                'vehicles': vehicles,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        except Exception as e:
            print(f"❌ Error getting vehicles: {e}")
            raise
    
    def get_all_owners(self, page=1, page_size=50):
        """Get all owners with pagination"""
        try:
            skip = (page - 1) * page_size
            total = self.db.db.owners.count_documents({})
            
            owners = list(
                self.db.db.owners
                .find({})
                .skip(skip)
                .limit(page_size)
            )
            
            # Convert ObjectId to string
            for o in owners:
                o['_id'] = str(o['_id'])
            
            return {
                'owners': owners,
                'total': total,
                'page': page,
                'page_size': page_size,
                'total_pages': (total + page_size - 1) // page_size
            }
        except Exception as e:
            print(f"❌ Error getting owners: {e}")
            raise

# Global service instance
vehicle_service = VehicleService()
