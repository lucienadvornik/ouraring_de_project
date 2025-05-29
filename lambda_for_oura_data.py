#Libraries
import json
import boto3
import requests
from datetime import date

# API configuration
API_TOKEN = "UEJ5GU7KMOFISZHYQOPVLQOLFQOQ2VDR"  
BASE_URL = "https://api.ouraring.com/v2/usercollection"
HEADERS = {"Authorization": f"Bearer {API_TOKEN}"}

# S3
s3 = boto3.client("s3")
BUCKET = "s3-for-oura-data"

# Today's date
TODAY = date.today().isoformat()

# Fetch data from Oura API
def fetch_oura(endpoint):
    url = f"{BASE_URL}/{endpoint}?start_date={TODAY}&end_date={TODAY}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()

# Main script
def lambda_handler(event, context):
    for data_type in ["sleep", "readiness"]:
        data = fetch_oura(f"daily_{data_type}")
        key = f"raw/{TODAY}/{data_type}.json"
        s3.put_object(
            Bucket=BUCKET,
            Key=key,
            Body=json.dumps(data),
            ContentType="application/json"
        )
    return {"status": "OK", "date": TODAY}
