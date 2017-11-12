from django.shortcuts import render
import json


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
    fo = open('metadata.json', 'r')
    s = fo.readline()
    data = json.loads(s)
    ans = []
    for (k, v) in data.items():
        a = q.lower()
        b = k.lower()
        if subsq(a, b, len(a), len(b)):
            path = k
            k = k.split('/')[1:]
            ans.append({'path': path, 'dirs': k, 'files': v})
    if (ans == []):
        return render(request, 'cosmos/notfound.html', {'query': query})
    return render(request, 'cosmos/searchresults.html', {'amount': len(ans), 'result': ans, 'query': query})


# search strategy
def subsq(a, b, m, n):
    # Base Cases
    if m == 0:    return True
    if n == 0:    return False
    # If last characters of two strings are matching
    if a[m - 1] == b[n - 1]:
        return subsq(a, b, m - 1, n - 1)
    # If last characters are not matching
    return subsq(a, b, m, n - 1)
