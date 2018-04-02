from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.conf import settings
import json
import random
from random import shuffle
import re
from search.models import Votes
from search.models import Comment
from search.templatetags.calculator import getResult
from search.form import VotesForm
from search.form import CommentForm

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


# Search query
def query(request):
    global algo_name, title
    ans = []
    rec = []
    amount = 0
    query = request.GET['q']
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

        q = query.replace(' ', COSMOS_SEP)
        data = json.loads(open(settings.METADATA_JSON, 'r').readline())
        for folder, file in data.items():
            filtered_v = []
            for f in file:
                if not is_file_extension_ignored(f):
                    filtered_v.append(f)
            if q in folder and "test" not in folder.split("/"):
                if filtered_v:
                    path = folder
                    avg_vote = fetch(request, path)
                    comment = comment_fetch(request, path)
                    folder_list = folder.split('/')
                    ans.append({'path': path, 'dirs': folder_list,
                                'files': filtered_v,
                                'avg_vote': avg_vote,
                                'comment': comment, })
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

        vote_form = VotesForm()
        return render(request, 'cosmos/searchresults.html',
                      {'amount': amount,
                       'title': title,
                       'result': ans,
                       'recommend': rec[:5],
                       'query': query,
                       'result_val': exprResult,
                       'algo_name': algo_name,
                       'vote_form': vote_form
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


def check(request):
    if request.method == 'POST':
        vote_form = VotesForm(request.POST)
        if vote_form.is_valid():
            vote_form.save()
            return redirect('search:index')
    else:
        vote_form = VotesForm()
    return render(request, 'cosmos/index.html', {'vote_form': vote_form})


def fetch(request, query):
    data = []
    count = 0
    data = Votes.objects.filter(project_name=query)
    z = len(data)
    if(z == 0):
        avg_vote = 4.9
    else:
        for vote in data:
            count = count + int(vote.vote_value)
        avg_vote = round(count / z, 1)
    return avg_vote


def comment_fetch(request, query):
    c = []
    data = Comment.objects.filter(project_name=query)
    for comment in data:
        c.append(comment.comment)
    return c


def comment(request):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.save()
            return redirect('search:index')
    else:
        comment_form = CommentForm()
    return render(request, 'cosmos/index.html', {'comment_form': comment_form})
