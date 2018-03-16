from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
import re
import requests
import bs4
from django.views.decorators.cache import cache_page

COSMOS_SEP = '_'


# Create your views here


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


@cache_page(60 * 15)
# Search query
def query(request):
    query = re.escape(request.GET['q']).replace('\ ', ' ')
    q = query.replace(' ', COSMOS_SEP)
    data = json.loads(open(settings.METADATA_JSON, 'r').readline())
    ans = []
    rec = []
    links = []
    headings = []
    amount = 0
    links, headings = search_results_from_sites(request)
    mylist = zip(links, headings)
    for folder, file in data.items():
        filtered_v = []
        for f in file:
            if not is_file_extension_ignored(f):
                filtered_v.append(f)
        if q in folder and "test" not in folder.split("/"):
            if filtered_v:
                path = folder
                folder_list = folder.split('/')
                ans.append({'path': path, 'dirs': folder_list, 'files': filtered_v})
                amount += len(filtered_v)
                if len(folder_list) == 2:
                    d = folder_list[-2] + '/'
                else:
                    d = folder_list[-3] + '/'
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
                            l = p[-1]
                            rec.append({'recpath': i, 'recdirs': p, 'last': l})
    if not ans:
        return render(request, 'cosmos/notfound.html', {'query': query, 'mylist': mylist })
    shuffle(rec)
    if request.is_ajax():
        algo = searchSuggestion(request)
        mimetype = 'application/json'
        return HttpResponse(algo, mimetype)
    else:
        return render(request, 'cosmos/searchresults.html',
                      {'amount': amount,
                       'result': ans,
                       'recommend': rec[:5],
                       'query': query,
                       'algo_name': query,
                       'mylist': mylist
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


def search_results_from_sites(request):
    keyword = request.GET['q']
    keyword.replace(' ', '+')
    res = requests.get('https://google.com/search?q=' + keyword)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    links = soup.select('.r a')
    link_list = []
    heading_list = []
    tab_counts = min(50, len(links))
    count = 0
    l = ["wikipedia", "tutorialspoint"]
    for i in range(tab_counts):
        link = 'https://google.com' + links[i].get('href')
        for j in l:
            if j in link:
                if count == 0:
                    count = count + 1
                else:
                    link_list.append(link)
                    heading_list.append(links[i].text)
    keyword = keyword + '+stackoverflow'
    res = requests.get('https://google.com/search?q=' + keyword)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    links = soup.select('.r a')
    tab_counts = min(5, len(links))

    for i in range(tab_counts):
        link = 'https://google.com' + links[i].get('href')
        if 'stackoverflow.com' in link:
            link_list.append(link)
            heading_list.append(links[i].text)
    return link_list, heading_list
