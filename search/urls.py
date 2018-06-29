from django.conf.urls import url
from search import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tags/', views.tags, name='tags'),
    url(r'^news/', views.news, name='news'),
    url(r'^lists/$', views.lists, name='lists'),
    url(r'^lists/(?P<foo>[\w\-]+)/$', views.lists_template, name='lists_template'),
    url(r'^query/', views.query, name='query'),
    url(r'^display', views.display, name='display'),
    url(r'^calculator/', views.calculator, name='calculator'),
]
