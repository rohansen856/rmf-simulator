# RMF Simulator Documentation

## Overview

The MainframeSimulator class is a comprehensive z/OS Resource Measurement Facility (RMF) simulator that generates realistic mainframe performance metrics. It simulates various system components including CPU, memory, storage devices, coupling facilities, message processing, network ports, and volumes across multiple LPARs (Logical Partitions) in a sysplex environment.

## Architecture

### Core Components

- **MainframeSimulator**: Main simulation engine
- **Storage Services**: MySQL, MongoDB, and S3 for metric persistence
- **LPAR Configurations**: Multiple logical partition configurations
- **Metric Definitions**: Prometheus-style metrics for monitoring

### Storage Architecture

The simulator supports three storage backends:
- **MySQL**: Relational database for structured metric storage
- **MongoDB**: NoSQL database for flexible document-based storage
- **S3**: Object storage with batched writes for scalability

## Initialization Process

### Baseline Establishment

The simulator initializes realistic baseline values for each LPAR:

```python
self.base_values[lpar.name] = {
    'cpu_base': 45.0 if lpar.workload_type == "online" else 25.0,
    'memory_base': 0.75,  # 75% base utilization
    'io_base': 15.0,      # 15ms base response time
    'cf_base': 25.0,      # 25 microseconds base service time
}
```

### Trend Factors

Cyclical patterns are established to simulate realistic workload variations:
- **Daily Cycle**: 0.8-1.2x multiplier
- **Weekly Cycle**: 0.9-1.1x multiplier  
- **Monthly Cycle**: 0.95-1.05x multiplier

## Time-Based Performance Factors

### Peak Hours Detection

The simulator calculates time-based performance factors considering:

- **Peak Hours**: Defined per LPAR configuration
  - Online workloads: 1.4x multiplier during peak
  - Batch workloads: 1.8x multiplier during peak
  - Batch off-peak: 0.3x multiplier

- **Weekly Patterns**: Monday gets 1.2x multiplier (higher load)
- **Monthly Patterns**: Month-end (days 28-31) gets 1.5x multiplier
- **Random Noise**: ±10% variation for realistic fluctuation

## Metric Simulation Details

### 1. CPU Metrics

**Simulated Components:**
- General Purpose processors
- zIIP (z/OS Integrated Information Processor)
- zAAP (z/OS Application Assist Processor)

**Calculation Logic:**
```python
gp_util = min(95.0, base_util * time_factor)
ziip_util = min(75.0, gp_util * 0.6)
zaap_util = min(70.0, gp_util * 0.4)
```

**Characteristics:**
- GP utilization capped at 95%
- zIIP typically 60% of GP utilization
- zAAP typically 40% of GP utilization

### 2. Memory Metrics

**Simulated Components:**
- Real Storage
- Virtual Storage  
- Common Service Area (CSA)

**Calculation Logic:**
- Real storage: Base utilization × time factor (max 90%)
- Virtual storage: 4-6x real storage depending on workload type
- CSA: Random 200-800MB allocation

**Storage Types:**
- Online workloads: 4x virtual storage multiplier
- Batch workloads: 6x virtual storage multiplier

### 3. LDEV (Storage Device) Metrics

**Device Types Simulated:**
- **3390 DASD**: 20 devices, 8ms base response, 40% base utilization
- **FlashCopy**: 8 devices, 2ms base response, 55% base utilization  
- **Tape**: 12 devices, 45ms base response, 25% base utilization

**Metrics Generated:**
- Response time (1-100ms range)
- Device utilization (5-95% range)

### 4. CLPR (Coupling Facility Link Performance) Metrics

**Simulated Components:**
- 4 CF links per LPAR (CF01-CF04)
- Service time measurements
- Request rate tracking

**Metrics:**
- **Service Time**: 5-200 microseconds
- **Request Rates**:
  - Synchronous: 1,000-10,000 requests/sec
  - Asynchronous: 500-3,000 requests/sec

### 5. MPB (Message Processing Block) Metrics

**Queue Types:**
- **CICS**: 5,000 base processing rate
- **IMS**: 3,000 base processing rate
- **MQ**: 2,000 base processing rate
- **BATCH**: 500 base processing rate

**Metrics:**
- Processing rate (messages/second)
- Queue depth (derived from processing rate)

### 6. Port Metrics

**Port Types:**
- **OSA**: 4 ports, 1Gbps max, 35% base utilization
- **Hipersocket**: 2 ports, 10Gbps max, 15% base utilization
- **FICON**: 8 ports, 400Mbps max, 45% base utilization

**Metrics:**
- Port utilization (5-85%)
- Throughput (derived from utilization)

### 7. Volume Metrics

**Volume Types:**
- **SYSRES**: 2 volumes, 60% base util, 1,500 base IOPS
- **WORK**: 15 volumes, 45% base util, 800 base IOPS
- **USER**: 25 volumes, 35% base util, 600 base IOPS
- **TEMP**: 8 volumes, 25% base util, 400 base IOPS

**Metrics:**
- Volume utilization (10-90%)
- IOPS (Input/Output Operations Per Second)

## Storage and Persistence

### Multi-Storage Strategy

Each metric is persisted to multiple storage systems:

1. **Prometheus Metrics**: For real-time monitoring
2. **MySQL**: Structured relational storage
3. **MongoDB**: Document-based NoSQL storage
4. **S3**: Batched object storage for analytics

### S3 Batching Strategy

- **Batch Size**: 50 metrics per batch
- **Time-based Flush**: Every 60 seconds
- **Format**: JSON documents with ISO timestamps

### Error Handling

The simulator implements robust error handling:
- Continues operation if individual storage systems fail
- Logs errors without stopping simulation
- Graceful degradation when services are unavailable

## Performance Characteristics

### Realistic Simulation Features

1. **Time-of-Day Variation**: Peak/off-peak patterns
2. **Workload Type Differentiation**: Online vs. batch behaviors
3. **Correlated Metrics**: Related metrics move together realistically
4. **Bounded Ranges**: All metrics have realistic min/max values
5. **Random Variation**: Includes realistic noise and fluctuation

### Workload Types

- **Online Workloads**: Higher CPU during business hours, more consistent memory usage
- **Batch Workloads**: Higher CPU during batch windows, variable resource consumption

## Configuration and Extensibility

### Environment Variables

- `ENABLE_MYSQL`: Enable/disable MySQL storage
- `ENABLE_MONGO`: Enable/disable MongoDB storage  
- `ENABLE_S3`: Enable/disable S3 storage

### LPAR Configuration

LPARs are configured with:
- Name and workload type
- Memory allocation
- Peak hours definition
- Baseline performance characteristics

## Usage Example

```python
# Initialize simulator with all storage backends
simulator = MainframeSimulator(
    enable_mysql=True,
    enable_mongodb=True, 
    enable_s3=True
)

# Update all metrics for all LPARs
await simulator.update_all_metrics()
```

## Monitoring and Observability

### Prometheus Integration

All metrics are exposed as Prometheus metrics with appropriate labels:
- Sysplex name
- LPAR name  
- Component-specific identifiers
- Metric type classifications

### Logging

Comprehensive logging includes:
- Debug-level metric updates
- Error handling for storage failures
- Batch flush operations
- Service initialization status

## Best Practices

1. **Regular Updates**: Call `update_all_metrics()` at regular intervals
2. **Error Monitoring**: Monitor logs for storage service failures
3. **Capacity Planning**: Monitor S3 batch sizes and flush frequency
4. **Performance Tuning**: Adjust batch sizes based on throughput requirements

# How Values Are Actually Generated - Simple Explanation for Beginners

## The Big Picture

Think of this simulator like a **fake computer system generator**. It pretends to be multiple computer systems running different types of work, and it generates fake performance numbers that look realistic. It's like a flight simulator, but for computer performance data.

## The Core Formula

Almost every number follows this basic pattern:

```
Final Value = Base Value × Time Factor × Random Variation
```

Let me break this down:

## 1. Base Values (Starting Points)

First, the simulator sets up "normal" baseline numbers for each computer system:

```python
# These are the "normal" values when nothing special is happening
base_values = {
    'cpu_base': 45.0,      # CPU normally runs at 45%
    'memory_base': 0.75,   # Memory normally 75% full
    'io_base': 15.0,       # Disk normally takes 15ms to respond
    'cf_base': 25.0,       # Special system communication takes 25μs
}
```

**Think of it like**: If you measured your laptop's CPU usage on a normal Tuesday afternoon, you might see 45% - that's your baseline.

## 2. Time Factor (Making It Realistic)

The simulator makes values change based on time of day, day of week, etc. Here's how:

### Peak Hours Multiplier
```python
if current_hour in peak_hours:
    peak_factor = 1.4  # 40% higher during busy times
else:
    peak_factor = 1.0  # Normal during quiet times
```

### Weekly Pattern
```python
if today_is_monday:
    weekday_factor = 1.2  # 20% higher on Mondays
else:
    weekday_factor = 1.0
```

### Monthly Pattern
```python
if end_of_month:  # Days 28-31
    month_end_factor = 1.5  # 50% higher during month-end
else:
    month_end_factor = 1.0
```

**Think of it like**: Your laptop runs hotter when you're gaming (peak hours), might be slower on Monday mornings (weekly pattern), and gets hammered when you're doing taxes at month-end (monthly pattern).

## 3. Random Variation (Making It Look Real)

Real systems never show perfectly smooth numbers, so the simulator adds randomness:

```python
noise_factor = 1.0 + random.uniform(-0.1, 0.1)  # ±10% random variation
```

**Think of it like**: Even if you do the same task twice, your computer might be 3% faster or slower each time due to background processes, temperature, etc.

## 4. Putting It All Together

Here's how CPU usage gets calculated:

```python
def calculate_cpu_usage():
    base_cpu = 45.0  # Normal CPU usage
    
    # Time-based factors
    time_factor = peak_factor × weekday_factor × month_end_factor × noise_factor
    
    # Final calculation
    cpu_usage = base_cpu × time_factor
    
    # Make sure it's realistic (can't be over 95%)
    cpu_usage = min(95.0, cpu_usage)
    
    return cpu_usage
```

## Real Examples

Let's see this in action:

### Example 1: Normal Tuesday at 2 PM
```python
base_cpu = 45.0
peak_factor = 1.0      # Not peak hours
weekday_factor = 1.0   # Not Monday
month_end_factor = 1.0 # Not month-end
noise_factor = 1.02    # 2% random bump

cpu_usage = 45.0 × 1.0 × 1.0 × 1.0 × 1.02 = 45.9%
```

### Example 2: Monday Morning at 9 AM (Peak Hours)
```python
base_cpu = 45.0
peak_factor = 1.4      # Peak hours!
weekday_factor = 1.2   # Monday effect
month_end_factor = 1.0 # Not month-end
noise_factor = 0.98    # 2% random drop

cpu_usage = 45.0 × 1.4 × 1.2 × 1.0 × 0.98 = 74.1%
```

### Example 3: Month-End Peak Hours
```python
base_cpu = 45.0
peak_factor = 1.4      # Peak hours
weekday_factor = 1.0   # Normal day
month_end_factor = 1.5 # Month-end crunch!
noise_factor = 1.05    # 5% random bump

cpu_usage = 45.0 × 1.4 × 1.0 × 1.5 × 1.05 = 99.2%
# But it gets capped at 95%: cpu_usage = 95.0%
```

## Different Types of Measurements

The simulator generates different types of fake measurements:

### 1. Percentage Values (0-100%)
- **CPU Usage**: How busy the processor is
- **Memory Usage**: How full the memory is
- **Disk Usage**: How busy the storage is

### 2. Response Times (milliseconds)
- **Disk Response**: How long it takes to read/write data
- **Network Response**: How long network requests take

### 3. Rates (operations per second)
- **Transaction Rate**: How many transactions per second
- **Message Rate**: How many messages processed per second

### 4. Sizes (bytes, megabytes, etc.)
- **Memory Allocation**: How much memory is being used
- **Storage Allocation**: How much disk space is used

## The Clever Parts

### 1. Related Values Move Together
If CPU usage is high, memory usage tends to be high too:
```python
memory_usage = base_memory × same_time_factor_as_cpu
```

### 2. Different System Types Act Differently
- **"Online" systems**: Busy during business hours (9-5)
- **"Batch" systems**: Busy at night when big jobs run

### 3. Realistic Limits
Every value has realistic bounds:
- CPU can't go over 95% (systems crash before 100%)
- Memory can't go over 90% (needs breathing room)
- Response times can't go below 1ms (physics limits)

## The Storage Part

Every fake number gets saved to three different databases:
1. **MySQL**: Traditional database (rows and columns)
2. **MongoDB**: Modern database (documents)
3. **S3**: File storage (for big data analysis)

This happens automatically every time a number is generated.

## Why This Works

This approach creates realistic-looking data because:

1. **Base values** are set to normal ranges
2. **Time patterns** match real-world usage
3. **Random variation** makes it look natural
4. **Realistic limits** prevent impossible values
5. **Related metrics** move together logically

## The End Result

You get thousands of realistic performance numbers that look like they came from real computer systems, updated every few seconds, showing natural patterns like:
- Higher usage during business hours
- Spikes at month-end
- Random day-to-day variation
- Realistic relationships between different measurements

It's sophisticated enough to fool monitoring systems and analysis tools into thinking they're looking at real performance data!