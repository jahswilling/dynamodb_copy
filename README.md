# dynamodb_copy

This script is used to migrate data between two DynamoDB tables in different environments (development and production) using the AWS SDK for Python (Boto3). It scans the development table and writes the items to the production table in batches of 25. It also implements exponential backoff in case of throttling exceptions.

## Requirements
- Python 3.x
- AWS SDK for Python (Boto3)
- An AWS account with access to DynamoDB and the tables to be migrated
- An AWS profile with access to the account and the tables to be migrated

## Usage
1. Set the AWS session using the profile name and region. Replace 'your_aws_profile' with the name of your AWS profile and 'your_aws_region' with the name of the region where the tables are located.
2. Set the names of the development and production tables. Replace 'dev_table_name' and 'prod_table_name' with the names of your development and production tables.
3. Set the batch size. You can adjust this value to optimize performance.
4. Set the maximum number of retries. You can adjust this value to optimize performance.
5. Run the script.
6. Check the number of items in the production table to ensure that all items have been migrated successfully.
7. Set the subject, body, sender, recipients, and password for the email to be sent.
8. Run the send_email function to send an email confirming that the migration is complete.

## Disclaimer
This script is provided as-is, without any warranty or support. It is intended to be used as a starting point for your own migration scripts and should be modified to fit your specific requirements.
