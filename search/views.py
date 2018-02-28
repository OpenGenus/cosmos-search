from django.shortcuts import render
from django.conf import settings
import json
import random
from random import shuffle
import math
# Create your views here

# To prefill the searchbar
def searchbar():
    jsonFile = open('tags.json', 'r')
    data = json.load(jsonFile)
    algo_list = data['tags']
    r_no = random.randint(0,len(algo_list))
    algo_tag = algo_list[r_no]

    tabbed_algos=set()

    data = json.loads(open(settings.METADATA_JSON, 'r').readline())
    for k,v in data.items():
        if k!="updated_at":
            ans=k.split("/")[0].title().split("_")
            ans2=' '.join(ans)
            tabbed_algos.add(ans2)

    tabbed_algos_list=list(tabbed_algos)
    tabbed_algos_list.sort()
    return algo_tag,list(tabbed_algos_list)


def index(request):
    algo_tag,tabbed_algos = searchbar()
    return render(request,'cosmos/index.html',{'algo_name':algo_tag,'tabbed_algos':tabbed_algos[5:],'tabbed_algos_shortlist':tabbed_algos[:5]})





# Handlers for error pages
def error400(request):
    return render(request, 'cosmos/error/HTTP400.html')


def error403(request):
    return render(request, 'cosmos/error/HTTP403.html')


def error404(request):
    return render(request, 'cosmos/error/HTTP404.html')


def error500(request):
    return render(request, 'cosmos/error/HTTP500.html')

# Generate all combinations of a search literal
def generate_perm(query):

    # Use bitmasking to generate all cases where the first letter of a word in the query is capitalized.
    binary = []
    final = []

    n = len(query.split('_'))
    for i in range(pow(2,n)):
        b = bin(i)[2:].zfill(n)
        binary.append(b)


    # Create a query for the bitmask.

    for b in binary:
        perms = []
        count = 0
        for word in query.split('_'):
            if b[count] == '0':
                perms.append(word[0].lower() + word[1:]) 
            else:
                perms.append(word[0].upper() + word[1:] )
            count = count+1
        p='_'.join(perms)
        final.append(p)
      
    # Return the final list of queries to be passed to the query view.  
    return final


# Search query
def query(request):
    query = request.GET['q']
    q = query.replace(' ', '_')

    combs=generate_perm(q)

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
        
        for q in combs:
            # We do not want /test/ in the results if the user types in "test" in the searchbox
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
