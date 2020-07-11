from rest_framework.serializers import ModelSerializer
from ..models import Analysis, Keyword

class KeywordCreateSerializer(ModelSerializer):
  class Meta:
    model = Keyword
    fields = ['keyword']

class KeywordListSerializer(ModelSerializer):
  class Meta:
    model = Keyword
    fields = ['keyword']

class AnalysisListSerializer(ModelSerializer):
  class Meta:
    model = Analysis
    fields = ['id', 'title', 'description']

class AnalysisCreateSerializer(ModelSerializer):

  keywords = KeywordCreateSerializer(many=True)

  class Meta:
    model = Analysis
    fields = ['title', 'description', 'keywords']

  def create(self, validated_data):
    keyword_validated_data = validated_data.pop('keywords')
    analysis = Analysis.objects.create(**validated_data)
    keywords_serializer = self.fields['keywords']
    for each in keyword_validated_data:
      each['analysis'] = analysis
    keywords_set = keywords_serializer.create(keyword_validated_data)
    return analysis

class AnalysisRetrieveSerializer(ModelSerializer):

  keywords = KeywordListSerializer(many=True)

  class Meta:
    model = Analysis
    fields = [
      'id',
      'title',
      'description',
      'date_created',
      'create_by',
      'statewise_tweets',
      'datewise_tweets',
      'trending_tweets',
      'trending_keywords',
      'keywords'
    ]