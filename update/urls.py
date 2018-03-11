from django.conf.urls import url
from update import views

urlpatterns = [
    url(r'^github_webhook$', views.github_webhook, name='github_webhook'),
]
