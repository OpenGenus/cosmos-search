from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
from bs4 import BeautifulSoup
import requests


# Create your views here.
def index(request):
    return render(request, 'cosmos/index.html')


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
        try:
            for f in v:
                if f.split('.')[-1] != 'md':
                    filtered_v.append(f)
        except TypeError:
            print('TypeError')
        if q in k:
            if filtered_v:
                path = k
                k = k.split('/')
                ans.append({'path': path, 'dirs': k, 'files': filtered_v})
                if len(k) == 2:
                    d = k[len(k)-2] + '/'
                else:
                    d = k[len(k)-3] + '/'
                for i, j in data.items():
                        if d in i:
                            if not q in i:
                                p = i
                                p = p.split('/')
                                l = p[len(p)-1]
                                rec.append({'recpath': i, 'recdirs':p, 'last': l})
    if not ans:
        return render(request, 'cosmos/notfound.html', {'query': query})
    shuffle(rec)
    return render(request, 'cosmos/searchresults.html',
                  {'amount': len(ans), 'result': ans, 'recommend': rec[0:5], 'query': query})

# search strategy
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
    if request.method == 'POST':
        display = request.POST.get('path')
        print display
    r = requests.get("https://raw.githubusercontent.com/OpenGenus/cosmos/master/code/artificial_intelligence/src/DBSCAN_Clustering/dbscan.py")
    pre = BeautifulSoup(r.text, 'html.parser')
    print "pre:"
    print pre
    file = open("search/templates/cosmos/data.html","w+")
    file.write(pre.text.encode('utf-8').strip())
    file.close()
    print "FUCK"
    return render(request, 'cosmos/data.html',{})
