import sys
import csv
import tweepy
import string
import pandas as pd
import json
import requests
import numpy as np
import matplotlib.pyplot as plt

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
filename = 'tweets.csv'
# open/create a csv file to append data
csvFile = open(filename, 'a')
# use csv writer
csvWriter = csv.writer(csvFile)
query = "the first purge"
count = 1
lang = "en"
since = "2018-07-04"
tweetdf = []
print('Preparing to stream your tweets....')
for tweet in tweepy.Cursor(api.search, q=query, count=count, lang=lang, since=since).items():
    myString = str(tweet)
    startString = 'text='
    endString = 'is_quote_status='
    print(myString)
    tweetdf.append(myString[myString.find(startString)+len(startString):myString.find(endString)])

tweets = pd.DataFrame(tweetdf).drop_duplicates()
print(tweets)
tweets.to_csv(filename)

tweets = pd.read_csv(filename)
tweets['language'] = 'en'
tweets.columns = ['id', 'text',  'language']
tweets.update(tweets.id.astype(str))
tweets = tweets[["language", "id", "text"]]
json_tweets = {"documents": tweets.to_dict(orient='records')}


with open('result.json', 'w') as fp:
    json.dump(json_tweets, fp)

with open('result.json') as f:
    json_tweets = json.load(f)




#sentimentanalysis
subscription_key = 'b8760a9d6dc646bb846a5387723b4083'
assert subscription_key
text_analytics_base_url = "https://westus2.api.cognitive.microsoft.com/text/analytics/v2.0/"
sentiment_api_url = text_analytics_base_url + "sentiment"
headers = {"Ocp-Apim-Subscription-Key": subscription_key}
response  = requests.post(sentiment_api_url, headers=headers, json=json_tweets)
sentiments = response.json()


print(sentiments)

json_output = pd.DataFrame()
json_sentiment = pd.DataFrame()
for index in range(0,int(len(sentiments['documents']))):
    tweet = [json_tweets['documents'][index]['text']]
    json_output = json_output.append(tweet)
    score = [sentiments['documents'][index]['score']]
    json_sentiment = json_sentiment.append(score)

json_response = pd.DataFrame()
json_response = pd.concat([json_output.reset_index(drop=True), json_sentiment.reset_index(drop=True)], axis=1)
json_response.columns = ['tweets', 'sentiment']
json_response = json_response[json_response.sentiment!=.5]
json_response = json.dumps(json_response.to_dict(orient='records'))
print(json_response)

#key phrase extraction
key_phrase_url = text_analytics_base_url + 'keyPhrases'
response = requests.post(key_phrase_url, headers=headers, json=json_tweets)
key_phrases = response.json()
print(key_phrases)

key_phrase_df = pd.DataFrame()
for index in range(0, int(len(key_phrases['documents']))):
    phrase = pd.Series(str(' '.join(key_phrases['documents'][index]['keyPhrases'])))
    key_phrase_df = key_phrase_df.append(phrase, ignore_index=True)

#key_phrase_df is a one column df of words
print(key_phrase_df.head(10))



#histogram
df_response = pd.DataFrame()
df_response = pd.concat([json_output.reset_index(drop=True), json_sentiment.reset_index(drop=True)], axis=1)
df_response.columns = ['tweets', 'sentiment']
df_response = df_response[df_response.sentiment!=.5]
fig = plt.hist(df_response['sentiment'])
plt.savefig(str(query+'sentiment.png'))


