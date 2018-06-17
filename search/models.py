from django.db import models  # noqa

# Create your models here.


class News(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=200)
    url = models.URLField(max_length=200)
    urlToImage = models.URLField(max_length=200)
