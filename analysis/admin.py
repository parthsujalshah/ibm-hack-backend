from django.contrib import admin
from .models import Analysis, Keyword, DefaultKeyword

admin.site.register(Analysis)
admin.site.register(Keyword)
admin.site.register(DefaultKeyword)