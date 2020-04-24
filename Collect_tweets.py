import json
import tweepy
import time
import boto3
from tweepy import OAuthHandler, StreamListener
from tweepy import API 
import datetime
import csv
from botocore.exceptions import ClientError


class TweetMiner(object):

    result_limit    =   20    
    data            =   []
    api             =   False
    
    twitter_keys = {
        "ACCESS_TOKEN": "",
        "ACCESS_TOKEN_SECRET" : "",
        "CONSUMER_KEY" :"",
        "CONSUMER_SECRET" :""
    }
    
    
    def __init__(self, keys_dict=twitter_keys, api=api, result_limit = 20):
        
        self.twitter_keys = keys_dict
        
        auth = tweepy.OAuthHandler(keys_dict['CONSUMER_KEY'], keys_dict['CONSUMER_SECRET'])
        auth.set_access_token(keys_dict['ACCESS_TOKEN'], keys_dict['ACCESS_TOKEN_SECRET'])
        
        self.api = tweepy.API(auth)
        self.twitter_keys = keys_dict
        
        self.result_limit = result_limit
        

    def mine_user_tweets(self, user="dril", #BECAUSE WHO ELSE!
                         mine_rewteets=False,
                         max_pages=5):

        data           =  []
        last_tweet_id  =  False
        page           =  1
        
        while page <= max_pages:
            if last_tweet_id:
                statuses   =   self.api.user_timeline(screen_name=user,
                                                     count=self.result_limit,
                                                     max_id=last_tweet_id - 1,
                                                     tweet_mode = 'extended',
                                                     include_retweets=True
                                                    )        
            else:
                statuses   =   self.api.user_timeline(screen_name=user,
                                                        count=self.result_limit,
                                                        tweet_mode = 'extended',
                                                        include_retweets=True)
                
            for item in statuses:

                mined = {
                    'tweet_id':        item.id,
                    'name':            item.user.name,
                    'screen_name':     item.user.screen_name,
                    'retweet_count':   item.retweet_count,
                    'text':            item.full_text,
                    'mined_at':        datetime.datetime.now(),
                    'created_at':      item.created_at,
                    'favourite_count': item.favorite_count,
                    'hashtags':        item.entities['hashtags'],
                    'status_count':    item.user.statuses_count,
                    'location':        item.place,
                    'source_device':   item.source
                }
                
                try:
                    mined['retweet_text'] = item.retweeted_status.full_text
                except:
                    mined['retweet_text'] = 'None'
                try:
                    mined['quote_text'] = item.quoted_status.full_text
                    mined['quote_screen_name'] = item.quoted_status.user.screen_name
                except:
                    mined['quote_text'] = 'None'
                    mined['quote_screen_name'] = 'None'
                
                last_tweet_id = item.id
                data.append(mined)
                
            page += 1
            
        return data 
        
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


def sendsqs(queue_url,object_name, bucket):
    sqs = boto3.client('sqs')
    response = sqs.send_message(QueueUrl=queue_url,
                                DelaySeconds= 1,
                                MessageBody=(json.dumps({'object_name':object_name , 'bucket':bucket})))
    print(response)
    return response


def lambda_handler(event, context):
    # TODO implement
    miner=TweetMiner(result_limit = 200 )
    
    mined_tweets = miner.mine_user_tweets(user='realDonaldTrump', max_pages=17)
    print('length of mined tweets is :', len(mined_tweets))
    csvw = csv.writer(open('/tmp/trump_tweets.csv', "w"))
    csvw.writerow(['created_at', 'location', 'text'])
    for tweet in mined_tweets:
            csvw.writerow([tweet['created_at'],tweet['location'], tweet['text']])
    print('started new file')
    
    upload_file(bucket= 'serverless-twitter',file_name = '/tmp/trump_tweets.csv',object_name = 'trump_tweets.csv' )
    
    queue_url = 'https://sqs.us-east-1.amazonaws.com/227763391973/serverless-tweet'
    sendsqs(queue_url ,object_name = 'trump_tweets.csv', bucket= 'serverless-twitter')
    
    return {
        'statusCode': 200,
        'body': json.dumps('successful')
    }
