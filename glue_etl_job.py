import sys
from datetime import datetime, timedelta
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame

# Init Spark/Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session

# === CONFIG ===
bucket = "s3-for-oura-data"
raw_path = f"s3://{bucket}/raw/"
processed_path = f"s3://{bucket}/processed/sleep/"

# Set date (Europe/Prague logic – shift UTC by +2 hours)
today = (datetime.utcnow() + timedelta(hours=2)).date().isoformat()

# Input path for the specific day
input_file = f"{raw_path}{today}/sleep.json"

# === LOAD JSON ===
df = spark.read.json(input_file)

# Add 'date' column if not already present (for partitioning)
df = df.withColumn("date", df["day"])  # or use lit(today) if 'day' is missing

# Convert to Glue DynamicFrame
dyf = DynamicFrame.fromDF(df, glueContext, "dyf")

# === SAVE AS PARQUET ===
glueContext.write_dynamic_frame.from_options(
    frame=dyf,
    connection_type="s3",
    connection_options={
        "path": processed_path,
        "partitionKeys": ["date"]
    },
    format="parquet"
)
