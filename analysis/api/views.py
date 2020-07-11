from django.shortcuts import get_object_or_404
from .serializers import AnalysisCreateSerializer, AnalysisListSerializer, AnalysisRetrieveSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import RetrieveAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from ..models import Analysis, DefaultKeyword
from constants.models import (
  DaysOfTrendingTweets,
  NoOfPopularTweets,
  NoOfTrendingKeywords,
  NumOfTweetsPerDay,
  NumOfTweetsPerState
)
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from analysis.nlp import statewise_sentiments, get_trends
import json
from ..utils import (
  total_sentiments,
  total_indivudual_sentiments,
  get_tone_labels,
  total_sentiment_count_per_state,
  total_sentiment_count_per_date,
  max_sentiment,
  add_OR_in_strings
)

class AnaylsisView(ModelViewSet):

  queryset = Analysis.objects.all()

  serializer_action_classes = {
    'create': AnalysisCreateSerializer,
    'list': AnalysisListSerializer,
    'retrieve': AnalysisRetrieveSerializer,
  }

  permission_classes_by_action = {
    'create': [IsAuthenticated],
    'list': [IsAuthenticated],
    'retrieve': [IsAuthenticated],
    'destroy': [IsAuthenticated],
  }

  def get_serializer_class(self):
    return self.serializer_action_classes[self.action]

  def get_permissions(self):
    try:
      return [permission() for permission in self.permission_classes_by_action[self.action]]
    except KeyError:
      return [permission() for permission in self.permission_classes]

  def perform_create(self, serializer):
    user_referred_id = Token.objects.filter(key=self.request.headers['Authorization'].split()[1])[0].user.id
    if serializer.is_valid():
      saved_model = serializer.save(create_by_id=user_referred_id)
      default_keywords = DefaultKeyword.objects.all()
      num_of_tweets_per_default_keyword = NumOfTweetsPerState.objects.get(id=1).value
      num_of_tweets_per_day = NumOfTweetsPerDay.objects.get(id=1).value
      days_of_trending_tweets = DaysOfTrendingTweets.objects.get(id=1).value
      num_of_popular_tweets = NoOfPopularTweets.objects.get(id=1).value
      num_of_trending_keywords = NoOfTrendingKeywords.objects.get(id=1).value
      or_def_keywords = add_OR_in_strings(default_keywords)
      or_def_keywords1 = or_def_keywords
      or_def_keywords2 = or_def_keywords

      sentiment_count_per_state = []
      for custom_keyword in serializer.data["keywords"]:
        or_def_keywords1 = or_def_keywords1 + " " + custom_keyword['keyword']
    
      print(type(or_def_keywords1))
      print(or_def_keywords1)
      print(num_of_tweets_per_default_keyword)
      print(type(num_of_tweets_per_default_keyword))
      sentiment_count_per_state.append(statewise_sentiments.state_tweets(num_of_tweets_per_default_keyword, or_def_keywords1))
      
      datewise_sentiments = []
      for custom_keyword in serializer.data["keywords"]:
        or_def_keywords2 = or_def_keywords2 + " " + custom_keyword['keyword']
      datewise_sentiments.append(statewise_sentiments.get_daily_tweets(or_def_keywords2, num_of_tweets_per_day, days_of_trending_tweets))

      _trending_tweets = get_trends.popular_tweets(add_OR_in_strings(default_keywords), num_of_popular_tweets)
      _trending_keywords = get_trends.trending_keywords_india(num_of_trending_keywords)

      saved_model.statewise_tweets = json.dumps(sentiment_count_per_state)
      saved_model.datewise_tweets = json.dumps(datewise_sentiments)
      saved_model.trending_tweets = json.dumps(_trending_tweets)
      saved_model.trending_keywords = json.dumps(_trending_keywords)
      saved_model.save()

  def list(self, request, *args, **kwargs):
    user_referred_id = Token.objects.filter(key=self.request.headers['Authorization'].split()[1])[0].user.id
    analysis_model = Analysis.objects.filter(create_by_id=user_referred_id)
    serializer = self.get_serializer(analysis_model, many=True)
    return Response(serializer.data)

  def retrieve(self, request, pk=None):
    user_referred_id = Token.objects.filter(key=self.request.headers['Authorization'].split()[1])[0].user.id
    queryset = Analysis.objects.filter(create_by_id=user_referred_id)
    analysis = get_object_or_404(queryset, pk=pk)
    serializer = AnalysisRetrieveSerializer(analysis)

    response = {}
    for ser_data in serializer.data:
      response[ser_data] = serializer.data[ser_data]

    default_keywords = DefaultKeyword.objects.all()
    days_of_trending_tweets = DaysOfTrendingTweets.objects.get(id=1).value

    #sentiment_count_per_state = json.loads(serializer.data['statewise_tweets'])
    sentiment_count_per_state = json.loads(serializer.data['statewise_tweets'])
    datewise_sentiments = json.loads(serializer.data['datewise_tweets'])
    _total_sentiments = total_sentiments(sentiment_count_per_state)
    _total_indivudual_sentiments = total_indivudual_sentiments(sentiment_count_per_state)
    _tone_labels = get_tone_labels(sentiment_count_per_state)
    _total_sentiment_count_per_state = total_sentiment_count_per_state(sentiment_count_per_state)
    _total_sentiment_count_per_date = total_sentiment_count_per_date(datewise_sentiments)

    _max_sentiment = max_sentiment(_total_indivudual_sentiments)
    
    response['total_sentiments'] = _total_sentiments
    response['total_indivudual_sentiments'] = _total_indivudual_sentiments
    response['tone_labels'] = _tone_labels
    response['total_sentiment_count_per_state'] = _total_sentiment_count_per_state
    response['total_sentiment_count_per_date'] = _total_sentiment_count_per_date
    response['max_sentiment'] = _max_sentiment

    return Response(response)


class AnaylsisViewHome(RetrieveAPIView):

  permission_classes = [AllowAny]

  def retrieve(self, request, *args, **kwargs):
    default_keywords = DefaultKeyword.objects.all()
    num_of_tweets_per_default_keyword = NumOfTweetsPerState.objects.get(id=1).value
    days_of_trending_tweets = DaysOfTrendingTweets.objects.get(id=1).value
    num_of_tweets_per_day = NumOfTweetsPerDay.objects.get(id=1).value
    num_of_popular_tweets = NoOfPopularTweets.objects.get(id=1).value
    num_of_trending_keywords = NoOfTrendingKeywords.objects.get(id=1).value
    or_def_keyword = add_OR_in_strings(default_keywords)

    sentiment_count_per_state = []
    sentiment_count_per_state.append(statewise_sentiments.state_tweets(num_of_tweets_per_default_keyword, or_def_keyword))
#     try:
#       for default_keyword in default_keywords:
#         sentiment_count_per_state.append(statewise_sentiments.state_tweets(num_of_tweets_per_default_keyword, default_keyword.keyword))
#     except Exception:
#       print()
#       print()
#       print()
#       print('in sentiment_count_per_state exception')
#       print()
#       print()
#       print()
#       sentiment_count_per_state = [
#         { 'Andhra Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 0, 'analytical': 3, 'confident': 0, 'tentative': 0 }, 'Arunachal Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 4, 'analytical': 1, 'confident': 0, 'tentative': 1 }, 'Assam': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 1, 'confident': 1, 'tentative': 1 }, 'Bihar': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 0, 'analytical': 1, 'confident': 0, 'tentative': 1 }, 'Chandigarh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 1, 'confident': 1, 'tentative': 1 }, 'Chhattisgarh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Daman and Diu': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 1, 'confident': 0, 'tentative': 1 }, 'Delhi': { 'anger': 0, 'disgust': 0, 'fear': 2, 'joy': 2, 'sadness': 0, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Goa': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 3, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Gujarat': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Haryana': { 'anger': 0, 'disgust': 0, 'fear': 3, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Himachal Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 3, 'sadness': 1, 'analytical': 0, 'confident': 1, 'tentative': 2 }, 'Jammu and Kashmir': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Jharkhand': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 2, 'analytical': 3, 'confident': 0, 'tentative': 5 }, 'Karnataka': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 3, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Kerala': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Ladakh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 2, 'analytical': 1, 'confident': 1, 'tentative': 2 }, 'Lakshadweep': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 2, 'analytical': 1, 'confident': 2, 'tentative': 1 }, 'Madhya Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 0, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Maharashtra': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 1 }, 'Manipur': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 5 }, 'Meghalaya': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 2, 'confident': 1, 'tentative': 2 }, 'Mizoram': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Nagaland': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 2, 'confident': 0, 'tentative': 3 }, 'Odisha': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 2, 'analytical': 1, 'confident': 1, 'tentative': 0 }, 'Puducherry': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 4, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Punjab': { 'anger': 0, 'disgust': 0, 'fear': 1, 'joy': 1, 'sadness': 0, 'analytical': 1, 'confident': 1, 'tentative': 1 }, 'Rajasthan': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 5, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Sikkim': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 3, 'sadness': 0, 'analytical': 1, 'confident': 1, 'tentative': 2 }, 'Tamil Nadu': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 3, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Telangana': { 'anger': 1, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 1, 'confident': 1, 'tentative': 0 }, 'Tripura': { 'anger': 0, 'disgust': 0, 'fear': 1, 'joy': 1, 'sadness': 1, 'analytical': 3, 'confident': 0, 'tentative': 1 }, 'Uttar Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 0, 'confident': 5, 'tentative': 0 }, 'Uttarakhand': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 2 }, 'West Bengal': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 1, 'confident': 1, 'tentative': 0 } },
#         { 'Andhra Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 0, 'analytical': 3, 'confident': 0, 'tentative': 0 }, 'Arunachal Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 4, 'analytical': 1, 'confident': 0, 'tentative': 1 }, 'Assam': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 1, 'confident': 1, 'tentative': 1 }, 'Bihar': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 0, 'analytical': 1, 'confident': 0, 'tentative': 1 }, 'Chandigarh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 1, 'confident': 1, 'tentative': 1 }, 'Chhattisgarh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Daman and Diu': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 1, 'confident': 0, 'tentative': 1 }, 'Delhi': { 'anger': 0, 'disgust': 0, 'fear': 2, 'joy': 2, 'sadness': 0, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Goa': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 3, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Gujarat': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Haryana': { 'anger': 0, 'disgust': 0, 'fear': 3, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Himachal Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 3, 'sadness': 1, 'analytical': 0, 'confident': 1, 'tentative': 2 }, 'Jammu and Kashmir': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Jharkhand': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 2, 'analytical': 3, 'confident': 0, 'tentative': 5 }, 'Karnataka': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 3, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Kerala': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Ladakh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 2, 'analytical': 1, 'confident': 1, 'tentative': 2 }, 'Lakshadweep': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 2, 'analytical': 1, 'confident': 2, 'tentative': 1 }, 'Madhya Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 0, 'analytical': 0, 'confident': 3, 'tentative': 0 }, 'Maharashtra': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 1 }, 'Manipur': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 5 }, 'Meghalaya': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 2, 'confident': 1, 'tentative': 2 }, 'Mizoram': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Nagaland': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 2, 'confident': 0, 'tentative': 3 }, 'Odisha': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 2, 'analytical': 1, 'confident': 1, 'tentative': 0 }, 'Puducherry': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 4, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Punjab': { 'anger': 0, 'disgust': 0, 'fear': 1, 'joy': 1, 'sadness': 0, 'analytical': 1, 'confident': 1, 'tentative': 1 }, 'Rajasthan': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 5, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Sikkim': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 3, 'sadness': 0, 'analytical': 1, 'confident': 1, 'tentative': 2 }, 'Tamil Nadu': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 3, 'sadness': 0, 'analytical': 0, 'confident': 0, 'tentative': 0 }, 'Telangana': { 'anger': 1, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 1, 'confident': 1, 'tentative': 0 }, 'Tripura': { 'anger': 0, 'disgust': 0, 'fear': 1, 'joy': 1, 'sadness': 1, 'analytical': 3, 'confident': 0, 'tentative': 1 }, 'Uttar Pradesh': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 0, 'confident': 5, 'tentative': 0 }, 'Uttarakhand': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 2 }, 'West Bengal': { 'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 1, 'analytical': 1, 'confident': 1, 'tentative': 0 } },
#       ]
# 
    datewise_sentiments = []
    datewise_sentiments.append(statewise_sentiments.get_daily_tweets(or_def_keyword, num_of_tweets_per_day, days_of_trending_tweets))
#     try:
#       for default_keyword in default_keywords:
#         datewise_sentiments.append(statewise_sentiments.get_daily_tweets(default_keyword.keyword, num_of_tweets_per_default_keyword, days_of_trending_tweets))
#     except Exception:
#       print()
#       print()
#       print()
#       print('in datewise_sentiments exception')
#       print()
#       print()
#       print()
#       datewise_sentiments = [
#         {'02-07-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 1}, '01-07-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 3, 'analytical': 0, 'confident': 2, 'tentative': 1}, '30-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 4, 'sadness': 0, 'analytical': 0, 'confident': 4, 'tentative': 1}, '29-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 0, 'confident': 1, 'tentative': 2}, '28-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 1, 'tentative': 0}, '27-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 0, 'confident': 1, 'tentative': 0}, '26-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 1, 'analytical': 0, 'confident': 1, 'tentative': 0}},
#         {'02-07-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 0, 'tentative': 1}, '01-07-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 3, 'analytical': 0, 'confident': 2, 'tentative': 1}, '30-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 4, 'sadness': 0, 'analytical': 0, 'confident': 4, 'tentative': 1}, '29-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 0, 'analytical': 0, 'confident': 1, 'tentative': 2}, '28-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 2, 'sadness': 1, 'analytical': 0, 'confident': 1, 'tentative': 0}, '27-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 1, 'sadness': 0, 'analytical': 0, 'confident': 1, 'tentative': 0}, '26-06-2020': {'anger': 0, 'disgust': 0, 'fear': 0, 'joy': 0, 'sadness': 1, 'analytical': 0, 'confident': 1, 'tentative': 0}},
#       ]
# 
    _total_sentiments = total_sentiments(sentiment_count_per_state)
    _total_indivudual_sentiments = total_indivudual_sentiments(sentiment_count_per_state)
    _tone_labels = get_tone_labels(sentiment_count_per_state)
    _total_sentiment_count_per_state = total_sentiment_count_per_state(sentiment_count_per_state)
    _total_sentiment_count_per_date = total_sentiment_count_per_date(datewise_sentiments)

    _trending_tweets = get_trends.popular_tweets(add_OR_in_strings(default_keywords), num_of_popular_tweets)
    _trending_keywords = get_trends.trending_keywords_india(num_of_trending_keywords)

    return Response({
      'sentiment_count_per_state': sentiment_count_per_state,
      'total_sentiments': _total_sentiments,
      'total_indivudual_sentiments': _total_indivudual_sentiments,
      'tone_labels': _tone_labels,
      'total_sentiment_count_per_state': _total_sentiment_count_per_state,
      'total_sentiment_count_per_date': _total_sentiment_count_per_date,
      'trending_tweets': _trending_tweets,
      'trending_keywords': _trending_keywords
    })