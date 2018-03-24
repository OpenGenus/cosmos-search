from . import views
from django.conf.urls import url

app_name = 'search'

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^query/', views.query, name='query'),
    url(r'^calculator/', views.calculator, name='calculator'),
    url(r'^check/$', views.check, name='check'),
    url(r'^fetch/$', views.fetch, name='fetch'),
]
