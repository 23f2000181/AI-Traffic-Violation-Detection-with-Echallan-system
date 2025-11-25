"""
Mock Data Generator for E-Challan System

This script populates the MongoDB database with sample vehicle owners and vehicles
for testing the e-challan automation system.
"""

import os
import sys
from datetime import datetime

# Add parent and current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
DATABASE_NAME = 'traffic_violations'

# Sample data
SAMPLE_OWNERS = [
    {
        "owner_id": "OWN001",
        "name": "Rajesh Kumar",
        "phone": "+919627677684",
        "email": "rajesh.kumar@example.com",
        "address": "123 MG Road, Mumbai, Maharashtra 400001"
    },
    {
        "owner_id": "OWN002",
        "name": "Priya Sharma",
        "phone": "+919876543211",
        "email": "priya.sharma@example.com",
        "address": "456 Park Street, Delhi, DL 110001"
    },
    {
        "owner_id": "OWN003",
        "name": "Amit Patel",
        "phone": "+919876543212",
        "email": "amit.patel@example.com",
        "address": "789 Brigade Road, Bangalore, Karnataka 560001"
    },
    {
        "owner_id": "OWN004",
        "name": "Sneha Reddy",
        "phone": "+919876543213",
        "email": "sneha.reddy@example.com",
        "address": "321 Banjara Hills, Hyderabad, Telangana 500034"
    },
    {
        "owner_id": "OWN005",
        "name": "Vikram Singh",
        "phone": "+919876543214",
        "email": "vikram.singh@example.com",
        "address": "654 Civil Lines, Jaipur, Rajasthan 302006"
    },
    {
        "owner_id": "OWN006",
        "name": "Ananya Iyer",
        "phone": "+919876543215",
        "email": "ananya.iyer@example.com",
        "address": "987 Anna Salai, Chennai, Tamil Nadu 600002"
    },
    {
        "owner_id": "OWN007",
        "name": "Rahul Verma",
        "phone": "+919876543216",
        "email": "rahul.verma@example.com",
        "address": "147 Park Street, Kolkata, West Bengal 700016"
    },
    {
        "owner_id": "OWN008",
        "name": "Kavita Desai",
        "phone": "+919876543217",
        "email": "kavita.desai@example.com",
        "address": "258 FC Road, Pune, Maharashtra 411004"
    },
    {
        "owner_id": "OWN009",
        "name": "Arjun Nair",
        "phone": "+919876543218",
        "email": "arjun.nair@example.com",
        "address": "369 MG Road, Kochi, Kerala 682016"
    },
    {
        "owner_id": "OWN010",
        "name": "Meera Gupta",
        "phone": "+919876543219",
        "email": "meera.gupta@example.com",
        "address": "741 Hazratganj, Lucknow, Uttar Pradesh 226001"
    }
]

SAMPLE_VEHICLES = [
    {
        "vehicle_no": "TD10195",
        "owner_id": "OWN001",
        "vehicle_type": "car",
        "model": "Honda City",
        "color": "Silver"
    },
    {
        "vehicle_no": "DL02CD5678",
        "owner_id": "OWN002",
        "vehicle_type": "motorcycle",
        "model": "Royal Enfield Classic 350",
        "color": "Black"
    },
    {
        "vehicle_no": "KA03EF9012",
        "owner_id": "OWN003",
        "vehicle_type": "car",
        "model": "Maruti Swift",
        "color": "Red"
    },
    {
        "vehicle_no": "TS04GH3456",
        "owner_id": "OWN004",
        "vehicle_type": "car",
        "model": "Hyundai Creta",
        "color": "White"
    },
    {
        "vehicle_no": "RJ05IJ7890",
        "owner_id": "OWN005",
        "vehicle_type": "motorcycle",
        "model": "Bajaj Pulsar 220",
        "color": "Blue"
    },
    {
        "vehicle_no": "TN06KL2345",
        "owner_id": "OWN006",
        "vehicle_type": "car",
        "model": "Toyota Innova",
        "color": "Grey"
    },
    {
        "vehicle_no": "WB07MN6789",
        "owner_id": "OWN007",
        "vehicle_type": "car",
        "model": "Tata Nexon",
        "color": "Blue"
    },
    {
        "vehicle_no": "MH08OP1234",
        "owner_id": "OWN008",
        "vehicle_type": "motorcycle",
        "model": "Honda Activa",
        "color": "Red"
    },
    {
        "vehicle_no": "KL09QR5678",
        "owner_id": "OWN009",
        "vehicle_type": "car",
        "model": "Mahindra XUV500",
        "color": "Black"
    },
    {
        "vehicle_no": "UP10ST9012",
        "owner_id": "OWN010",
        "vehicle_type": "car",
        "model": "Kia Seltos",
        "color": "White"
    }
]

def seed_database():
    """Populate database with sample data"""
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        
        print("🚀 Starting database seeding...")
        print(f"📊 Database: {DATABASE_NAME}")
        
        # Clear existing data (optional - comment out if you want to keep existing data)
        print("\n🗑️  Clearing existing data...")
        db.owners.delete_many({})
        db.vehicles.delete_many({})
        print("✅ Existing data cleared")
        
        # Insert owners
        print("\n👥 Inserting owners...")
        for owner in SAMPLE_OWNERS:
            owner['created_at'] = datetime.utcnow()
            owner['updated_at'] = datetime.utcnow()
        
        result = db.owners.insert_many(SAMPLE_OWNERS)
        print(f"✅ Inserted {len(result.inserted_ids)} owners")
        
        # Insert vehicles
        print("\n🚗 Inserting vehicles...")
        for vehicle in SAMPLE_VEHICLES:
            vehicle['created_at'] = datetime.utcnow()
            vehicle['registered_at'] = datetime.utcnow()
        
        result = db.vehicles.insert_many(SAMPLE_VEHICLES)
        print(f"✅ Inserted {len(result.inserted_ids)} vehicles")
        
        # Create indexes
        print("\n📑 Creating indexes...")
        db.owners.create_index("owner_id", unique=True)
        db.vehicles.create_index("vehicle_no", unique=True)
        db.vehicles.create_index("owner_id")
        db.challans.create_index("challan_no", unique=True)
        db.challans.create_index("vehicle_no")
        db.challans.create_index("status")
        print("✅ Indexes created")
        
        # Display summary
        print("\n" + "="*60)
        print("📊 DATABASE SEEDING COMPLETE")
        print("="*60)
        print(f"Total Owners: {db.owners.count_documents({})}")
        print(f"Total Vehicles: {db.vehicles.count_documents({})}")
        print("\n📋 Sample Vehicle Numbers:")
        for vehicle in SAMPLE_VEHICLES[:5]:
            print(f"   - {vehicle['vehicle_no']} ({vehicle['model']})")
        print(f"   ... and {len(SAMPLE_VEHICLES) - 5} more")
        
        print("\n💡 You can now test the e-challan system with these license plates!")
        print("="*60)
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        raise

if __name__ == "__main__":
    seed_database()
