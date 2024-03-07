# smart-city-realtime-data-Engineering

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

## Getting Started

### Architecture
![](assets/architecture.png)

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
- How to execute folder not to get crawled
```bash
_spark_metadata
_spark_metadata/**
**/_spark_metadata
**spark_metadata**
```

