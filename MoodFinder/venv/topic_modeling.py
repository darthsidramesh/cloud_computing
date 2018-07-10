import pandas as pd
import json
import requests

#preprocessing
filename = 'lebrontweets.csv'
tweets = pd.read_csv(filename)
tweets['language'] = 'en'
tweets.columns = ['id', 'text',  'language']
tweets.update(tweets.id.astype(str))
tweets = tweets[['language', 'id', 'text']]
json_tweets = {'documents': tweets.to_dict(orient='records')}
json_tweets = json.dumps(json_tweets)

#sentimentanalysis
subscription_key = 'b8760a9d6dc646bb846a5387723b4083'
assert subscription_key
text_analytics_base_url = "https://westus2.api.cognitive.microsoft.com/text/analytics/v2.0/"
sentiment_api_url = text_analytics_base_url + "sentiment"
headers = {"Ocp-Apim-Subscription-Key": subscription_key}
response  = requests.post(sentiment_api_url, headers=headers, json=json_tweets)
sentiments = response.json()

print(sentiments)