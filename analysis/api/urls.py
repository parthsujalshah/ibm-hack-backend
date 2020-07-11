from django.urls import path, include
from .views import AnaylsisView, AnaylsisViewHome
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('', AnaylsisView)

urlpatterns = [
  path('user/', include(router.urls)),
  path('generic/', AnaylsisViewHome.as_view()),
]