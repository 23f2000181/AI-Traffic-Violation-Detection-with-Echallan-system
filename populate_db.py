from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')

client = MongoClient(MONGO_URI)
db = client['echallan']

# Insert mock owners
owners = [
    {
        "_id": "OWN001",
        "owner_id": "OWN001",
        "name": "Aadita Nag",
        "phone": "+916901578022",
        "address": "Mock Street, City",
        "email": "a@example.com"
    },
    {
        "_id": "OWN002",
        "owner_id": "OWN002",
        "name": "Test User",
        "phone": "+919999999999",
        "address": "Another Street, City",
        "email": "test@example.com"
    }
]

# Insert mock vehicles
vehicles = [
    {
        "_id": "MH01AB1234",
        "vehicle_no": "MH01AB1234",
        "owner_id": "OWN001",
        "make": "Honda",
        "model": "Activa",
        "color": "Red"
    },
    {
        "_id": "MH01AA0001",
        "vehicle_no": "MH01AA0001",
        "owner_id": "OWN002",
        "make": "Honda",
        "model": "CB Shine",
        "color": "Blue"
    }
]

# Insert mock rules
rules = [
    {
        "_id": "no_helmet_riding",
        "rule_id": "no_helmet_riding",
        "violation_class": "NoHelmet",
        "min_confidence": 0.45,
        "apply_to": ["two_wheeler"],
        "penalty": 500,
        "points": 2,
        "active": True
    },
    {
        "_id": "helmet_detected",
        "rule_id": "helmet_detected",
        "violation_class": "Helmet",
        "min_confidence": 0.45,
        "apply_to": ["two_wheeler"],
        "penalty": 0,  # No penalty for helmet
        "points": 0,
        "active": True
    }
]

# Insert data
db.owners.insert_many(owners)
db.vehicles.insert_many(vehicles)
db.rules.insert_many(rules)

print("Mock data inserted successfully!")
