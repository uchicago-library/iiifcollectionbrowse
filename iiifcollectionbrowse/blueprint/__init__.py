"""
iiifcollectionbrowse
"""
import logging

from flask import Blueprint, render_template, url_for, request

import requests


__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.0.1"


log = logging.getLogger(__name__)


BLUEPRINT = Blueprint('iiifcollectionbrowse', __name__,
                      template_folder='templates',
                      static_folder='static')


VIEWER_URL = "https://iiif-viewer.lib.uchicago.edu/uv/uv.html#"


def get_thumbnail(rec, width=200, height=200, preserve_ratio=True):
    # If we pass an identifier just try and
    # get the record from the identifier.
    if preserve_ratio:
        width = "!"+str(width)
    if not isinstance(rec, dict):
        try:
            resp = requests.get(rec)
            resp.raise_for_status()
            rec = resp.json()
        except:
            # TODO: handle failure
            raise
    # Try and update the record from its URI
    try:
        remote_rec_resp = requests.get(rec['@id'])
        remote_rec_resp.raise_for_status()
        remote_rec_json = remote_rec_resp.json()
        rec.update(remote_rec_json)
    except:
        pass
    # If one is hardcoded
    if rec.get('thumbnail'):
        return rec['thumbnail']['@id']+"/full/{},{}/0/default.jpg".format(width, height)
    # Dynamic functionality - get the first image that should be relevant
    if rec['@type'] == "sc:Collection":
        # prefer the first member, if it exists
        if rec.get("members"):
            return get_thumbnail(rec['members'][0])
        # otherwise try for manifests
        elif rec.get("manifests"):
            return get_thumbnail(rec['manifests'][0])
        # finally check for subcollections
        elif rec.get("collections"):
            return get_thumbnail(rec['collections'][0])
        else:
            raise ValueError()
    elif rec['@type'] == "sc:Manifest":
        # sequences MUST be > 0
        return get_thumbnail(rec['sequences'][0])
    elif rec['@type'] == "sc:Sequence":
        # canvases MUST be > 0
        return get_thumbnail(rec['canvases'][0])
    elif rec['@type'] == "sc:Canvas":
        if rec.get('images'):
            return get_thumbnail(rec['images'][0])
        else:
            raise ValueError()
    # We made it!
    elif rec['@type'] == "oa:Annotation":
        # Be sure we haven't stumbled into something
        # that isn't an image
        if rec.get("resource") is None:
            raise ValueError()
        # TODO: Actually parse the URL
        # Time for a hack for just the moment
        x = rec['resource']['@id']
        return x.split(".tif")[0] + ".tif" + "/full/{},{}/0/default.jpg".format(width, height)
    else:
        raise ValueError()


@BLUEPRINT.route("/<path:c_url>")
def collection(c_url):
    resp = requests.get(c_url)
    resp.raise_for_status()
    rj = resp.json()
    members = []
    collections = []
    manifests = []
    page = request.args.get("page", 1)
    try:
        page = int(page)
    except:
        page = 1
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
    # Handle thumbnail finding for viewingHint == individuals
    if rj.get('viewingHint') == "individuals" and page > 0:
        # Paginate if we're doing thumbnails - 30 results per page max
        total = max(len(members), len(collections), len(manifests))
        start = (page-1)*10
        end = page*10
        members = members[start:end]
        collections = collections[start:end]
        manifests = manifests[start:end]
        if end > total:
            next_page = None
        else:
            next_page = "/{}?page={}".format(c_url, str(page+1))
        prev_page = None
        if page > 1:
            prev_page =  "/{}?page={}".format(c_url, str(page-1))
        for x in members + collections + manifests:
            try:
                x['thumb_url'] = get_thumbnail(x)
            except:
                x['thumb_url'] = ""
        return render_template(
            "collection_individuals.html",
            viewer_url=VIEWER_URL,
            cname=rj['label'],
            cdesc=rj.get('description'),
            next_page=next_page,
            prev_page=prev_page,
            members=members,
            collections=collections,
            manifests=manifests
        )
    else:
        return render_template(
            "collection.html",
            viewer_url=VIEWER_URL,
            cname=rj['label'],
            cdesc=rj.get('description'),
            members=members,
            collections=collections,
            manifests=manifests
        )
