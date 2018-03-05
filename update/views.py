import json
import hashlib
import hmac
import http.client
import git
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt


def get_file_context(filename):
    '''
    :param filename: name of file
    :type filename: str
    :return: context of the file if file can be opened else empty string
    '''

    context = ''

    try:
        with open(filename, 'r') as f:
            context = f.read()
    except OSError:
        pass

    return context


def get_json_from_file(filename, default_={}):
    '''
    :param filename: name of file
    :type filename: str
    :param default_: the default json
    :type default_: json
    :return: json of context of the file if file can be opened else default
    '''

    context = get_file_context(filename)

    if context:
        default_ = json.loads(context)

    return default_


def update_kv_to_json(key, value, json_):
    '''
    :param key: list for keys by layer or key
    :type key: list or any type for json key
    :param json_:
    :type json_: json
    :return: elem which containing the key in json_
    '''

    if isinstance(key, list) and len(key) > 1:
        j = json_
        # the key of int will be str in json
        k = str(key[0])
        if k not in json_:
            j[k] = {}
        j = j[k]
        update_kv_to_json(key[1:], value, j)

    elif isinstance(key, list) and len(key) == 1:
        json_[key[0]] = value

    else:
        json_[key] = value


def update_kv_to_file(key, value, filename):
    '''
    :param key: list for keys by layer or key
    :type key: list or any type for json key
    :param value:
    :type value: any type for json key
    :param filename:
    :type filename: str

    TODO: update value of list
    '''

    json_ = get_json_from_file(filename)

    update_kv_to_json(key, value, json_)

    with open(filename, 'w') as f:
        json.dump(json_, f)


def update_metadata():
    data = {}
    for (dirpath, dirnames, filenames) in os.walk(settings.COSMOS_PATH):
        if dirnames == []:
            dirpath = '/'.join(dirpath.split('/')[2:])
            data[dirpath] = filenames
    with open(settings.METADATA_JSON, 'w') as f:
        json.dump(data, f)


def update_tags():
    topics = []
    for keys in json.load(open(settings.METADATA_JSON)):
        for topic in keys.split('/'):
            if topic not in (topics + ['unclassified', 'src', 'updated_at', 'test']):
                topics.append(topic)
    data = list(map(lambda v: v.replace('_', ' ').replace('-', ' ').lower(), topics))
    with open(settings.TAGS_JSON, 'w') as f:
        json.dump(data, f)


def manage_webhook_event(event, payload):

    """Simple webhook handler that prints the event and payload to the console"""

    if event == 'push':
        updated_at = payload['repository']['pushed_at']
        try:
            repo = git.Repo(settings.COSMOS_PATH)
            o = repo.remotes.origin
            print("Pulling cosmos!")
            o.pull()
            print("Pulling done!")
        except git.exc.NoSuchPathError:
            print("Cloning cosmos!")
            git.Git().clone(settings.COSMOS_LINK)
            print("Cloning done!")
        update_metadata()
        update_kv_to_file(settings.METADATA_JSON, updated_at, settings.TIMESTAMPS_JSON)
        update_tags()
        update_kv_to_file(settings.TAGS_JSON, updated_at, settings.TIMESTAMPS_JSON)


@csrf_exempt
def github_webhook(request):
    github_signature = request.META['HTTP_X_HUB_SIGNATURE']
    signature = hmac.new(settings.GITHUB_WEBHOOK_SECRET, request.body, hashlib.sha1)
    expected_signature = 'sha1=' + signature.hexdigest()
    if not hmac.compare_digest(github_signature, expected_signature):
        return HttpResponseForbidden('Invalid signature header')
    if 'payload' in request.POST:
        payload = json.loads(request.POST['payload'])
    else:
        payload = json.loads(request.body)
    event = request.META['HTTP_X_GITHUB_EVENT']
    manage_webhook_event(event, payload)
    return HttpResponse('Webhook received', status=http.client.ACCEPTED)
