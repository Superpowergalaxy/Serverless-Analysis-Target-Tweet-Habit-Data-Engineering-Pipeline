# Serverless-Analysis-Target-Tweet-Habit-Data-Engineering-Pipeline
Serverless Analysis Target Tweet Habit  Data Engineering Pipeline with AWS lambda, S3. SQS


![pipline](https://user-images.githubusercontent.com/8799320/80254980-136f8900-864a-11ea-9a35-161a073842e8.png)

To use twitter API, you need to apply for an twitter developer account and obtain the twitter_keys.


To run included scrept you need to add libraries AWS does not provide. You can add those libraries by:

Open cloud9 instance, start an lambda function, cd into the lambda function folder. Run:

For `Collect_tweets.py`:
        
        pip3 install --target=./ tweepy

For `analyisis tweets.py`:
        
        pip3 install --target=./ matplotlib

After install the necessary library, deploy the function, and added the SQS trigger to the `analyisis tweets.py` scrept. and an watch timmer trigger for the `Collect_tweets.py` scrept. 

You can have the result:
![result](https://user-images.githubusercontent.com/8799320/80251624-eae49080-8643-11ea-9d16-108ea8edcc46.png)
