from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.urls import reverse
from requests_oauthlib import OAuth1Session
import pytumblr

ConsumerKey = 'ZcuvHMdmd9R7fJ34JQIUrF5C0pGiRVgwqNPQsYfk2ddaZ2aT6C'
ConsumerSecret = 'AgRQTuZ7ycvL50VDj1LPJBEpaLMwg9tlXIjUx6XQ4XzBIc57bZ'

request_token_url = 'https://www.tumblr.com/oauth/request_token'
authorization_base_url = 'https://www.tumblr.com/oauth/authorize'
access_token_url = 'https://www.tumblr.com/oauth/access_token'
call_back_url = 'http://207.246.82.64/tumblr/oauth/'

tumblr = OAuth1Session(ConsumerKey, client_secret=ConsumerSecret, callback_uri=call_back_url)


def tumblrinit(request):
    tumblr.fetch_request_token(request_token_url)
    authorization_url = tumblr.authorization_url(authorization_base_url)
    return HttpResponseRedirect(authorization_url)


def tumblroauth(request):
    redirect_response = request.get_full_path()

    tumblr.parse_authorization_response(redirect_response)
    tumblr.fetch_access_token(access_token_url)
    request.session['Owner_key'] = tumblr.auth.client.resource_owner_key
    request.session['Owner_secret'] = tumblr.auth.client.resource_owner_secret

    return HttpResponseRedirect(reverse('tumblr_main'))


def tumblrmain(request):
    Owner_key = request.session.get('Owner_key', 0)
    Owner_secret = request.session.get('Owner_secret', 0)
    if Owner_key == 0:
        return HttpResponseRedirect(reverse('tumblr'))
    tumblr_client = pytumblr.TumblrRestClient(ConsumerKey, ConsumerSecret, Owner_key, Owner_secret)
    t_list = tumblr_client.dashboard(type='photo')
    img_list = []
    for Albumlist in t_list['posts']:
        for photolist in Albumlist['photos']:
            img_list.append(photolist['original_size']['url'])

    return render(request, 'urtumblrimg.html', {'imglist': img_list})


def tumblrvideo(request):
    Owner_key = request.session.get('Owner_key', 0)
    Owner_secret = request.session.get('Owner_secret', 0)
    if Owner_key == 0:
        return HttpResponseRedirect(reverse('tumblr'))
    tumblr_client = pytumblr.TumblrRestClient(ConsumerKey, ConsumerSecret, Owner_key, Owner_secret)

    myoffset = request.GET.get('myoffset', 0)
    mylimit = 50
    t_list = tumblr_client.dashboard(limit=mylimit, offset=myoffset, type='video')

    video_list = []
    for Albumlist in t_list['posts']:
        video_list.append([Albumlist['video_url'], Albumlist['thumbnail_url']])

    return render(request, 'urtumblrvideo.html', {'videolist': video_list})
