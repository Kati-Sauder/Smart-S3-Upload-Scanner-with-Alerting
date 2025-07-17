# Smart-S3-Upload-Scanner-with-Alerting

This project uses AWS Lambda, Amazon Rekognition, S3 and SNS to automatically check, sort and, if necessary, alert uploaded images.

## 🔎 Features

- Images are automatically checked and labelled regarding their content
- They are also being checked for moderation content (e.g. NSFW)
- Automatic move to:
  - ✅ `smart-upload-verified`: harmless content
  - ⛔️ `smart-upload-quarantined`: problematic content
- SNS notification for moderation findings

## 🔩 AWS Services used

- S3: Upload, storage, sorting

- Lambda: image processing & orchestration

- Rekognition: label & moderation analysis

- SNS: Notifications

- IAM: authorizations and roles

## 💡 How it works

1. An image is uploaded to the inbox bucket.

2. The Lambda function is triggered by an event.

3. The image is analyzed with Rekognition:

   - General labels (e.g. “Cat”, ‘Beach’, “Food”)
   - Moderation labels (e.g. “Explicit Nudity”)

4. The image is moved depending on the result:

   - To “Verified” or “Quarantined”

5. If moderation labels were recognized:

   - SNS alert is sent

## 🧫 Test

1. Upload an image to the smart-upload-inbox bucket

2. Check the result in the appropriate target bucket

3. Receive SNS message in e-mail inbox

## 📸 Screenshots

I uploaded some test images to my inbox-bucket (only jpg and png possible with Rekognition).

Here You can see the content of the verified bucket. There's a flaw: Altough there is a picture called "violence" (image of strangling) it has been moved to the verified bucket. So it's still a machine which can make mistakes. 

![Architecture Diagram]([assets/content of verified s3.png](https://github.com/Kati-Sauder/Smart-S3-Upload-Scanner-with-Alerting/blob/main/assets/content%20of%20verified%20s3.png))

And here the content of the quarantined bucket.

**Note:**
Amazon Rekognition lets you set a confidence threshold (e.g. MinConfidence=80) when detecting moderation labels.

This defines how confident Rekognition must be before labeling content as inappropriate.

- Strict moderation needs (e.g. for youth-friendly platforms): use MinConfidence = 70–80

- Tolerant/moderate filtering: use MinConfidence = 90+

So there's definitely a risk of false positives but also the risk of unsafe content "passing through". This tool is an awesome way to filter but if you want to be 100% sure about uploaded content, do a manual check. SNS alerts help with that, so you won't miss any new uploaded content. 

![Architecture Diagram]([assets/content of quarantined s3.png](https://github.com/Kati-Sauder/Smart-S3-Upload-Scanner-with-Alerting/blob/main/assets/content%20of%20quarantined%20s3.png))

Under properties, you can see the metadata of all objects in the bucket. It shows the labels Rekognition has given each image. 

![Architecture Diagram]([assets/metadata of object in bucket.png](https://github.com/Kati-Sauder/Smart-S3-Upload-Scanner-with-Alerting/blob/main/assets/metadata%20of%20object%20in%20bucket.png))

Triggered SNS alert because  of problematic content found in a bucket. 

![Architecture Diagram]([assets/sns alert email.png](https://github.com/Kati-Sauder/Smart-S3-Upload-Scanner-with-Alerting/blob/main/assets/sns%20alert%20email.png))

## ⚙️ Simplified Deployment Guide

**Prerequisites**

- AWS account

- IAM role for Lambda with permissions for:

  - S3 (GetObject, PutObject, DeleteObject)

  - Rekognition (DetectLabels, DetectModerationLabels)

  - SNS (Publish)

- Three S3 buckets:

  - smart-upload-inbox

  - smart-upload-verified

  - smart-upload-quarantined

- SNS topic mit meaningful name

- Lambda function with trigger on smart-upload-inbox

---------------

**Step-by-Step Setup (AWS Console)**

1. Create S3 Buckets

   - INBOX BUCKET

   - VERIFIED BUCKET

   - QUARANTINED BUCKET

2. Create SNS Topic

- Name: INBOX BUCKET NAME

- Add your email as a subscriber and confirm the subscription

3. Create Lambda Function

- Runtime: Python 3.x

- Paste the code

- Set environment variables (if needed)

- Assign the IAM role with required permissions

4. Add S3 Trigger to Lambda

- Event type: PUT

- Bucket: INBOX BUCKET NAME

5. Update Bucket Policy (optional but recommended)

- Allow Lambda to be triggered by S3

- Ensure cross-bucket access permissions

6. Upload Test Images to Inbox

- Images are automatically scanned

- Based on labels, images are moved to:

  - smart-upload-verified ✅

  - or smart-upload-quarantined ⛔

- Alerts sent to SNS subscribers

## ✏️ Note

This project was created entirely via the AWS console (without IaC).
The architecture can still be converted into code (e.g. with Terraform).

## License

This project is licensed under the [MIT License](LICENSE).




