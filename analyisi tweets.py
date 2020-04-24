import json
import tempfile
import csv
import os
import boto3
import matplotlib.pyplot as plt
from botocore.exceptions import ClientError


def read_csv(bucket, object_name):
    s3 = boto3.client('s3')

    with tempfile.TemporaryDirectory() as tmpdir:
        download_path = os.path.join(tmpdir, object_name)
        s3.download_file(bucket, object_name, download_path)
        items = []
        with open(download_path) as csvfile:
            readCSV = csv.reader(csvfile, delimiter=',')
            # skep header
            next(readCSV)

            times = []
            for row in readCSV:
                time = int(row[0].split(' ')[-1].split(':')[0])
                times.append(time)
    return times
    
def plot_times_hist(times):
    plt.figure()
    plt.hist(times, bins = 24,range=(0,23))
    plt.title('President Trump\'s twtter usage vs time')
    plt.xlabel('Hours of the Day')
    plt.ylabel('Freqency of tweet')
    plt.savefig("/tmp/trump_tweets_time.pdf")
    
def upload_file(bucket,file_name,object_name = None):

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    # remember to set the creditenals with 'aws configure' command 
    s3_client = boto3.client('s3')

    try:
        response = s3_client.upload_file(file_name, bucket,object_name)
        print('upload_successful\n', response)
    except ClientError as e:
        print(e)
        return False
    return True

    
def lambda_handler(event, context):
    print(event)
    #loop throuth all sqs 
    for enenti in event['Records']:
        # print(enenti['body'])
        indata = json.loads(enenti['body'])
        object_name = indata['object_name']
        bucket =  indata['bucket'] 
        # log buckit and object
        print(object_name, bucket)
        read_csv(bucket, object_name)
        
        # get file
    
        # object_name = 'trump_tweets.csv'
        # bucket= 'serverless-twitter'
        times = read_csv(bucket, object_name)
        print('length collected: ',len(times))
        plot_times_hist(times)
        upload_file(bucket= 'serverless-twitter',file_name = '/tmp/trump_tweets_time.pdf', object_name = 'trump_tweets_time.pdf')




    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }