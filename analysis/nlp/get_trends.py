import tweepy as tw
import json
from ibm_watson import ToneAnalyzerV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
from os import path, environ

base_dir = path.abspath(path.dirname(path.dirname(path.dirname(__file__))))
load_dotenv(path.join(base_dir, '.env'))

auth = tw.OAuthHandler(environ.get('TWITTER_CONSUMER_KEY'), environ.get('TWITTER_CONSUMER_SECRET'))
auth.set_access_token(environ.get('TWITTER_ACCESS_TOKEN'), environ.get('TWITTER_ACCESS_TOKEN_SECRET'))

api = tw.API(auth, wait_on_rate_limit=True, timeout=150)

def sent_count(document_tone):
    #Declaring dictionary for getting count of each sentiment from all tweets displayed
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
    ibmApiKey = environ.get('IBM_TONE_ANALYZER_KEY')
    ibmUrl = environ.get('IBM_TONE_ANALYZER_URL')
    authenticator = IAMAuthenticator(ibmApiKey)
    tone_analyzer = ToneAnalyzerV3(version=version, authenticator=authenticator)
    tone_analyzer.set_service_url(ibmUrl)   
    jsonFile = tone_analyzer.tone({'text': textString}, content_type='text/plain',sentences=True).get_result()
    
    document_tone = jsonFile['document_tone']['tones']
    sent_count_dict = sent_count(document_tone)
    jsonDumpsData = {'jsonFile':json.dumps(jsonFile),'sent_count_dict':json.dumps(sent_count_dict)}
    return jsonDumpsData

def trending_keywords_india(no_of_terms):
    # India's Where on Earth ID provided by Yahoo
    no_of_terms = int(no_of_terms)
    trends_list = []
    india_woeid = 23424848

    india_trends = api.trends_place(india_woeid)
    trends = json.loads(json.dumps(india_trends, indent =1))
    
    #Top trending tweets in India
    for trend in trends[0]["trends"][0:no_of_terms]:
        trends_list.append(trend["name"])
    return trends_list

def popular_tweets(searchTerm, num_of_tweets):
    output = []
    num_of_tweets = int(num_of_tweets)
    geo = "21.1498134,79.0820556,1045km"
    tweets = api.search(q=searchTerm,result_type="recent",count=2*num_of_tweets, geocode=geo,lang='en')
    
    for i,tweet in enumerate(tweets):
        tweetedText = tweet.text
        jsonFile1 = analyze_tone(tweetedText)
        if (len(json.loads(jsonFile1['jsonFile'])['document_tone']['tones']) > 0) :
            output.append({'tweet_text': tweetedText, 'sent_count': jsonFile1['sent_count_dict']})
            if(len(output) == num_of_tweets):
                break
    return output