import boto3
import urllib.parse

s3 = boto3.client('s3')
rekognition = boto3.client('rekognition')
sns = boto3.client('sns')

SNS_TOPIC_ARN = 'arn:aws:sns:eu-central-1:216989098112:SmartUploadAlert'
VERIFIED_BUCKET = 'smart-upload-verified'
QUARANTINED_BUCKET = 'smart-upload-quarantined'


def lambda_handler(event, context):
    # Parse bucket and key from S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key_raw = event['Records'][0]['s3']['object']['key']
    key = urllib.parse.unquote_plus(key_raw)

    # Get image from S3 bucket
    response = s3.get_object(Bucket=bucket, Key=key)
    image_bytes = response['Body'].read()

    # Detect general labels
    label_response = rekognition.detect_labels(
        Image={'Bytes': image_bytes},
        MaxLabels=10,
        MinConfidence=75
    )
    labels = [label['Name'] for label in label_response['Labels']]

    # Detect moderation labels
    mod_response = rekognition.detect_moderation_labels(
        Image={'Bytes': image_bytes},
        MinConfidence=80
    )
    mod_labels = [label['Name'] for label in mod_response['ModerationLabels']]

    # Determine target bucket and create SNS message
    if mod_labels:
        target_bucket = QUARANTINED_BUCKET
        reason = ', '.join(mod_labels)
        message = f"⚠️ Image '{key}' flagged for moderation: {reason}. Labels detected: {', '.join(labels)}"
    else:
        target_bucket = VERIFIED_BUCKET
        message = f"✅ Image '{key}' passed moderation. Labels detected: {', '.join(labels)}"

    # Move image to target bucket
    s3.copy_object(
        Bucket=target_bucket,
        CopySource={'Bucket': bucket, 'Key': key},
        Key=key,
        Metadata={
            'Labels': ','.join(labels),
            'ModerationLabels': ','.join(mod_labels) if mod_labels else 'None'
        },
        MetadataDirective='REPLACE'
    )
    s3.delete_object(Bucket=bucket, Key=key)

    # Send SNS alert with error handling
    try:
        print("SNS_TOPIC_ARN:", SNS_TOPIC_ARN)
        response = sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=message,
            Subject="Smart Upload Scanner"
        )
        print("SNS publish successful:", response)
    except Exception as e:
        print("SNS publish failed:", str(e))
