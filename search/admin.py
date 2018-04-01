from django.contrib import admin

from search.models import Votes
from search.models import Comment

admin.site.register(Votes)
admin.site.register(Comment)
