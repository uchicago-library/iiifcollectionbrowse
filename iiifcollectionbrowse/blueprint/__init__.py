"""
iiifcollectionbrowse
"""
import logging

from flask import Blueprint, render_template, url_for

import requests


__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.0.1"


log = logging.getLogger(__name__)


BLUEPRINT = Blueprint('iiifcollectionbrowse', __name__,
                      template_folder='templates',
                      static_folder='static')


VIEWER_URL = "https://universalviewer.io/uv.html"
# VIEWER_URL = "http://localhost:4000/index.html#"


@BLUEPRINT.route("/c/<path:c_url>")
def collection(c_url):
    resp = requests.get(c_url)
    resp.raise_for_status()
    rj = resp.json()
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
    for x in rj.get("members"):
        if x['@type'] == "sc:Collection":
            x['t_url'] = url_for(".collection", c_url=x['@id'])
    return render_template(
        "collection.html",
        viewer_url=VIEWER_URL,
        cname=rj['label'],
        members=members,
        collections=collections,
        manifests=manifests
    )
