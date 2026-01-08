// MongoDB Initialization Script
// Creates collections, indexes, and initial data for fraud detection system

// Switch to fraud_detection database
db = db.getSiblingDB('fraud_detection');

// Create collections with validation schemas
db.createCollection('fraud_evaluations', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['transaction_id', 'user_id', 'risk_level', 'reasons', 'timestamp', 'status'],
            properties: {
                transaction_id: {
                    bsonType: 'string',
                    description: 'Unique transaction identifier'
                },
                user_id: {
                    bsonType: 'string',
                    description: 'User identifier'
                },
                risk_level: {
                    enum: ['LOW_RISK', 'MEDIUM_RISK', 'HIGH_RISK'],
                    description: 'Risk level classification'
                },
                reasons: {
                    bsonType: 'array',
                    description: 'List of reasons for risk classification',
                    items: {
                        bsonType: 'string'
                    }
                },
                timestamp: {
                    bsonType: 'date',
                    description: 'Evaluation timestamp'
                },
                status: {
                    enum: ['APPROVED', 'REJECTED', 'PENDING_REVIEW'],
                    description: 'Transaction status'
                },
                amount: {
                    bsonType: 'double',
                    description: 'Transaction amount'
                },
                location: {
                    bsonType: 'object',
                    properties: {
                        latitude: {
                            bsonType: 'double',
                            minimum: -90,
                            maximum: 90
                        },
                        longitude: {
                            bsonType: 'double',
                            minimum: -180,
                            maximum: 180
                        }
                    }
                },
                reviewed_by: {
                    bsonType: 'string',
                    description: 'Analyst ID who reviewed'
                },
                reviewed_at: {
                    bsonType: 'date',
                    description: 'Review timestamp'
                }
            }
        }
    }
});

// Create indexes for performance
db.fraud_evaluations.createIndex({ transaction_id: 1 }, { unique: true });
db.fraud_evaluations.createIndex({ user_id: 1 });
db.fraud_evaluations.createIndex({ timestamp: -1 });
db.fraud_evaluations.createIndex({ status: 1 });
db.fraud_evaluations.createIndex({ risk_level: 1 });

// Create audit log collection
db.createCollection('audit_logs', {
    validator: {
        $jsonSchema: {
            bsonType: 'object',
            required: ['action', 'user_id', 'timestamp'],
            properties: {
                action: {
                    bsonType: 'string',
                    description: 'Action performed'
                },
                user_id: {
                    bsonType: 'string',
                    description: 'User who performed action'
                },
                timestamp: {
                    bsonType: 'date',
                    description: 'Action timestamp'
                },
                details: {
                    bsonType: 'object',
                    description: 'Additional action details'
                }
            }
        }
    }
});

db.audit_logs.createIndex({ timestamp: -1 });
db.audit_logs.createIndex({ user_id: 1 });

// Create user locations cache collection (for fallback if Redis fails)
db.createCollection('user_locations');
db.user_locations.createIndex({ user_id: 1 }, { unique: true });
db.user_locations.createIndex({ updated_at: 1 }, { expireAfterSeconds: 86400 }); // TTL 24h

print('✅ MongoDB initialized successfully');
print('📊 Collections created: fraud_evaluations, audit_logs, user_locations');
print('🔍 Indexes created for optimal query performance');
