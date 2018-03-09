from django.http import HttpResponse
from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
import re
import math

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


# expression computation
class Stack:
    def __init__(self):
        self.item = []

    def isEmpty(self):
        return self.item == []

    def push(self, T):
        self.item.insert(0, T)

    def pop(self):
        return self.item.pop(0)

    def peek(self):
        return self.item[0]

    def size(self):
        return len(self.item)


def isMathExpression(expr, op_math):
    token = []
    i = 0
    while i < len(expr):
        if expr[i] == ' ':
            i += 1
        if expr[i] == '+' and ((len(token) > 0 and token[-1] == '(') or i == 0):
            token.append('u+')
            i += 1
        elif expr[i] == '-' and ((len(token) > 0 and token[-1] == '(') or i == 0):
            token.append('u-')
            i += 1
        elif expr[i].isdigit() or expr[i] == '.':
            j = i
            flot = 0
            while j < len(expr) and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if flot == 0:
                        flot = 1
                    else:
                        return False
                j += 1
            try:
                val = int(expr[i:j])
            except ValueError:
                val = float(expr[i:j])
            token.append(val)
            i = j

        elif expr[i] == '(' and len(token) > 0 and (str(token[-1]).isdigit() or token[-1] == ')'):
            token.append('*')

        elif expr[i] == '(' or expr[i] == ')' or expr[i] == '+' or \
                expr[i] == '*' or expr[i] == '-' or expr[i] == '/' or \
                expr[i] == '%' or expr[i] == '^':
            token.append(expr[i])
            i += 1

        elif expr[i] == 'x' or expr[i] == 'X':
            token.append('*')
            i += 1

        elif expr[i:i + 5].lower() in op_math:
            token.append(expr[i:i + 5].lower())
            if i + 5 >= len(expr):
                return False
            elif expr[i + 5] != '(':
                return False
            i += 5

        elif expr[i:i + 4].lower() in op_math:
            token.append(expr[i:i + 4].lower())
            if i + 4 >= len(expr):
                return False
            elif expr[i + 4] != '(':
                return False
            i += 4

        elif expr[i:i + 3].lower() in op_math:
            token.append(expr[i:i + 3].lower())
            if i + 3 >= len(expr):
                return False
            elif expr[i + 3] != '(':
                return False
            i += 3

        else:
            return False
    return token


def calculate(val1, val2, op):
    if op == 'u-':
        return -val1
    if op == 'u+':
        return val1
    if op == '^':
        return math.pow(val1, val2)
    if op == '+':
        return val1 + val2
    if op == '-':
        return val1 - val2
    if op == '*':
        return val1 * val2
    if op == '/':
        return val1 / val2
    if op == '%':
        return val1 % val2
    if op == 'sin':
        return math.sin(val1)
    if op == 'cos':
        return math.cos(val1)
    if op == 'tan':
        return math.tan(val1)
    if op == 'cot':
        return 1 / math.tan(val1)
    if op == 'cosec':
        return 1 / math.sin(val1)
    if op == 'sec':
        return 1 / math.cos(val1)
    if op == 'exp':
        return math.exp(val1)
    if op == 'sqrt':
        return math.sqrt(val1)
    if op == 'log':
        return math.sqrt(val1)


def check_precedence(opr, i, op_precdn, op_math):
    if opr in op_precdn and i in op_math:
        return True
    if op_precdn.index(opr) <= 2:
        return True
    if op_precdn.index(opr) <= 5:
        return op_precdn.index(i) > 2
    else:
        return op_precdn.index(i) > 5


def evaluate(tokens, op_precdn, op_math):
    value = Stack()
    operator = Stack()
    open_bracket = 0
    for i in tokens:
        if i == '(':
            open_bracket = open_bracket + 1
            operator.push(i)
        elif i == ')':
            if open_bracket > 0:
                while operator.peek() != '(':
                    opr = operator.pop()
                    if opr in op_math or opr == 'u+' or opr == 'u-':
                        try:
                            val = value.pop()
                            value.push(calculate(val, -1, opr))
                        except IndexError:
                            return False
                    elif opr in op_precdn:
                        try:
                            val2 = value.pop()
                            val1 = value.pop()
                            value.push(calculate(val1, val2, opr))
                        except IndexError:
                            return False
                operator.pop()
                open_bracket -= 1
            else:
                return False
        elif i not in op_math and i not in op_precdn:
            value.push(i)
        else:
            if operator.isEmpty():
                operator.push(i)
            else:
                opr = operator.peek()
                if opr == '(':
                    operator.push(i)
                elif opr in op_math or opr == 'u+' or opr == 'u-':
                    if not value.isEmpty():
                        try:
                            val = value.pop()
                            operator.pop()
                            operator.push(i)
                            value.push(calculate(val, -1, opr))
                        except IndexError:
                            return False
                elif opr in op_precdn:
                    if value.size() > 1:
                        if check_precedence(opr, i, op_precdn, op_math) and \
                                not ((i == '^' or i in op_math) and opr == '^'):
                            try:
                                val2 = value.pop()
                                val1 = value.pop()
                                operator.pop()
                                value.push(calculate(val1, val2, opr))
                            except IndexError:
                                return False
                            operator.push(i)
                        else:
                            operator.push(i)
                    else:
                        operator.push(i)
                else:
                    return False

    while value.size() != 0 and operator.size() != 0:
        opr = operator.peek()
        if opr in op_math or opr == 'u+' or opr == 'u-':
            val = value.pop()
            operator.pop()
            try:
                value.push(calculate(val, -1, opr))
            except IndexError:
                return False
        else:
            if value.size() > 1:
                try:
                    val2 = value.pop()
                    val1 = value.pop()
                    operator.pop()
                    value.push(calculate(val1, val2, opr))
                except IndexError:
                    return False
            else:
                break

    if value.size() == 1 and operator.size() == 0:
        return value.peek()
    else:
        return False


def getResult(expr):
    op_precdn = ['u+', 'u-', '^', '/', '*', '%', '+', '-']
    op_math = ['sin', 'cos', 'cosec', 'tan', 'sec', 'cot', 'exp', 'sqrt', 'log']
    tokens = isMathExpression(expr, op_math)
    if tokens:
        return evaluate(tokens, op_precdn, op_math)
    else:
        return False


# calculator
def calculator(request):
    q = request.POST.get('txt')
    if q is not None:
        getResult(q)
        res = getResult(q)
        if type(res) == int or type(res) == float:
            exprResult = round(res, 3)
        else:
            exprResult = 'NaN'
        return exprResult
    return 'NaN'


def is_file_extension_ignored(file_):
    return file_.split('.')[-1] in ['md', 'MD']


# Search query
def query(request):
    if request.method == 'GET':
        try:
            query = re.escape(request.GET['q']).replace('\ ', ' ')
        except Exception:
            return render(request, 'cosmos/searchresults.html',
                          {'result': None,
                           'title': "Calculator",
                           'recommend': None,
                           'query': None,
                           'result_val': None,
                           'algo_name': ""
                           })

        if '\\' in query:
            query = query.replace('\\', '')

        res = getResult(query)
        if type(res) == int or type(res) == float:
            exprResult = round(res, 3)
        else:
            exprResult = None

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
                                    l = p[len(p) - 1]
                                    rec.append({'recpath': i, 'recdirs': p, 'last': l})

        if not ans and exprResult is None:
            return render(request, 'cosmos/notfound.html', {'query': query})

        if exprResult is not None:
            title = "Calculator"
            algo_name = ""
        else:
            title = query
            algo_name = query

        shuffle(rec)
        return render(request, 'cosmos/searchresults.html',
                      {'amount': amount,
                       'title': title,
                       'result': ans,
                       'recommend': rec[:5],
                       'query': query,
                       'result_val': exprResult,
                       'algo_name': algo_name
                       })

    elif request.method == 'POST':
        exprResult = calculator(request)
        q = request.POST.get('txt')
        return render(request, 'cosmos/searchresults.html',
                      {'result': None,
                       'recommend': None,
                       'title': "Calculator",
                       'query': q,
                       'result_val': exprResult,
                       'algo_name': ""
                       })

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
