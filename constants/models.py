from django.db import models

class NumOfTweetsPerState(models.Model):
  description = models.CharField(max_length=200)
  value = models.IntegerField()

class NumOfTweetsPerDay(models.Model):
  description = models.CharField(max_length=200)
  value = models.IntegerField()

class DaysOfTrendingTweets(models.Model):
  description = models.CharField(max_length=200)
  value = models.IntegerField()

class NoOfPopularTweets(models.Model):
  description = models.CharField(max_length=200)
  value = models.IntegerField()

class NoOfTrendingKeywords(models.Model):
  description = models.CharField(max_length=200)
  value = models.IntegerField()