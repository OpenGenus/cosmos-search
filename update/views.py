import json, hashlib, hmac, http.client, json, git, os
from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

def update_metadata(updated_at):
    data = {'updated_at' : updated_at}
    for (dirpath, dirnames, filenames) in os.walk(settings.COSMOS_PATH):
        if dirnames == []:
            dirpath = '/'.join(dirpath.split('/')[2:])
            data[dirpath] = filenames
    with open(settings.METADATA_JSON, 'w') as f:
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
        update_metadata(updated_at)

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
