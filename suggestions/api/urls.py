from django.urls import path
from .views import SuggestionsView

urlpatterns = [
  path('searchsuggestions/<searchterm>/', SuggestionsView.as_view()),
]