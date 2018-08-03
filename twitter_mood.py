import sys
import csv
import tweepy
import pandas as pd
import json
import requests
import matplotlib.pyplot as plt
import re, nltk
from nltk.stem.porter import PorterStemmer
from nltk.corpus import stopwords
from gensim import corpora, models
import gensim
from wordcloud import WordCloud

if sys.version_info[0] < 3:
  input = raw_input
# Azure credentials
subscription_key = ''#subscription key
assert subscription_key
text_analytics_base_url = "https://westus2.api.cognitive.microsoft.com/text/analytics/v2.0/"
headers = {"Ocp-Apim-Subscription-Key": subscription_key}
# Twitter credentials
consumer_key = ''#your key
consumer_secret = ''#your secret
access_token = ''#your token
access_token_secret = ''#your secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)
stemmer = PorterStemmer()
filename = 'tweets.csv'
csvFile = open(filename, 'a')
csvWriter = csv.writer(csvFile)

def download_tweets(api, query, count, lang, since):
    print('Preparing to stream your tweets....')
    tweet_df = []
    for tweet in tweepy.Cursor(api.search, q=query, count=count, lang=lang, since=since).items():
        myString = str(tweet)
        startString = 'text='
        endString = 'is_quote_status='
        tweet_df.append(myString[myString.find(startString)+len(startString):myString.find(endString)])
    tweetsdedup = pd.DataFrame(tweet_df).drop_duplicates()
    print(tweetsdedup)
    tweetsdedup.to_csv(filename)


def azure_body_constructor(filename):
    tweets = pd.read_csv(filename)
    tweets['language'] = 'en'
    tweets.columns = ['id', 'text',  'language']
    tweets.update(tweets.id.astype(str))
    tweets = tweets[["language", "id", "text"]]
    json_tweets = {"documents": tweets.to_dict(orient='records')}
    return json_tweets


def json_formatter(json_tweets):
    with open('result.json', 'w') as fp:
        json.dump(json_tweets, fp)
    with open('result.json') as f:
        json_formatted = json.load(f)
    return json_formatted


def analyze_sentiment(json_tweets):
    json_formatter(json_tweets)
    sentiment_api_url = text_analytics_base_url + "sentiment"
    response  = requests.post(sentiment_api_url, headers=headers, json=json_tweets)
    sentiments = response.json()
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
    return json_response
    # json_response = json_response[json_response.sentiment!=.5]


def analyze_keyphrases(json_tweets):
    json_formatter(json_tweets)
    key_phrase_url = text_analytics_base_url + 'keyPhrases'
    response = requests.post(key_phrase_url, headers=headers, json=json_tweets)
    key_phrases = response.json()
    key_phrase_df = pd.DataFrame()
    for index in range(0, int(len(key_phrases['documents']))):
        phrase = pd.Series(str(' '.join(key_phrases['documents'][index]['keyPhrases'])).lower())
        key_phrase_df = key_phrase_df.append(phrase, ignore_index=True)
    key_phrase_df.columns = ['keyPhrases']
    return key_phrase_df.head()


def word_count(key_phrases):
    wordcounts = key_phrases.keyPhrases.str.split(expand=True).stack().value_counts()
    return wordcounts



def build_hist(query, df_response):
    plt.hist(df_response['sentiment'])
    plt.savefig(str(query+'sentiment.png'))
    print("Histogram file saved")




def stem_tokens(tokens, stemmer):
    stemmed = []
    for item in tokens:
        stemmed.append(stemmer.stem(item))
    return stemmed


def tokenize(text):
    text = re.sub("[^a-zA-Z]", " ", text)  # Removing numbers and punctuation
    text = re.sub(" +", " ", text)  # Removing extra white space
    text = re.sub("\\b[a-zA-Z0-9]{10,100}\\b", " ", text)  # Removing very long words above 10 characters
    text = re.sub("\\b[a-zA-Z0-9]{0,1}\\b", " ", text)  # Removing single characters (e.g k, K)
    tokens = nltk.word_tokenize(text.strip())
    tokens = nltk.pos_tag(tokens)
    # Uncomment next line to use stemmer
    # tokens = stem_tokens(tokens, stemmer)
    return tokens


def extract_topics(filename, Uname, num_topics):
    fileObj = input_file(filename)
    text_corpus = []
    for doc in fileObj:
        temp_doc = tokenize(doc.strip())
        current_doc = []
        for word in range(len(temp_doc)):
            if temp_doc[word][0] not in stopset and temp_doc[word][1] == 'NN':
                current_doc.append(temp_doc[word][0])

        text_corpus.append(current_doc)

    dictionary = corpora.Dictionary(text_corpus)
    corpus = [dictionary.doc2bow(text) for text in text_corpus]
    ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=60)
    for t in range(ldamodel.num_topics):
        plt.figure()
        plt.imshow(WordCloud().fit_words(dict(ldamodel.show_topic(t, 200))))
        plt.axis("off")
        plt.title("Topic #" + str(t))
        plt.show()
    print 'Topics for ', Uname, '\n'
    for topics in ldamodel.print_topics(num_topics=num_topics, num_words=7):
        print topics, "\n"


def input_file(filename):
    tweets = pd.read_csv(filename)
    tweets['language'] = 'en'
    tweets.columns = ['id', 'text',  'language']
    tweets.update(tweets.id.astype(str))
    tweets = tweets[["language", "id", "text"]]
    return tweets.text

stopset = stopwords.words('english')
freq_words = ['http', 'https', 'amp', 'com', 'co', 'th']
for i in freq_words:
    stopset.append(i)


def main(query, count, since, num_topics):
    lang = "en"
    download_tweets(api=api, query=query, count=count, lang=lang, since=since)
    json_tweets = azure_body_constructor(filename)
    sentiment = analyze_sentiment(json_tweets)
    json_response = json.dumps(sentiment.to_dict(orient='records'))
    keyPhrases = analyze_keyphrases(json_tweets)
    build_hist(query, sentiment)
    extract_topics(filename, query, num_topics)


query = "lakers"
count = 5
since = "2018-07-14"
num_topics = 5
main(query, count, since, num_topics)
