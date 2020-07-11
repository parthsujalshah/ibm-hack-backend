from django.contrib import admin
from .models import *

admin.site.register(NumOfTweetsPerDay)
admin.site.register(DaysOfTrendingTweets)
admin.site.register(NoOfPopularTweets)
admin.site.register(NoOfTrendingKeywords)
admin.site.register(NumOfTweetsPerState)