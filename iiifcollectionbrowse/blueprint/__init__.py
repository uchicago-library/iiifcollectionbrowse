"""
iiifcollectionbrowse
"""
import logging
from threading import Thread

from flask import Blueprint, render_template, url_for, request

import requests

from pyiiif.pres_api.utils import get_thumbnail

# Hacky workaround
from urllib.parse import unquote


__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.0.1"


log = logging.getLogger(__name__)


BLUEPRINT = Blueprint('iiifcollectionbrowse', __name__,
                      template_folder='templates',
                      static_folder='static')


VIEWER_URL = "https://iiif-viewer.lib.uchicago.edu/uv/uv.html#"
REQUESTS_TIMEOUT = 1/10
NO_THUMB_IMG_URL = ""
COLORS = {
    "contrast_color": "#800000",
    "thumbnail_backdrop": "#D6D6CE"
}



def threaded_thumbnails(identifier, result, index):
    # Wrap up this operation so we can use this function
    # as the target of a threading.Thread
    result[index] = get_thumbnail(identifier)


@BLUEPRINT.route("/<path:c_url>")
def collection(c_url):
    # Try to pull the collection record
    resp = requests.get(c_url, timeout=REQUESTS_TIMEOUT)
    resp.raise_for_status()
    rj = resp.json()
    # Parse the record
    members = []
    collections = []
    manifests = []
    if rj.get("members"):
        members = rj['members']
    if rj.get('collections'):
        collections = rj['collections']
    if rj.get('manifests'):
        manifests = rj['manifests']
    # build template urls
    for x in collections:
        x['t_url'] = url_for(".collection", c_url=x['@id'])
    for x in members:
        if x['@type'] == "sc:Collection":
            x['t_url'] = url_for(".collection", c_url=x['@id'])
    # Get if the current request is paginated or not
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except Exception:
        page = 1
    # Thumbnail view - paginated
    if rj.get('viewingHint') == "individuals" and page > 0:
        # 30 results per page max, to not block too long on
        # dynamically generating thumbnails even in bad cases
        total = max(len(members), len(collections), len(manifests))
        start = (page-1)*10
        end = page*10
        # Generate sublists of just the stuff for this page
        members = members[start:end]
        collections = collections[start:end]
        manifests = manifests[start:end]
        # Assemble page links and stuff
        list_view = "{}?page=-1".format(url_for(".collection", c_url=c_url))
        if end > total:
            next_page = None
        else:
            next_page = "{}?page={}".format(url_for(".collection", c_url=c_url), str(page+1))
        prev_page = None
        if page > 1:
            prev_page = "{}?page={}".format(url_for(".collection", c_url=c_url), str(page-1))
        # Handle thumbnail finding for viewingHint == individuals
        # https://stackoverflow.com/questions/6893968/
        # how-to-get-the-return-value-from-a-thread-in-python
        # Note: This makes the order the lists are concat'd together
        # in important - otherwise thumbnails won't match.
        results = [None] * len(members+collections+manifests)
        for i, x in enumerate(members + collections + manifests):
            x['thumb_thread'] = Thread(target=threaded_thumbnails, args=(x['@id'], results, i))
            x['thumb_thread'].start()
        for i, x in enumerate(members + collections + manifests):
            x['thumb_thread'].join(timeout=10)
            if results[i] is not None:
                # This call to unquote is a hack to get the thumbnails
                # to work against a Loris server until we figure out
                # why our apache setup isn't passing escaped URLs through
                # to the server
                x['thumb_url'] = unquote(results[i])
            else:
                x['thumb_url'] = NO_THUMB_IMG_URL
        return render_template(
            "collection_thumbnails.html",
            viewer_url=VIEWER_URL,
            cname=rj['label'],
            cdesc=rj.get('description'),
            list_view=list_view,
            next_page=next_page,
            prev_page=prev_page,
            members=members,
            collections=collections,
            manifests=manifests,
            colors=COLORS
        )
    # List view - no pagination
    else:
        thumbnail_view = None
        if rj.get('viewingHint') == 'individuals':
            thumbnail_view = "{}?page=1".format(url_for(".collection", c_url=c_url))
        return render_template(
            "collection_list.html",
            viewer_url=VIEWER_URL,
            cname=rj['label'],
            cdesc=rj.get('description'),
            members=members,
            collections=collections,
            manifests=manifests,
            colors=COLORS,
            thumbnail_view=thumbnail_view
        )
