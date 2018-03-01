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
    jsonFile = open('tags.json', 'r')
    data = json.load(jsonFile)
    algo_list = data['tags']
    r_no = random.randint(0, len(algo_list) - 1)
    algo_tag = algo_list[r_no]
    return algo_tag


def index(request):
    algo_tag = get_random_tag()
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
                if f.split('.')[-1] != 'md':
                    filtered_v.append(f)
        except TypeError:
            print('TypeError')
        if q in folder:
            if filtered_v:
                path = folder
                folder = folder.split('/')
                ans.append({'path': path, 'dirs': folder, 'files': filtered_v})
                amount += len(filtered_v)
                if len(folder) == 2:
                    d = folder[len(folder) - 2] + '/'
                else:
                    d = folder[len(folder) - 3] + '/'
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
    return render(request, 'cosmos/searchresults.html',
                  {'amount': amount, 'result': ans, 'recommend': rec[0:5],
                   'query': query.split(' '), 'algo_name': query,
                   'amount_is_plural': amount > 1})


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
