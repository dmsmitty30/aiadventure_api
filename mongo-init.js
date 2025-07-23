// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the aiadventure database
db = db.getSiblingDB('aiadventure_db');

// Create collections if they don't exist
db.createCollection('users');
db.createCollection('adventures');

// Create indexes for better performance
db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "createdAt": 1 });

db.adventures.createIndex({ "owner_id": 1 });
db.adventures.createIndex({ "createdAt": 1 });
db.adventures.createIndex({ "is_public": 1 });

// Create a compound index for adventure queries
db.adventures.createIndex({ "owner_id": 1, "createdAt": -1 });

print('MongoDB initialization completed successfully!');
print('Database: aiadventure_db');
print('Collections: users, adventures');
print('Indexes created for optimal performance'); 