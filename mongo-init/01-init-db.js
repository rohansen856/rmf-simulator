// mongo-init/01-init-db.js - MongoDB initialization script
// This script runs when MongoDB container starts for the first time

// Switch to the rmf_monitoring database
db = db.getSiblingDB('rmf_monitoring');

// Create the application user
db.createUser({
  user: 'rmf_user',
  pwd: 'rmf_password',
  roles: [
    {
      role: 'readWrite',
      db: 'rmf_monitoring'
    },
    {
      role: 'dbAdmin',
      db: 'rmf_monitoring'
    }
  ]
});

// Create collections with schema validation (optional but recommended)
db.createCollection('cpu_metrics', {
//   validator: {
//     $jsonSchema: {
//       bsonType: 'object',
//       required: ['timestamp', 'sysplex', 'lpar', 'cpu_type', 'utilization_percent'],
//       properties: {
//         timestamp: { bsonType: 'date' },
//         sysplex: { bsonType: 'string' },
//         lpar: { bsonType: 'string' },
//         cpu_type: { bsonType: 'string' },
//         utilization_percent: { bsonType: 'double', minimum: 0, maximum: 100 }
//       }
//     }
//   }
});

db.createCollection('memory_metrics', {
//   validator: {
//     $jsonSchema: {
//       bsonType: 'object',
//       required: ['timestamp', 'sysplex', 'lpar', 'memory_type', 'usage_bytes'],
//       properties: {
//         timestamp: { bsonType: 'date' },
//         sysplex: { bsonType: 'string' },
//         lpar: { bsonType: 'string' },
//         memory_type: { bsonType: 'string' },
//         usage_bytes: { bsonType: 'long', minimum: 0 }
//       }
//     }
//   }
});

db.createCollection('ldev_utilization_metrics', {
//   validator: {
//     $jsonSchema: {
//       bsonType: 'object',
//       required: ['timestamp', 'sysplex', 'lpar', 'device_id', 'utilization_percent'],
//       properties: {
//         timestamp: { bsonType: 'date' },
//         sysplex: { bsonType: 'string' },
//         lpar: { bsonType: 'string' },
//         device_id: { bsonType: 'string' },
//         utilization_percent: { bsonType: 'double', minimum: 0, maximum: 100 }
//       }
//     }
//   }
});

db.createCollection('ldev_response_time_metrics', {
//   validator: {
//     $jsonSchema: {
//       bsonType: 'object',
//       required: ['timestamp', 'sysplex', 'lpar', 'device_type', 'response_time_seconds'],
//       properties: {
//         timestamp: { bsonType: 'date' },
//         sysplex: { bsonType: 'string' },
//         lpar: { bsonType: 'string' },
//         device_type: { bsonType: 'string' },
//         response_time_seconds: { bsonType: 'double', minimum: 0 }
//       }
//     }
//   }
});

// Create indexes for better performance
print('Creating indexes...');

// CPU metrics indexes
db.cpu_metrics.createIndex({ 'timestamp': -1 });
db.cpu_metrics.createIndex({ 'lpar': 1, 'cpu_type': 1 });
db.cpu_metrics.createIndex({ 'sysplex': 1, 'timestamp': -1 });
db.cpu_metrics.createIndex({ 'timestamp': 1 }, { expireAfterSeconds: 7776000 }); // 90 days TTL

// Memory metrics indexes
db.memory_metrics.createIndex({ 'timestamp': -1 });
db.memory_metrics.createIndex({ 'lpar': 1, 'memory_type': 1 });
db.memory_metrics.createIndex({ 'sysplex': 1, 'timestamp': -1 });
db.memory_metrics.createIndex({ 'timestamp': 1 }, { expireAfterSeconds: 7776000 });

// LDEV utilization indexes
db.ldev_utilization_metrics.createIndex({ 'timestamp': -1 });
db.ldev_utilization_metrics.createIndex({ 'device_id': 1 });
db.ldev_utilization_metrics.createIndex({ 'lpar': 1, 'timestamp': -1 });
db.ldev_utilization_metrics.createIndex({ 'timestamp': 1 }, { expireAfterSeconds: 7776000 });

// LDEV response time indexes
db.ldev_response_time_metrics.createIndex({ 'timestamp': -1 });
db.ldev_response_time_metrics.createIndex({ 'device_type': 1 });
db.ldev_response_time_metrics.createIndex({ 'lpar': 1, 'timestamp': -1 });
db.ldev_response_time_metrics.createIndex({ 'timestamp': 1 }, { expireAfterSeconds: 7776000 });

// Create remaining collections with basic structure
const collections = [
  'clpr_service_time_metrics',
  'clpr_request_rate_metrics',
  'mpb_processing_rate_metrics',
  'mpb_queue_depth_metrics',
  'ports_utilization_metrics',
  'ports_throughput_metrics',
  'volumes_utilization_metrics',
  'volumes_iops_metrics'
];

collections.forEach(function(collectionName) {
  if (!db.getCollectionNames().includes(collectionName)) {
    db.createCollection(collectionName);
    
    // Create basic indexes for all collections
    db[collectionName].createIndex({ 'timestamp': -1 });
    db[collectionName].createIndex({ 'lpar': 1, 'timestamp': -1 });
    db[collectionName].createIndex({ 'sysplex': 1, 'timestamp': -1 });
    db[collectionName].createIndex({ 'timestamp': 1 }, { expireAfterSeconds: 7776000 }); // 90 days TTL
  }
});

// Create specific indexes for specialized collections
db.clpr_service_time_metrics.createIndex({ 'cf_link': 1 });
db.clpr_request_rate_metrics.createIndex({ 'cf_link': 1, 'request_type': 1 });
db.mpb_processing_rate_metrics.createIndex({ 'queue_type': 1 });
db.mpb_queue_depth_metrics.createIndex({ 'queue_type': 1 });
db.ports_utilization_metrics.createIndex({ 'port_type': 1, 'port_id': 1 });
db.ports_throughput_metrics.createIndex({ 'port_type': 1, 'port_id': 1 });
db.volumes_utilization_metrics.createIndex({ 'volume_type': 1, 'volume_id': 1 });
db.volumes_iops_metrics.createIndex({ 'volume_type': 1, 'volume_id': 1 });

// Create aggregation views for common queries
db.createView('cpu_summary', 'cpu_metrics', [
  {
    $group: {
      _id: {
        lpar: '$lpar',
        cpu_type: '$cpu_type',
        hour: { $hour: '$timestamp' }
      },
      avg_utilization: { $avg: '$utilization_percent' },
      max_utilization: { $max: '$utilization_percent' },
      min_utilization: { $min: '$utilization_percent' },
      count: { $sum: 1 }
    }
  }
]);

db.createView('memory_summary', 'memory_metrics', [
  {
    $group: {
      _id: {
        lpar: '$lpar',
        memory_type: '$memory_type',
        hour: { $hour: '$timestamp' }
      },
      avg_usage: { $avg: '$usage_bytes' },
      max_usage: { $max: '$usage_bytes' },
      min_usage: { $min: '$usage_bytes' },
      count: { $sum: 1 }
    }
  }
]);

print('Database initialization completed successfully!');
print('Created user: rmf_user');
print('Database: rmf_monitoring');
print('Collections created with indexes and TTL');
