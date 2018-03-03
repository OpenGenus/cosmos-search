import json
import hashlib
import hmac
import http.client
import git
import os

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt


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
        update_tags()


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
