import sys
import csv
import tweepy
import string
import pandas as pd

if sys.version_info[0] < 3:
  input = raw_input
## Twitter credentials
consumer_key = "eTzZbHURKGFeumEqLO8Cdto36"
consumer_secret = "qE9M14IdJmpneUFdhYOxCi4hsKDz5dyYzJwRwXP2aKqCSSMnP3"
access_token = "1009092444023975936-NzWwBRhztdts13A1NnTflXL2bgOhhV"
access_token_secret = "WasBYGaPFyrm7Wx7rObEOJAcjH9GNFKpuVfBfeuBoxpJg"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)
filename = 'lebrontweets.csv'
# open/create a csv file to append data
csvFile = open(filename, 'a')
# use csv writer
csvWriter = csv.writer(csvFile)
query = "#lebron"
count = 1
lang = "en"
since = "2018-06-30"
tweetdf = []

for tweet in tweepy.Cursor(api.search, q=query, count=count, lang=lang, since=since).items():
    myString = str(tweet)
    startString = 'text='
    endString = 'is_quote_status='
    print(myString)
    tweetdf.append(myString[myString.find(startString)+len(startString):myString.find(endString)])

tweets = pd.DataFrame(tweetdf).drop_duplicates()
print(tweets)
tweets.to_csv(filename)


