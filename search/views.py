from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle


# Create your views here


# To prefill the searchbar
def searchbar():
    jsonFile = open(settings.TAGS_JSON, 'r')
    algo_list = json.load(jsonFile)
    r_no = random.randint(0, len(algo_list))
    algo_tag = algo_list[r_no]
    return algo_tag


def searchSuggestion(request):
    jsonFile = open(settings.TAGS_JSON, 'r')
    algo_list = json.load(jsonFile)
    filterData = []
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
    algo_tag = searchbar()
    algo = searchSuggestion(request)
    if request.is_ajax():
        mimetype = 'application/json'
        return HttpResponse(algo, mimetype)
    return render(request, 'cosmos/index.html', {'algo_name': algo_tag})


# Handlers for error pages
def error400(request):
    return render(request, 'cosmos/error/HTTP400.html')


def error403(request):
    return render(request, 'cosmos/error/HTTP403.html')


def error404(request):
    return render(request, 'cosmos/error/HTTP404.html')


def error500(request):
    return render(request, 'cosmos/error/HTTP500.html')


# Search query
def query(request):
    query = request.GET['q']
    q = query.replace(' ', '_')
    data = json.loads(open(settings.METADATA_JSON, 'r').readline())
    ans = []
    rec = []
    for k, v in data.items():
        filtered_v = []
        for f in v:
            if f.split('.')[-1] != 'md':
                filtered_v.append(f)
        if q in k and "test" not in k.split("/"):
            if filtered_v:
                path = k
                k = k.split('/')
                ans.append({'path': path, 'dirs': k, 'files': filtered_v})
                if len(k) == 2:
                    d = k[len(k) - 2] + '/'
                else:
                    d = k[len(k) - 3] + '/'
                for i, j in data.items():
                    if d in i:
                        if q not in i:
                            p = i
                            p = p.split('/')
                            l = p[len(p) - 1]
                            rec.append({'recpath': i, 'recdirs': p, 'last': l})
    if not ans:
        return render(request, 'cosmos/notfound.html', {'query': query})
    shuffle(rec)
    if request.is_ajax():
        algo = searchSuggestion(request)
        mimetype = 'application/json'
        return HttpResponse(algo, mimetype)
    else:
        return render(request, 'cosmos/searchresults.html',
                      {'amount': len(ans),
                       'result': ans,
                       'recommend': rec[0:5],
                       'query': query
                       })


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
