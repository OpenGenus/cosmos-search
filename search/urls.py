from django.conf.urls import url
from search import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^query/', views.query, name='query'),
    url(r'^$', views.index1, name='index1'),
    url(r'^query1/', views.query1, name='query1'),
]
