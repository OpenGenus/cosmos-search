from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
import re

COSMOS_SEP = '_'


# Create your views here


# To prefill the searchbar
def get_random_tag():
    jsonFile = open(settings.TAGS_JSON, 'r')
    data = json.load(jsonFile)
    algo_list = data['tags']
    r_no = random.randint(0, len(algo_list) - 1)
    algo_tag = algo_list[r_no]
    return algo_tag


def searchSuggestion(request):
    jsonFile = open(settings.TAGS_JSON, 'r')
    data = json.load(jsonFile)
    algo_list = list(data['tags'])
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
    algo_tag = get_random_tag()
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


def is_file_extension_ignored(file_):
    return file_.split('.')[-1] in ['md', 'MD']


# Search query
def query(request):
    query = re.escape(request.GET['q']).replace('\ ', ' ')
    q = query.replace(' ', COSMOS_SEP)
    data = json.loads(open(settings.METADATA_JSON, 'r').readline())
    ans = []
    rec = []
    amount = 0
    for folder, file in data.items():
        filtered_v = []
        try:
            for f in file:
                if not is_file_extension_ignored(f):
                    filtered_v.append(f)
        except TypeError:
            print('TypeError')
        if q in folder and "test" not in folder.split("/"):
            if filtered_v:
                path = folder
                folder_list = folder.split('/')
                ans.append({'path': path, 'dirs': folder_list, 'files': filtered_v})
                amount += len(filtered_v)
                if len(folder_list) == 2:
                    d = folder_list[len(folder_list) - 2] + '/'
                else:
                    d = folder_list[len(folder_list) - 3] + '/'
                for i, j in data.items():
                    if d in i:
                        if q not in i:

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
                      {'amount': amount,
                       'result': ans,
                       'recommend': rec[0:5],
                       'query': query,
                       'algo_name': query
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
