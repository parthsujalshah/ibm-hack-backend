from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
import requests
from rest_framework.response import Response

class SuggestionsView(RetrieveAPIView):

  permission_classes = [IsAuthenticated]
  
  def retrieve(self, request, *args, **kwargs):
    url = "http://suggestqueries.google.com/complete/search"
    params = {
      "client":'firefox',
      "q": kwargs['searchterm'],
    }
    suggestions = requests.get(url, params=params).json()[1]
    response_list = []
    for suggestion in suggestions:
      response_list.append({'value': suggestion})
    return Response(response_list)