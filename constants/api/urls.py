from django.urls import path
from .views import GetAllConstantsView

urlpatterns = [
  path('all/', GetAllConstantsView.as_view()),
]