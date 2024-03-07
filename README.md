# smart-city-realtime-data-Engineering

This project aims to track details from one point (London) to another point (Birmingham) by generating data for specific topics using Apache Kafka. The generated data includes information related to emergencies, GPS coordinates, traffic conditions, vehicle details, and weather updates.

## Prerequisites / Technology Used
- **macOS**: [Install Docker Desktop](https://docs.docker.com/desktop/).
- Programming Language - Python
- Apache Kafka
- Apache Spark
- Amazon Web Services (AWS)
  - S3
  - Glue
  - Crawler
  - Athena
- Postgres SQL
- Tableau
- Datagrip

## Getting Started
### Architecture
![](assets/architecture.png)

### Kafka Topics
- "emergency_data"
- "gps_data"
- "traffic_data"
- "vehicle_data"
- "weather_data"
### Data Generation
- Data for the specified topics is generated at each timestamp.
- The data is encapsulated into JSON objects and sent to a Kafka producer.

![](assets/data_generation.png)

### Data Processing
- Kafka partitions and distributes the data based on topics.
- Apache Zookeeper manages the coordination between producers and consumers.

![](assets/kafkaDataProducer.png)

### Data Processing with Spark
- Utilizes Apache Spark for data processing.
- Two Spark workers are employed to process the data.

![](assets/sparkDataProcessing.png)

### Storage
- Processed data is stored in an S3 bucket.

![](assets/S3BucketData.png)

### Data Pipeline
- Crawlers are used to extract data from S3 and feed it into AWS Glue.

![](assets/DatabaseGlue.png)

### Data Cleaning For Visualization
- Python scripts are utilized to scrape data from Athena.
![](assets/extractdatafromAthen.png)
- Data is then cleaned and converted into a PostgreSQL table
```sql
DROP TABLE IF EXISTS route_information;

CREATE TABLE route_information AS
SELECT 
    to_timestamp(v.timestamp, 'YYYY-MM-DD HH24:MI:SS.US') AS timestamp,
    CASE
        WHEN v.location ~ '^\[\d+(\.\d+)?,\s*-?\d+(\.\d+)?\]$'
        THEN split_part(trim(']' from trim('[' from v.location)), ',', 1)::numeric
        ELSE NULL
    END AS latitude,
    CASE
        WHEN v.location ~ '^\[\d+(\.\d+)?,\s*-?\d+(\.\d+)?\]$'
        THEN split_part(trim(']' from trim('[' from v.location)), ',', 2)::numeric
        ELSE NULL
    END AS longitude,
    CASE
        WHEN v.speed ~ '^\d+(\.\d+)?$'
        THEN v.speed::double precision
        ELSE NULL
    END AS speed,
    v.direction AS direction,
    e.type AS incident_type,
    e.status AS incident_status,
    w.weathercondition AS weather_condition
FROM
    vehicle_data v
LEFT JOIN
    emergency_data e ON v.timestamp = e.timestamp AND v.location = e.location
LEFT JOIN
    weather_data w ON v.timestamp = w.timestamp AND v.location = w.location;



SELECT * FROM route_information
ORDER BY timestamp;
```

### Visualization
- Connected the postgresSQL to Tableau as Data Source
![](assets/tableau.png)
- Dashboard
![](assets/visualization.png)

### Commands
- Bucket Policy
```bash
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:PutObjectAcl"
            ],
            "Resource": "arn:aws:s3:::smart-city-streaming-data-aditsvet/*"
        }
    ]
}
```
- Delete/List topics from Kafka
```bash 
kafka-topics --delete --topic emergency_data --bootstrap-server broker:29092
kafka-topics --delete --topic gps_data --bootstrap-server broker:29092
kafka-topics --delete --topic weather_data --bootstrap-server broker:29092
kafka-topics --delete --topic traffic_data --bootstrap-server broker:29092
kafka-topics --delete --topic vehicle_data --bootstrap-server broker:29092
kafka-topics --list --bootstrap-server broker:29092
```
- Docker execution command
```bash
docker exec -it smart-city-realtime-spark-master-1 spark-submit \
--master spark://spark-master:7077 \
--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.6,\
com.amazonaws:aws-java-sdk:1.11.469 \
jobs/spark-city.py
```
- How to exclude folder not to get crawled
```bash
_spark_metadata
_spark_metadata/**
**/_spark_metadata
**spark_metadata**
```

