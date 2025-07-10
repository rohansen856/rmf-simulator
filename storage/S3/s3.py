import boto3
from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
import json
import gzip
import pickle
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import os
from contextlib import contextmanager
import io
import pandas as pd
from utils.logger import logger

@dataclass
class S3Config:
    endpoint_url: str = os.getenv('S3_ENDPOINT_URL', 'http://localhost:9000')
    access_key: str = os.getenv('S3_ACCESS_KEY', 'minioadmin')
    secret_key: str = os.getenv('S3_SECRET_KEY', 'minioadmin')
    bucket_name: str = os.getenv('S3_BUCKET_NAME', 'rmf-metrics')
    region_name: str = os.getenv('S3_REGION', 'us-east-1')
    use_ssl: bool = os.getenv('S3_USE_SSL', 'false').lower() == 'true'
    signature_version: str = os.getenv('S3_SIGNATURE_VERSION', 's3v4')

class S3StorageService:
    def __init__(self, config: S3Config = None):
        self.config = config or S3Config()
        self.s3_client = None
        self.s3_resource = None
        self.bucket = None
        self.initialize_storage()
    
    def _create_s3_clients(self):
        """Create S3 client and resource"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config.access_key,
                aws_secret_access_key=self.config.secret_key,
                region_name=self.config.region_name
            )
            
            client_config = {
                'endpoint_url': self.config.endpoint_url,
                'use_ssl': self.config.use_ssl,
                'config': boto3.session.Config(
                    signature_version=self.config.signature_version,
                    retries={'max_attempts': 3, 'mode': 'adaptive'}
                )
            }
            
            self.s3_client = session.client('s3', **client_config)
            self.s3_resource = session.resource('s3', **client_config)
            
            # Test connection
            self.s3_client.head_bucket(Bucket=self.config.bucket_name)
            
            logger.info(f"Successfully connected to S3-compatible storage: {self.config.endpoint_url}")
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, but connection is working
                logger.info(f"Connected to S3-compatible storage: {self.config.endpoint_url}")
            else:
                logger.error(f"S3 ClientError: {e}")
                raise
        except NoCredentialsError:
            logger.error("S3 credentials not found or invalid")
            raise
        except EndpointConnectionError as e:
            logger.error(f"Failed to connect to S3 endpoint: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to S3: {e}")
            raise
    
    def initialize_storage(self):
        """Initialize S3 connection and create bucket if necessary"""
        try:
            self._create_s3_clients()
            self._ensure_bucket_exists()
            self._setup_bucket_lifecycle()
            logger.info("S3 storage initialization completed successfully")
            
        except Exception as e:
            logger.error(f"S3 storage initialization failed: {e}")
            raise
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.s3_client.head_bucket(Bucket=self.config.bucket_name)
            logger.info(f"Bucket '{self.config.bucket_name}' already exists")
            
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.config.region_name == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.config.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.config.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.config.region_name}
                        )
                    
                    # Set bucket versioning
                    self.s3_client.put_bucket_versioning(
                        Bucket=self.config.bucket_name,
                        VersioningConfiguration={'Status': 'Enabled'}
                    )
                    
                    logger.info(f"Created bucket '{self.config.bucket_name}' with versioning enabled")
                    
                except ClientError as create_error:
                    logger.error(f"Failed to create bucket: {create_error}")
                    raise
            else:
                logger.error(f"Error checking bucket: {e}")
                raise
        
        # Get bucket reference
        self.bucket = self.s3_resource.Bucket(self.config.bucket_name)
    
    def _setup_bucket_lifecycle(self):
        """Setup lifecycle policy for automatic cleanup of old data"""
        try:
            lifecycle_config = {
                'Rules': [
                    {
                        'ID': 'RMFMetricsRetention',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'metrics/'},
                        'Expiration': {'Days': 90},
                        'NoncurrentVersionExpiration': {'NoncurrentDays': 30}
                    },
                    {
                        'ID': 'RMFArchiveRetention',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': 'archive/'},
                        'Transitions': [
                            {
                                'Days': 30,
                                'StorageClass': 'GLACIER'
                            }
                        ],
                        'Expiration': {'Days': 2555}  # 7 years
                    }
                ]
            }
            
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.config.bucket_name,
                LifecycleConfiguration=lifecycle_config
            )
            
            logger.info("Bucket lifecycle policy configured successfully")
            
        except ClientError as e:
            # MinIO might not support lifecycle policies
            logger.warning(f"Could not set lifecycle policy (might not be supported): {e}")
    
    def _generate_object_key(self, metric_type: str, timestamp: datetime, 
                           sysplex: str, lpar: str, additional_info: str = "") -> str:
        """Generate S3 object key with proper partitioning"""
        date_part = timestamp.strftime("%Y/%m/%d/%H")
        
        if additional_info:
            return f"metrics/{metric_type}/{sysplex}/{lpar}/{date_part}/{additional_info}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json.gz"
        else:
            return f"metrics/{metric_type}/{sysplex}/{lpar}/{date_part}/{timestamp.strftime('%Y%m%d_%H%M%S')}.json.gz"
    
    def _compress_data(self, data: Union[Dict, List]) -> bytes:
        """Compress data using gzip"""
        json_data = json.dumps(data, default=str, ensure_ascii=False)
        return gzip.compress(json_data.encode('utf-8'))
    
    def _decompress_data(self, compressed_data: bytes) -> Union[Dict, List]:
        """Decompress gzipped data"""
        json_data = gzip.decompress(compressed_data).decode('utf-8')
        return json.loads(json_data)
    
    def store_cpu_metric(self, timestamp: datetime, sysplex: str, lpar: str, 
                        cpu_type: str, utilization_percent: float):
        """Store CPU utilization metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'cpu_type': cpu_type,
                'utilization_percent': utilization_percent,
                'metric_type': 'cpu_utilization'
            }
            
            object_key = self._generate_object_key('cpu', timestamp, sysplex, lpar, cpu_type)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'cpu_utilization',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'cpu-type': cpu_type
                }
            )
            
            logger.debug(f"Stored CPU metric: {object_key}")
            
        except Exception as e:
            logger.error(f"Error storing CPU metric to S3: {e}")
            raise
    
    def store_memory_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                          memory_type: str, usage_bytes: int):
        """Store memory usage metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'memory_type': memory_type,
                'usage_bytes': usage_bytes,
                'metric_type': 'memory_usage'
            }
            
            object_key = self._generate_object_key('memory', timestamp, sysplex, lpar, memory_type)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'memory_usage',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'memory-type': memory_type
                }
            )
            
            logger.debug(f"Stored memory metric: {object_key}")
            
        except Exception as e:
            logger.error(f"Error storing memory metric to S3: {e}")
            raise
    
    def store_ldev_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    device_id: str, utilization_percent: float):
        """Store LDEV utilization metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'device_id': device_id,
                'utilization_percent': utilization_percent,
                'metric_type': 'ldev_utilization'
            }
            
            object_key = self._generate_object_key('ldev_utilization', timestamp, sysplex, lpar, device_id)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'ldev_utilization',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'device-id': device_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing LDEV utilization metric to S3: {e}")
            raise
    
    def store_ldev_response_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                      device_type: str, response_time_seconds: float):
        """Store LDEV response time metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'device_type': device_type,
                'response_time_seconds': response_time_seconds,
                'metric_type': 'ldev_response_time'
            }
            
            object_key = self._generate_object_key('ldev_response_time', timestamp, sysplex, lpar, device_type)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'ldev_response_time',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'device-type': device_type
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing LDEV response time metric to S3: {e}")
            raise
    
    def store_clpr_service_time_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     cf_link: str, service_time_microseconds: float):
        """Store CLPR service time metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'cf_link': cf_link,
                'service_time_microseconds': service_time_microseconds,
                'metric_type': 'clpr_service_time'
            }
            
            object_key = self._generate_object_key('clpr_service_time', timestamp, sysplex, lpar, cf_link)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'clpr_service_time',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'cf-link': cf_link
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing CLPR service time metric to S3: {e}")
            raise
    
    def store_clpr_request_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     cf_link: str, request_type: str, request_rate: float):
        """Store CLPR request rate metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'cf_link': cf_link,
                'request_type': request_type,
                'request_rate': request_rate,
                'metric_type': 'clpr_request_rate'
            }
            
            object_key = self._generate_object_key('clpr_request_rate', timestamp, sysplex, lpar, f"{cf_link}_{request_type}")
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'clpr_request_rate',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'cf-link': cf_link,
                    'request-type': request_type
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing CLPR request rate metric to S3: {e}")
            raise
    
    def store_mpb_processing_rate_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       queue_type: str, processing_rate: float):
        """Store MPB processing rate metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'queue_type': queue_type,
                'processing_rate': processing_rate,
                'metric_type': 'mpb_processing_rate'
            }
            
            object_key = self._generate_object_key('mpb_processing_rate', timestamp, sysplex, lpar, queue_type)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'mpb_processing_rate',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'queue-type': queue_type
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing MPB processing rate metric to S3: {e}")
            raise
    
    def store_mpb_queue_depth_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                   queue_type: str, queue_depth: int):
        """Store MPB queue depth metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'queue_type': queue_type,
                'queue_depth': queue_depth,
                'metric_type': 'mpb_queue_depth'
            }
            
            object_key = self._generate_object_key('mpb_queue_depth', timestamp, sysplex, lpar, queue_type)
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'mpb_queue_depth',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'queue-type': queue_type
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing MPB queue depth metric to S3: {e}")
            raise
    
    def store_ports_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                     port_type: str, port_id: str, utilization_percent: float):
        """Store ports utilization metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'port_type': port_type,
                'port_id': port_id,
                'utilization_percent': utilization_percent,
                'metric_type': 'ports_utilization'
            }
            
            object_key = self._generate_object_key('ports_utilization', timestamp, sysplex, lpar, f"{port_type}_{port_id}")
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'ports_utilization',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'port-type': port_type,
                    'port-id': port_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing ports utilization metric to S3: {e}")
            raise
    
    def store_ports_throughput_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                    port_type: str, port_id: str, throughput_mbps: float):
        """Store ports throughput metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'port_type': port_type,
                'port_id': port_id,
                'throughput_mbps': throughput_mbps,
                'metric_type': 'ports_throughput'
            }
            
            object_key = self._generate_object_key('ports_throughput', timestamp, sysplex, lpar, f"{port_type}_{port_id}")
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'ports_throughput',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'port-type': port_type,
                    'port-id': port_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing ports throughput metric to S3: {e}")
            raise
    
    def store_volumes_utilization_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                       volume_type: str, volume_id: str, utilization_percent: float):
        """Store volumes utilization metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'volume_type': volume_type,
                'volume_id': volume_id,
                'utilization_percent': utilization_percent,
                'metric_type': 'volumes_utilization'
            }
            
            object_key = self._generate_object_key('volumes_utilization', timestamp, sysplex, lpar, f"{volume_type}_{volume_id}")
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'volumes_utilization',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'volume-type': volume_type,
                    'volume-id': volume_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing volumes utilization metric to S3: {e}")
            raise
    
    def store_volumes_iops_metric(self, timestamp: datetime, sysplex: str, lpar: str,
                                volume_type: str, volume_id: str, iops: int):
        """Store volumes IOPS metric in S3"""
        try:
            data = {
                'timestamp': timestamp.isoformat(),
                'sysplex': sysplex,
                'lpar': lpar,
                'volume_type': volume_type,
                'volume_id': volume_id,
                'iops': iops,
                'metric_type': 'volumes_iops'
            }
            
            object_key = self._generate_object_key('volumes_iops', timestamp, sysplex, lpar, f"{volume_type}_{volume_id}")
            compressed_data = self._compress_data(data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=object_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                Metadata={
                    'metric-type': 'volumes_iops',
                    'sysplex': sysplex,
                    'lpar': lpar,
                    'volume-type': volume_type,
                    'volume-id': volume_id
                }
            )
            
        except Exception as e:
            logger.error(f"Error storing volumes IOPS metric to S3: {e}")
            raise
    
    def batch_store_metrics(self, metrics_batch: List[Dict[str, Any]]):
        """Store multiple metrics in a single batch operation"""
        try:
            batch_timestamp = datetime.now()
            batch_id = batch_timestamp.strftime('%Y%m%d_%H%M%S_%f')
            
            # Group metrics by type and LPAR for efficient storage
            grouped_metrics = {}
            for metric in metrics_batch:
                key = f"{metric['metric_type']}_{metric['sysplex']}_{metric['lpar']}"
                if key not in grouped_metrics:
                    grouped_metrics[key] = []
                grouped_metrics[key].append(metric)
            
            # Store each group as a separate object
            for group_key, group_metrics in grouped_metrics.items():
                metric_type, sysplex, lpar = group_key.split('_', 2)
                
                object_key = f"metrics/batch/{metric_type}/{sysplex}/{lpar}/{batch_timestamp.strftime('%Y/%m/%d/%H')}/batch_{batch_id}.json.gz"
                compressed_data = self._compress_data(group_metrics)
                
                self.s3_client.put_object(
                    Bucket=self.config.bucket_name,
                    Key=object_key,
                    Body=compressed_data,
                    ContentType='application/json',
                    ContentEncoding='gzip',
                    Metadata={
                        'batch-id': batch_id,
                        'metric-type': metric_type,
                        'sysplex': sysplex,
                        'lpar': lpar,
                        'metrics-count': str(len(group_metrics))
                    }
                )
                
                logger.debug(f"Stored batch of {len(group_metrics)} metrics: {object_key}")
            
        except Exception as e:
            logger.error(f"Error storing metrics batch to S3: {e}")
            raise
    
    def retrieve_metrics(self, metric_type: str, sysplex: str = None, lpar: str = None,
                        start_time: datetime = None, end_time: datetime = None,
                        limit: int = 1000) -> List[Dict]:
        """Retrieve metrics from S3 based on filters"""
        try:
            # Build prefix for S3 listing
            prefix = f"metrics/{metric_type}/"
            if sysplex:
                prefix += f"{sysplex}/"
                if lpar:
                    prefix += f"{lpar}/"
            
            # List objects
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.config.bucket_name,
                Prefix=prefix,
                MaxKeys=limit
            )
            
            metrics = []
            for page in page_iterator:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    # Check if object falls within time range
                    if start_time or end_time:
                        obj_timestamp = self._extract_timestamp_from_key(obj['Key'])
                        if obj_timestamp:
                            if start_time and obj_timestamp < start_time:
                                continue
                            if end_time and obj_timestamp > end_time:
                                continue
                    
                    # Retrieve and decompress object
                    try:
                        response = self.s3_client.get_object(
                            Bucket=self.config.bucket_name,
                            Key=obj['Key']
                        )
                        
                        compressed_data = response['Body'].read()
                        metric_data = self._decompress_data(compressed_data)
                        
                        if isinstance(metric_data, list):
                            metrics.extend(metric_data)
                        else:
                            metrics.append(metric_data)
                            
                        if len(metrics) >= limit:
                            break
                            
                    except Exception as e:
                        logger.error(f"Error retrieving object {obj['Key']}: {e}")
                        continue
                
                if len(metrics) >= limit:
                    break
            
            return metrics[:limit]
            
        except Exception as e:
            logger.error(f"Error retrieving metrics from S3: {e}")
            return []
    
    def _extract_timestamp_from_key(self, object_key: str) -> Optional[datetime]:
        """Extract timestamp from S3 object key"""
        try:
            # Extract timestamp from key pattern: .../YYYYMMDD_HHMMSS.json.gz
            parts = object_key.split('/')
            if len(parts) >= 1:
                filename = parts[-1].replace('.json.gz', '')
                if '_' in filename:
                    timestamp_str = filename.split('_')[-2] + '_' + filename.split('_')[-1]
                    return datetime.strptime(timestamp_str, '%Y%m%d_%H%M%S')
            return None
            
        except Exception:
            return None
    
    def export_metrics_to_csv(self, metric_type: str, output_path: str,
                            sysplex: str = None, lpar: str = None,
                            start_time: datetime = None, end_time: datetime = None) -> str:
        """Export metrics to CSV file"""
        try:
            metrics = self.retrieve_metrics(
                metric_type=metric_type,
                sysplex=sysplex,
                lpar=lpar,
                start_time=start_time,
                end_time=end_time,
                limit=100000
            )
            
            if not metrics:
                logger.warning(f"No metrics found for export: {metric_type}")
                return None
            
            # Convert to DataFrame and save as CSV
            df = pd.DataFrame(metrics)
            
            # Generate output filename if not provided
            if not output_path:
                timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
                output_path = f"/tmp/rmf_export_{metric_type}_{timestamp_str}.csv"
            
            df.to_csv(output_path, index=False)
            
            # Upload CSV back to S3
            csv_key = f"exports/{metric_type}/export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            with open(output_path, 'rb') as csv_file:
                self.s3_client.put_object(
                    Bucket=self.config.bucket_name,
                    Key=csv_key,
                    Body=csv_file,
                    ContentType='text/csv',
                    Metadata={
                        'export-type': metric_type,
                        'record-count': str(len(metrics)),
                        'export-timestamp': datetime.now().isoformat()
                    }
                )
            
            logger.info(f"Exported {len(metrics)} metrics to {output_path} and uploaded to S3: {csv_key}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting metrics to CSV: {e}")
            return None
    
    def create_archive(self, start_date: datetime, end_date: datetime) -> str:
        """Create an archive of metrics for a date range"""
        try:
            archive_id = f"archive_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}"
            
            # Collect all metrics for the date range
            metric_types = [
                'cpu', 'memory', 'ldev_utilization', 'ldev_response_time',
                'clpr_service_time', 'clpr_request_rate', 'mpb_processing_rate',
                'mpb_queue_depth', 'ports_utilization', 'ports_throughput',
                'volumes_utilization', 'volumes_iops'
            ]
            
            archive_data = {}
            for metric_type in metric_types:
                metrics = self.retrieve_metrics(
                    metric_type=metric_type,
                    start_time=start_date,
                    end_time=end_date,
                    limit=1000000
                )
                if metrics:
                    archive_data[metric_type] = metrics
            
            if not archive_data:
                logger.warning(f"No data found for archive period: {start_date} to {end_date}")
                return None
            
            # Create archive object
            archive_key = f"archive/{archive_id}.json.gz"
            compressed_data = self._compress_data(archive_data)
            
            self.s3_client.put_object(
                Bucket=self.config.bucket_name,
                Key=archive_key,
                Body=compressed_data,
                ContentType='application/json',
                ContentEncoding='gzip',
                StorageClass='GLACIER',  # Use cheaper storage for archives
                Metadata={
                    'archive-id': archive_id,
                    'start-date': start_date.isoformat(),
                    'end-date': end_date.isoformat(),
                    'metric-types': ','.join(archive_data.keys()),
                    'total-records': str(sum(len(data) for data in archive_data.values()))
                }
            )
            
            logger.info(f"Created archive: {archive_key}")
            return archive_key
            
        except Exception as e:
            logger.error(f"Error creating archive: {e}")
            return None
    
    def cleanup_old_data(self, days_to_keep: int = 90):
        """Clean up old data beyond retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            # List objects older than cutoff date
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.config.bucket_name,
                Prefix='metrics/'
            )
            
            objects_to_delete = []
            for page in page_iterator:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    if obj['LastModified'].replace(tzinfo=None) < cutoff_date:
                        objects_to_delete.append({'Key': obj['Key']})
                    
                    # Process in batches of 1000 (S3 delete limit)
                    if len(objects_to_delete) >= 1000:
                        self._delete_objects_batch(objects_to_delete)
                        objects_to_delete = []
            
            # Delete remaining objects
            if objects_to_delete:
                self._delete_objects_batch(objects_to_delete)
            
            logger.info(f"Cleaned up old S3 objects older than {days_to_keep} days")
            
        except Exception as e:
            logger.error(f"Error cleaning up old S3 data: {e}")
    
    def _delete_objects_batch(self, objects_to_delete: List[Dict]):
        """Delete a batch of S3 objects"""
        try:
            response = self.s3_client.delete_objects(
                Bucket=self.config.bucket_name,
                Delete={
                    'Objects': objects_to_delete,
                    'Quiet': True
                }
            )
            
            deleted_count = len(objects_to_delete)
            if 'Errors' in response:
                deleted_count -= len(response['Errors'])
                for error in response['Errors']:
                    logger.error(f"Failed to delete {error['Key']}: {error['Message']}")
            
            logger.debug(f"Successfully deleted {deleted_count} objects")
            
        except Exception as e:
            logger.error(f"Error deleting objects batch: {e}")
    
    def get_storage_statistics(self) -> Dict:
        """Get storage usage statistics"""
        try:
            # List all objects to calculate statistics
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(Bucket=self.config.bucket_name)
            
            stats = {
                'total_objects': 0,
                'total_size_bytes': 0,
                'metrics_objects': 0,
                'metrics_size_bytes': 0,
                'archive_objects': 0,
                'archive_size_bytes': 0,
                'export_objects': 0,
                'export_size_bytes': 0,
                'oldest_object': None,
                'newest_object': None
            }
            
            for page in page_iterator:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    stats['total_objects'] += 1
                    stats['total_size_bytes'] += obj['Size']
                    
                    # Update oldest/newest
                    obj_date = obj['LastModified'].replace(tzinfo=None)
                    if not stats['oldest_object'] or obj_date < stats['oldest_object']:
                        stats['oldest_object'] = obj_date
                    if not stats['newest_object'] or obj_date > stats['newest_object']:
                        stats['newest_object'] = obj_date
                    
                    # Categorize by prefix
                    if obj['Key'].startswith('metrics/'):
                        stats['metrics_objects'] += 1
                        stats['metrics_size_bytes'] += obj['Size']
                    elif obj['Key'].startswith('archive/'):
                        stats['archive_objects'] += 1
                        stats['archive_size_bytes'] += obj['Size']
                    elif obj['Key'].startswith('exports/'):
                        stats['export_objects'] += 1
                        stats['export_size_bytes'] += obj['Size']
            
            # Convert bytes to human readable format
            stats['total_size_mb'] = round(stats['total_size_bytes'] / (1024 * 1024), 2)
            stats['metrics_size_mb'] = round(stats['metrics_size_bytes'] / (1024 * 1024), 2)
            stats['archive_size_mb'] = round(stats['archive_size_bytes'] / (1024 * 1024), 2)
            stats['export_size_mb'] = round(stats['export_size_bytes'] / (1024 * 1024), 2)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage statistics: {e}")
            return {}
    
    def get_connection_status(self) -> Dict:
        """Get S3 connection status and bucket information"""
        try:
            # Test connection by listing bucket
            response = self.s3_client.head_bucket(Bucket=self.config.bucket_name)
            
            # Get bucket location
            try:
                location_response = self.s3_client.get_bucket_location(Bucket=self.config.bucket_name)
                bucket_region = location_response.get('LocationConstraint', 'us-east-1')
            except:
                bucket_region = 'unknown'
            
            # Get bucket versioning status
            try:
                versioning_response = self.s3_client.get_bucket_versioning(Bucket=self.config.bucket_name)
                versioning_status = versioning_response.get('Status', 'Disabled')
            except:
                versioning_status = 'unknown'
            
            status = {
                'connected': True,
                'endpoint_url': self.config.endpoint_url,
                'bucket_name': self.config.bucket_name,
                'bucket_region': bucket_region,
                'versioning_enabled': versioning_status == 'Enabled',
                'use_ssl': self.config.use_ssl,
                'access_key': self.config.access_key[:8] + '...' if self.config.access_key else None
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting S3 connection status: {e}")
            return {
                'connected': False,
                'error': str(e),
                'endpoint_url': self.config.endpoint_url,
                'bucket_name': self.config.bucket_name
            }
    
    def create_backup(self, backup_prefix: str = None) -> str:
        """Create a backup by copying all current data to a backup prefix"""
        try:
            if not backup_prefix:
                backup_prefix = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # List all objects in metrics/ prefix
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.config.bucket_name,
                Prefix='metrics/'
            )
            
            copied_objects = 0
            for page in page_iterator:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    source_key = obj['Key']
                    backup_key = f"{backup_prefix}/{source_key}"
                    
                    # Copy object
                    copy_source = {
                        'Bucket': self.config.bucket_name,
                        'Key': source_key
                    }
                    
                    self.s3_client.copy_object(
                        CopySource=copy_source,
                        Bucket=self.config.bucket_name,
                        Key=backup_key,
                        MetadataDirective='COPY'
                    )
                    
                    copied_objects += 1
                    
                    if copied_objects % 100 == 0:
                        logger.info(f"Copied {copied_objects} objects to backup")
            
            logger.info(f"Backup completed: {backup_prefix} ({copied_objects} objects)")
            return backup_prefix
            
        except Exception as e:
            logger.error(f"Error creating S3 backup: {e}")
            return None
    
    def close_connection(self):
        """Close S3 connections (cleanup)"""
        try:
            # boto3 clients are thread-safe and manage connections automatically
            # No explicit cleanup needed, but we can reset references
            self.s3_client = None
            self.s3_resource = None
            self.bucket = None
            logger.info("S3 storage service connections closed")
            
        except Exception as e:
            logger.error(f"Error closing S3 connections: {e}")

# Example usage and testing
if __name__ == "__main__":
    # Initialize the service
    s3_service = S3StorageService()
    
    # Test connection
    status = s3_service.get_connection_status()
    print(f"S3 Connection status: {status}")
    
    # Insert sample data
    timestamp = datetime.now()
    s3_service.store_cpu_metric(timestamp, "SYSPLEX01", "PROD01", "general_purpose", 75.5)
    s3_service.store_memory_metric(timestamp, "SYSPLEX01", "PROD01", "real_storage", 1073741824)
    
    # Get statistics
    stats = s3_service.get_storage_statistics()
    print(f"Storage statistics: {stats}")
    
    # Close connection
    s3_service.close_connection()