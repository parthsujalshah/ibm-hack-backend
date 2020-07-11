import tweepy as tw
import json
import datetime
import time 
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
from os import path, environ
from time import sleep

base_dir = path.abspath(path.dirname(path.dirname(path.dirname(__file__))))
load_dotenv(path.join(base_dir, '.env'))

auth = tw.OAuthHandler(environ.get('TWITTER_CONSUMER_KEY'), environ.get('TWITTER_CONSUMER_SECRET'))
auth.set_access_token(environ.get('TWITTER_ACCESS_TOKEN'), environ.get('TWITTER_ACCESS_TOKEN_SECRET'))

api = tw.API(auth, wait_on_rate_limit=True, timeout = 150)


searchTerm = 'car'

def sent_count(document_tone):
    sentiments = ['anger','disgust','fear','joy','sadness','analytical','confident','tentative']
    sent_count_dict = {}
    
    for s in sentiments:
        sent_count_dict[s] = 0

    for sent_index in sentiments:
        for i in range(len(document_tone)):
            if document_tone[i]['tone_id'] == sent_index:
                sent_count_dict[sent_index]+=1
    return sent_count_dict

def analyze_tone(textString):
    version = '2017-09-21'
    ibmUrl = environ.get('IBM_TONE_ANALYZER_URL')
    ibmApiKey = environ.get('IBM_TONE_ANALYZER_KEY')
    authenticator = IAMAuthenticator(ibmApiKey)
    tone_analyzer = ToneAnalyzerV3(version=version, authenticator=authenticator)
    tone_analyzer.set_service_url(ibmUrl)
    jsonFile = tone_analyzer.tone({'text': textString}, content_type='text/plain',sentences=True).get_result()
    document_tone = jsonFile['document_tone']['tones']
    sent_count_dict = sent_count(document_tone)
    jsonDumpsData = {'jsonFile':json.dumps(jsonFile),'sent_count_dict':sent_count_dict}
    return jsonDumpsData

def get_daily_tweets(searchTerm, count, no_of_days):
    no_of_days = int(no_of_days)
    count = int(count)
    geo = "21.1498134,79.0820556,1045km"
    today = datetime.date.today()
    start_datetime = today - datetime.timedelta(days=1)
    output = {}
    while len(output) != no_of_days:
        for tweet in tw.Cursor(api.search,q=searchTerm, since= start_datetime, until= today, geocode= geo, lang='en').items(count):
            tweetText = tweet.text
            tweet_date = tweet.created_at.strftime('%d-%m-%Y')
            jsonfile = analyze_tone(tweetText)
            if tweet_date in output:
                for i in output[tweet_date]:
                    output[tweet_date][i] += jsonfile['sent_count_dict'][i]
            else:
                output[tweet_date] = jsonfile['sent_count_dict']
        today -= datetime.timedelta(days=1)
        start_datetime -= datetime.timedelta(days=1)
    return output

def state_tweets(num_of_tweets_per_state, default_keyword):
    num_of_tweets_per_state = int(num_of_tweets_per_state)
    states_and_uts=['Andaman and Nicobar Islands','Andhra Pradesh','Arunachal Pradesh','Assam','Bihar','Chandigarh','Chhattisgarh','Daman and Diu','Delhi','Goa','Gujarat','Haryana','Himachal Pradesh','Jammu and Kashmir','Jharkhand','Karnataka','Kerala','Ladakh','Lakshadweep','Madhya Pradesh','Maharashtra','Manipur','Meghalaya','Mizoram','Nagaland','Odisha','Puducherry','Punjab','Rajasthan','Sikkim','Tamil Nadu','Telangana','Tripura','Uttar Pradesh','Uttarakhand','West Bengal']

    location = [(10.2188344, 92.5771329), (15.9240905, 80.1863809), (27.6891712, 96.4597226), (26.4073841, 93.2551303), (25.6440845, 85.906508), (30.7194022, 76.7646552), (21.6637359, 81.8406351), (20.713587, 70.92296517214575), (28.6517178, 77.2219388), (15.3004543, 74.0855134), (22.41540825, 72.03149703699282), (29.0, 76.0), (31.81676015, 77.34932051968858), (33.5574473, 75.06152), (23.4559809, 85.2557301), (14.5203896, 75.7223521), (10.3528744, 76.5120396), (33.9456407, 77.6568576),
                (10.8832771, 72.8171069), (23.9699282, 79.39486954625225), (19.531932, 76.0554568), (24.7208818, 93.9229386), (25.5379432, 91.2999102), (23.2146169, 92.8687612), (26.1630556, 94.5884911), (20.5431241, 84.6897321), (11.9340568, 79.8306447), (30.9293211, 75.5004841), (26.8105777, 73.7684549), (27.601029, 88.45413638680145), (10.9094334, 78.3665347), (17.8495919, 79.1151663), (23.7750823, 91.7025091), (27.1303344, 80.859666), (30.091993549999998, 79.32176659343018), (22.9964948, 87.6855882)]

    state_dict = {}

    for i, state_index in enumerate(states_and_uts):
        tweets_list = []
        geocode="%f"%location[i][0]+','+"%f" % location[i][1]+",100km"
        for tweet in tw.Cursor(api.search, q=default_keyword, lang='en', geocode=geocode).items(num_of_tweets_per_state):
            retrieved_tweet = tweet.text
            json_tones = analyze_tone(retrieved_tweet)
            if state_index in state_dict:
                for i in state_dict[state_index]:
                    state_dict[state_index][i] += json_tones['sent_count_dict'][i]
            else:
                state_dict[state_index] = json_tones['sent_count_dict']
    return state_dict