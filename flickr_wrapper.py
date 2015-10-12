#Copyright (c) 2015 Crowd Dynamics Labs
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import urllib2
import json
import webbrowser
import unicodedata

def to_json(html):
    """
    converts flickr REST response to json

    html: HTML string response of flickr REST API

    """
    return json.loads(html[14:-1])


def get_related_tags(tag):
    """
    given an input string
    returns a list of related tags

    """
    url = ''.join(
        ['https://api.flickr.com/services/rest/?&method=flickr.tags.getRelated&api_key=8167ea9189063c9bcc3f87f8923176fd&format=json&tag=',
        tag
        ])
    try:
        response = urllib2.urlopen(url) 
    except:
        return None
    
    # process response
    html = response.read()
    data = to_json(html)

    tags = data['tags']['tag']

    ret = []

    for tag in tags:
        ret.append(tag['_content'])

    return ret


def is_food(tag):
    """
    given a tag
    returns True if the tag is food related
    False if not

    """

    similar_tags = get_related_tags(tag)

    if 'food' in similar_tags:
        return True
    else:
        return False


def search_photos(tags):
    """
    Returns a list of photo JSON objects that have ALL the tags
    specified in the input parameter

    tags: List of tags to search for
    returns: list of photo JSON objects

    relevant JSON keys for each object

    1) owner
    2) id

    """ 
    tags = "%2C".join(tags) 

    # call Flickr API
    # Parameters
    # privacy_filter = public photos
    # safe_search = safe
    # content_type = photos
    # media = photos only
    # sort = relevance
    # per_page         ( number of images per page, where page count defaults to 1)
    url = ''.join(["""https://api.flickr.com/services/rest/?
        &method=flickr.photos.search&api_key=8167ea9189063c9bcc3f87f8923176fd
        &privacy_filter=1
        &safe_search=1
        &content_type=1
        &media=photos&tag_mode=all
        &sort=relevance
        &per_page=50            
        &format=json&tags=""", tags])
    url = url.replace('\n', '')
    url = url.replace(' ', '')
    response = urllib2.urlopen(url) 
    
    # process response
    html = response.read()
    data = to_json(html)
    return data['photos']['photo']


def get_image(photo_id):
    """
    Wrapper for https://www.flickr.com/services/api/flickr.photos.getSizes.html

    returns the image source of the image specified by the photo_id
    """
    # call Flickr API
    url = 'https://api.flickr.com/services/rest/?&method=flickr.photos.getSizes&api_key=8167ea9189063c9bcc3f87f8923176fd&format=json&photo_id=' + photo_id
    response = urllib2.urlopen(url)

    # process response
    html = response.read()
    info = to_json(html)
    print(info)
    if info["sizes"]["candownload"] == 0:
        # cannot download
        return None
    else:
        images = info["sizes"]["size"]
        for image in images:
            if image["label"] == "Medium":
                return image["source"]
        return images[-1]


def get_info(photo_id):
    """
    Wrapper for https://www.flickr.com/services/api/flickr.photos.getInfo.html

    photo_id: photo ID of the photo

    """

    # call Flickr API
    url = 'https://api.flickr.com/services/rest/?&method=flickr.photos.getInfo&api_key=8167ea9189063c9bcc3f87f8923176fd&format=json&photo_id=' + photo_id
    response = urllib2.urlopen(url)
    
    # process response
    html = response.read()
    info = to_json(html)
    # prepare return data
    ret = {}
    ret['user_id'] =info['photo']['owner']['nsid'] 
    ret['photo_id'] = info['photo']['id']
    ret['url'] = info['photo']['urls']['url'][0]['_content']
    ret['tags'] = [tag['_content'] for tag in info['photo']['tags']['tag']]

    return ret
