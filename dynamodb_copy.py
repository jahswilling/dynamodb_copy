import boto3
from boto3.dynamodb.conditions import Key
import botocore

import time
import smtplib
from email.mime.text import MIMEText

#Set the AWS session using the profile name and region
session = boto3.session.Session(profile_name='your_aws_profile')
ddb = session.resource('dynamodb', region_name='your_aws_region')

#Set the names of the development and production tables
dev_table_name = ddb.Table('dev_table_name')
prod_table_name = ddb.Table('prod_table_name')

print(f"Number of items in {dev_table_name.name}: {dev_table_name.item_count}")

#Set the initial variables for the batch migration process
count = 0
start_time = time.time()

batch_size = 25
items = []
response = dev_table_name.scan(Limit=batch_size)
items.extend(response['Items'])

# Define the maximum number of retries
max_retries = 10


#Scanning the development table and writing to the production table in batches
while 'LastEvaluatedKey' in response:
    response = dev_table_name.scan(ExclusiveStartKey=response['LastEvaluatedKey'], Limit=batch_size)
    items.extend(response['Items'])
    if len(items) >= batch_size:
        # Implement exponential backoff
        retries = 0
        while retries < max_retries:
            try:
                with prod_table_name.batch_writer() as batch:
                    for item in items:
                        batch.put_item(Item=item)
                    time.sleep(1) # Wait for 1 second between batches
                    count += len(items)
                    items = []
                break
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'ThrottlingException':
                    wait_time = 2 ** retries
                    print(f"ThrottlingException encountered, retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                    retries += 1
                else:
                    raise e

# Write any remaining items
if items:
    # Implement exponential backoff
    retries = 0
    while retries < max_retries:
        try:
            with prod_table_name.batch_writer() as batch:
                for item in items:
                    batch.put_item(Item=item)
                count += len(items)
                items = []
            break
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'ThrottlingException':
                wait_time = 2 ** retries
                print(f"ThrottlingException encountered, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
                retries += 1
            else:
                raise e

print(f"Number of items in {dev_table_name.name}: {count}")


print("All items have been migrated successfully!")
end_time = time.time() # Record the end time

elapsed_time = end_time - start_time  # Calculate the elapsed time
print(f"Elapsed time: {elapsed_time} seconds")

#send mail function
def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    smtp_server.login(sender, password)
    smtp_server.sendmail(sender, recipients, msg.as_string())
    smtp_server.quit()

subject = "Migrating Data Between DynamoDB Table's"
body = f'The total time is {elapsed_time}'
sender = "jahswilling@gmail.com"
recipients = ["jahswilling@gmail.com"]
password = "your_password"

#Send an email to confirm that the migration is complete
send_email(subject, body, sender, recipients, password)

print("Email sent!")
