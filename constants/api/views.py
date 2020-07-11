from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from ..models import *

class GetAllConstantsView(RetrieveAPIView):
  def retrieve(self, request, *args, **kwargs):
    response = NumOfTweetsPerState.objects.get(id=1).value * 36 + NumOfTweetsPerDay.objects.get(id=1).value * DaysOfTrendingTweets.objects.get(id=1).value + NoOfPopularTweets.objects.get(id=1).value
    return Response(response)