from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
import re
from wikiapi import WikiApi
from search.templatetags.calculator import getResult
import bs4
import requests


COSMOS_SEP = '_'


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


# calculator
def calculator(request):
    global exprResult
    if request.method == 'POST':
        q = request.POST.get('txt')
        if q is not None:
            getResult(q)
            res = getResult(q)
            if type(res) == int or type(res) == float:
                exprResult = round(res, 3)
            else:
                exprResult = 'Error'
    else:
        exprResult = None
        q = None
    return render(request, 'cosmos/searchresults.html',
                  {'title': 'Calculator',
                   'query': q,
                   'result_val': exprResult,
                   })


def is_file_extension_ignored(file_):
    return file_.split('.')[-1] in ['md', 'MD']


def stackoverflow(query):
    result = []
    query = query.replace(" ", "+")
    query += "algorithm+Google+site:stackoverflow.com"
    data = requests.get('https://www.google.co.in/search?q=' + query)
    k = 0
    soup = bs4.BeautifulSoup(data.text, 'html.parser')
    for x in soup.find_all('a'):
        k = k + 1
        str1 = x.get('href')
        if str1.startswith("/url?q=https://stackoverflow.com/"):
            res = {"title": ''.join(x.findAll(text=True)),
                   "url": str1.split("/url?q=")[1]
                   }
            result.append(res)
            if len(result) > 4:
                break
    return result


def wiki(query):
    wiki = WikiApi()
    wiki_temp = wiki.find(query)
    if(len(wiki_temp) != 0):
        wiki_res1 = wiki.get_article(wiki_temp[0])
        return wiki_res1
    else:
        wiki_te = wiki.find('Barack Obama')
        wiki_res1 = wiki.get_article(wiki_te[0])
        wiki_res1.heading = '404_NOT_FOUND'
        wiki_res1.url = '#'
        return wiki_res1


def tutorialpoint(query):
    query = query.replace(" ", "+")
    query += "tutorial+point"
    data = requests.get('https://www.google.co.in/search?q=' + query)
    soup = bs4.BeautifulSoup(data.text, 'html.parser')
    final = None
    k = 0
    for x in soup.find_all('a', {'href': re.compile('https://www.tutorialspoint.com/')}):
        k += 1
        str1 = x.get('href')
        str1 = str1.split("htm")[0]
        str1 = str1 + 'htm'
        p = list(str1)
        s1 = str1.find("http")
        s2 = str1.find(".htm")
        s3 = str1.find(".asp")
        t = []
        if (s2 != -1):
            for i in range(s1, s2 + 4):
                t.append(p[i])
            final = ''.join(t)

        else:
            for i in range(s1, s3 + 4):
                t.append(p[i])
            final = ''.join(t)
        if final:
            break
    return final


def query(request):
    global algo_name, title
    if request.method == 'GET':
        query = re.escape(request.GET['q']).replace('\ ', ' ')
        if '\\' in query:
            query = query.replace('\\', '')
        res = getResult(query)
        if type(res) == int or type(res) == float:
            exprResult = round(res, 3)
            title = "Calculator"
            algo_name = ""
        else:
            exprResult = None
        query = ' '.join(query.split())

        q = query.replace(' ', COSMOS_SEP)
        data = json.loads(open(settings.METADATA_JSON, 'r').readline())
        ans = []
        rec = []
        amount = 0
        for folder, file in data.items():
            filtered_v = []
            for f in file:
                if not is_file_extension_ignored(f):
                    filtered_v.append(f)
            if q in folder and "test" not in folder.split("/"):
                if filtered_v:
                    stk_res = []
                    path = folder
                    folder_list = folder.split('/')
                    # print(folder_list[-1])
                    wiki_res = wiki(folder_list[-1])
                    tut_res = tutorialpoint(folder_list[-1])
                    stk_res = stackoverflow(folder_list[-1])
                    ans.append({'path': path, 'dirs': folder_list,
                                'files': filtered_v,
                                'wiki': wiki_res,
                                'stack': stk_res,
                                'tut': tut_res})
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
                                    l = p[len(p) - 1]
                                    rec.append({'recpath': i, 'recdirs': p, 'last': l})

        if not ans and exprResult is None:
            return render(request, 'cosmos/notfound.html', {'query': query})

        if ans:
            algo_name = query
            title = query

        if ans and exprResult:
            amount += 1

        shuffle(rec)
        return render(request, 'cosmos/searchresults.html',
                      {'amount': amount,
                       'title': title,
                       'result': ans,
                       'recommend': rec[:5],
                       'query': query,
                       'result_val': exprResult,
                       'algo_name': algo_name,
                       'res_stack': stk_res,
                       'res_wiki': wiki_res,
                       'res_tut': tut_res
                       })

    elif request.method == 'POST':
        calculator(request)

    if request.is_ajax():
        algo = searchSuggestion(request)
        mimetype = 'application/json'
        return HttpResponse(algo, mimetype)


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
    display = "https://raw.githubusercontent.com/OpenGenus/cosmos/master/code/" + path
    r = requests.get(display)
    path = path.replace('_', ' ')
    path = path.replace('.', ' in ')
    l = path.split('/')
    if 'src' in l:
        l.remove('src')
    return render(request, 'cosmos/data.html', {'code': r.text, 'path': l})
