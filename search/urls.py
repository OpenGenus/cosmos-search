from django.conf.urls import url
from search import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^query/', views.query, name='query'),
    url(r'^video/', views.video_search, name='video'),
    url(r'^display', views.display, name='display'),
    url(r'^calculator/', views.calculator, name='calculator'),
]
