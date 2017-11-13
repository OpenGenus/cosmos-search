from django.conf.urls import url
from update import views

urlpatterns = [
    url(r'^$', views.github_webhook, name='github_webhook'),
]
