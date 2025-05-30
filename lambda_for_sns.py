# Configuration
# - Additional layer: requests library
# - Runtime: Python 3.10, Architecture: x86_64

#Libraries
import boto3
import json
from datetime import datetime, timedelta


# S3
s3 = boto3.client("s3")
sns = boto3.client("sns")
BUCKET = "s3-for-oura-data"

# Configuration
TOPIC_ARN = "arn:aws:sns:eu-central-1:123456789012:oura-health-alerts"

def lambda_handler(event, context):
    today = (datetime.utcnow() + timedelta(hours=2)).date().isoformat() # Today's date in Prague, CZ
    key = f"raw/{today}/readiness.json"
    
    try:
        response = s3.get_object(Bucket=BUCKET, Key=key)
        data = json.loads(response["Body"].read())
        
        if not data["data"]:
            return {"message": "No readiness data available"}
        
        readiness = data["data"][0]  # první záznam
        score = readiness.get("score", 0)

        if score < 70:
            message = f"Your readiness score is {score}. Consider recovery today."
            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="Low Readiness Alert",
                Message=message
            )
            return {"alert_sent": True, "score": score}
        else:
            return {"alert_sent": False, "score": score}

    except Exception as e:
        return {"error": str(e)}
