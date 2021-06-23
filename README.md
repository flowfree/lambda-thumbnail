Lambda Thumbnail Generator
==========================

AWS Lambda function to generate a thumbnail for each image file that is uploaded to an S3 bucket. Based on [this tutorial](https://docs.aws.amazon.com/lambda/latest/dg/with-s3-tutorial.html) with some modifications.

Prerequisites
-------------

1. AWS CLI version 2

2. Docker

3. Create two S3 buckets. The first bucket will be used to upload the images and the second bucket will be used to store the generated thumbnails.

Deploy to Lambda
----------------

1.  Clone this repository:
        
        git clone git@github.com:flowfree/lambda-thumbnail.git

2.  Open `lambda_function.py` file and modify `bucket_src` and `bucket_dst` to match with your S3 buckets.

        bucket_src = <source bucket>
        bucket_dst = <bucket to store the thumbnails>

3.  Build the Docker container:

        docker build -t lambda-thumbnail .

4.  Authenticate the Docker CLI to your Amazon ECR registry:

        aws ecr get-login-password --region <region> | \
            docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com

5.  Create a repository in Amazon ECR:

        aws ecr create-repository \
            --repository-name lambda-thumbnail \
            --image-scanning-configuration scanOnPush=true \
            --image-tag-mutability MUTABLE

6.  Tag the previously built image to match with the repository name:

        docker tag lambda-thumbnail:latest <account>.dkr.ecr.<region>.amazonaws.com/lambda-thumbnail:latest

7.  Deploy the image to Amazon ECR:

        docker push <account>.dkr.ecr.<region>.amazonaws.com/lambda-thumbnail:latest

8.  Create a new IAM role for the Lambda function. It should have sufficient permissions like this:

        {
          "Version":"2012-10-17",
          "Statement":[
            {
              "Effect":"Allow",
              "Action":[
                "logs:PutLogEvents",
                "logs:CreateLogGroup",
                "logs:CreateLogStream"
              ],
              "Resource":"arn:aws:logs:*:*:*"
            },
            {
              "Effect":"Allow",
              "Action":[
                "s3:GetObject",
                "s3:GetObjectAcl"
              ],
              "Resource": "<ARN of the source S3 bucket>/*"
            },
            {
              "Effect":"Allow",
              "Action":[
                "s3:PutObject",
                "s3:PutObjectAcl"
              ],
              "Resource":"<ARN of the destination bucket>/*"
            },
            {
              "Effect":"Allow",
              "Action":[
                "ecr:SetRepositoryPolicy",
                "ecr:GetRepositoryPolicy",
                "ecr:InitiateLayerUpload"
              ],
              "Resource":"arn:aws:ecr:<region>:<account>:repository/*"
            }
          ]
        }

9.  Create the Lambda function:

        aws lambda create-function \
            --function-name lambda-thumbnail \
            --role <Role ARN> \
            --package-type Image \
            --code ImageUri=<account>.dkr.ecr.<region>.amazonaws.com/lambda-thumbnail:latest 


Test the Lambda function
------------------------

1.  Upload a sample image to the source bucket.

2.  Open `inputFile.txt` file, and change the value of the bucket name and object key to match with the uploaded image.

        {
          "Records": [
            {
              ...
              "s3": {
                "bucket": {
                  "name": <name of the source bucket>
                  ...
                },
                "object": {
                  "key": <name of the uploaded file>
                  ...
                }
                ...
              }
              ...
            }
          ]
        }

3.  Run the Lambda function:

        aws lambda invoke \
            --cli-binary-format raw-in-base64-out \
            --function-name lambda-thumbnail \
            --invocation-type Event \
            --payload file://inputFile.txt outputfile.txt

    It should create the thumbnail image on the destination bucket.

