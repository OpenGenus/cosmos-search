from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
import re
from newsapi import NewsApiClient
import requests
from search.models import News
from search.templatetags.calculator import getResult as calculate
from search.templatetags.youtube import youtube_search

COSMOS_SEP = '_'

# Create your views here


def dicToQueries(headlines, queries):
    count = 1
    for item in headlines["articles"]:
        for key, value in item.items():
            if key == "title":
                if value == None:
                    queries.filter(id=count).update(title="None")
                else:
                    queries.filter(id=count).update(title=value)
            if key == "description":
                if value == None:
                    queries.filter(id=count).update(description="None")
                else:
                    queries.filter(id=count).update(description=value)
            if key == "author":
                if value == None:
                    queries.filter(id=count).update(author="None")
                else:
                    queries.filter(id=count).update(author=value)
            if key == "url":
                queries.filter(id=count).update(url=value)
            if key == "urlToImage":
                if value == None:
                    queries.filter(id=count).update(urlToImage="None")
                else:
                    queries.filter(id=count).update(urlToImage=value)
        count += 1
    return queries


# News Page


def news(request):
    queries = News.objects.all()
    args = {"queries": queries}
    try:
        api = NewsApiClient(api_key='728bb1f02da34d37b4a5da9f67b87fbe')
        headlines = api.get_top_headlines(sources='techcrunch')
        if headlines["status"] == "ok":
            modified_queries = dicToQueries(headlines, queries)
            args = {"queries": modified_queries}
        else:
            args = {"queries": queries}
        return render(request, 'cosmos/news.html', args)
    except:
        return render(request, 'cosmos/news.html', args)


# Tags page for users


def tags(request):
    f = open(settings.TAGS_JSON, 'r')
    jsonL = sorted(list(json.load(f)))
    args = {"tags": jsonL}
    return render(request, 'cosmos/tags.html', args)

# To prefill the searchbar


def get_random_tag():
    jsonFile = open(settings.TAGS_JSON, 'r')
    algo_list = json.load(jsonFile)
    r_no = random.randint(0, len(algo_list) - 1)
    algo_tag = algo_list[r_no]
    return algo_tag


def searchSuggestion(request):
    jsonFile = open(settings.TAGS_JSON, 'r')
    algo_list = json.load(jsonFile)
    results = []
    if request.is_ajax():
        val = request.GET.get('term', '')
        filterData = []
        for word in algo_list:
            if word.startswith(val):
                filterData.append(word)
        i = 0
        for tag in filterData:
            tag_json = {}
            tag_json['id'] = filterData.index(tag)
            tag_json['label'] = tag
            tag_json['value'] = tag
            results.append(tag_json)
            i = i + 1
            if i >= 6:
                break
        searchTag = json.dumps(results)
    else:
        searchTag = 'fail'
    return searchTag


def index(request):
    randomTags = []
    for i in range(4):
        randomTags.append(get_random_tag())
    query = get_random_tag()
    algo = searchSuggestion(request)
    if request.is_ajax():
        mimetype = 'application/json'
        return HttpResponse(algo, mimetype)
    return render(request, 'cosmos/index.html', {'query': query, 'random': randomTags})


# Handlers for error pages
def error400(request):
    return render(request, 'cosmos/error/HTTP400.html')


def error403(request):
    return render(request, 'cosmos/error/HTTP403.html')


def error404(request):
    return render(request, 'cosmos/error/HTTP404.html')


def error500(request):
    return render(request, 'cosmos/error/HTTP500.html')


def is_file_extension_ignored(file_):
    return file_.split('.')[-1] in ['md', 'MD']


codes = None
videos = None
expression_result = None


def query(request):
    if request.is_ajax():
        return query_ajax(request)
    elif request.method == 'GET':
        return query_get(request)


def query_ajax(request):
    request_type = request.GET.get('type', '')
    mimetype = 'application/json'
    if request_type == 'video':
        query = request.GET.get('query', None)
        max_results = request.GET.get('max', 24)
        video_search(request, query, max_results)
        return HttpResponse(json.dumps(videos), mimetype)
    elif request_type == 'calculator':
        expression = request.GET.get('expression', None)
        calculator(request, expression)
        return HttpResponse(json.dumps(expression_result), mimetype)


def query_get(request):
    query = ' '.join(re.escape(request.GET['q'])
                     .replace('\ ', ' ')
                     .replace('\\', '')
                     .lower()
                     .split())
    calculator(request, query)
    code_search(request, query)
    video_search(request, query)

    if codes['code_amount'] or videos['video_amount'] or expression_result is not None:
        return render(request, 'cosmos/searchResults.html',
                      {'query': query,
                       'expression_result': expression_result,
                       'codes': codes,
                       'videos': videos,
                       'active_tab': (
                           'calculator' if expression_result is not None else
                           'code' if codes['code_amount'] else
                           'video' if videos['video_amount'] else
                           ''
                       )})
    else:
        return render(request, 'cosmos/notfound.html', {'query': query})


def code_search(request, query):
    global codes

    codes = {
        'codes': [],
        'code_amount': 0,
        'recommendations': [],
    }

    query = query.replace(' ', COSMOS_SEP)
    data = json.loads(open(settings.METADATA_JSON, 'r').readline())
    for folder, file in data.items():
        filtered_v = []
        for f in file:
            if not is_file_extension_ignored(f):
                filtered_v.append(f)
        if query in folder and "test" not in folder.split("/"):
            if filtered_v:
                path = folder
                folder_list = folder.split('/')
                codes['codes'].append({'path': path, 'dirs': folder_list, 'files': filtered_v})
                codes['code_amount'] += len(filtered_v)
                if len(folder_list) == 2:
                    d = folder_list[-2] + '/'
                else:
                    d = folder_list[-3] + '/'
                for i, j in data.items():
                    if d in i:
                        if query not in i:
                            only_contents_md = True
                            for f in j:
                                if not is_file_extension_ignored(f):
                                    only_contents_md = False
                                    break
                            if only_contents_md:
                                continue
                            p = i
                            p = p.split('/')
                            l = p[len(p) - 1]
                            codes['recommendations'].append(
                                {'recpath': i, 'recdirs': p, 'last': l})
    shuffle(codes['recommendations'])
    codes['recommendations'] = codes['recommendations'][:5]


def video_search(request, query='algorithm', max_results=24):
    global videos

    videos = {
        'videos': '',
        'video_amount': 0,
        'nextpage': None,
    }

    youtube_result = {}
    max_results = min(int(max_results), 50)
    nextpage = ''
    id_ = 0

    if request.is_ajax():
        q = query.split('&')
        query = q[0]
        nextpage = q[1]
        id_ = q[2]
    if len(query.split(" ")) == 1:
        query = query + '+' + 'algorithm'

    youtube_query = {
        'q': query.replace(' ', '+'),
        'max_results': max_results,
        'nextpage': nextpage,
        'id': id_
    }
    youtube_result = youtube_search(youtube_query)
    videos = {
        'videos': json.dumps(youtube_result['videos_Results']),
        'video_amount': len(youtube_result['videos_Results']),
        'nextpage': youtube_result['nextpage'],
    }


def calculator(request, expression):
    global expression_result
    res = calculate(expression)

    if expression is not None and isinstance(res, (int, float)):
        expression_result = round(res, 3)
    elif 'calculator' in expression:
        expression_result = 0
    else:
        expression_result = None


# Search strategy
def subsq(a, b, m, n):
    # Base Cases
    if m == 0:
        return True
    if n == 0:
        return False
    # If last characters of two strings are matching
    if a[m - 1] == b[n - 1]:
        return subsq(a, b, m - 1, n - 1)
    # If last characters are not matching
    return subsq(a, b, m, n - 1)


def display(request):
    path = request.GET['path']
    link = "https://www.github.com/OpenGenus/cosmos/blob/master/code/" + request.GET['link']
    raw = "https://raw.githubusercontent.com/OpenGenus/cosmos/master/code/" + request.GET['link']
    query = request.GET['query']
    r = requests.get(raw)
    return render(request, 'cosmos/code.html', {'code': r.text, 'link': link, 'query': query, 'path': path})
