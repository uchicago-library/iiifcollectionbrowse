"""
iiifcollectionbrowse
"""
import logging
import os
from threading import Thread

from flask import Blueprint, render_template, url_for, request

import requests

from pyiiif.pres_api.utils import get_thumbnail

from .exceptions import NoCollectionFoundError, InvalidCollectionRecordError, \
    NoCollectionParameterError, IncompatibleRecordError

# Hacky workaround
from urllib.parse import unquote


__author__ = "Brian Balsamo"
__email__ = "brian@brianbalsamo.com"
__version__ = "0.1.0"


log = logging.getLogger(__name__)


BLUEPRINT = Blueprint('iiifcollectionbrowse', __name__,
                      template_folder='../templates',
                      static_folder='../static')


config = {
    "DEFAULT_COLLECTION": os.environ.get(
        "IIIFCOLLBROWSE_DEFAULT_COLL",
        None
    ),
    "VIEWER_URL": os.environ.get(
        "IIIFCOLLBROWSE_VIEWER_URL",
        "https://iiif-viewer.lib.uchicago.edu/uv/uv.html#"
    ),
    "REQUESTS_TIMEOUT": os.environ.get(
        "IIIFCOLLBROWSE_REQUESTS_TIMEOUT",
        1
    ),
    "NO_THUMB_IMG_URL": os.environ.get(
        "IIIFCOLLBROWSE_NO_THUMB_IMG_URL",
        ""
    ),
    "CONTRAST_COLOR": os.environ.get(
        "IIIFCOLLBROWSE_CONTRAST_COLOR",
        "#800000"
    ),
    "THUMBNAIL_BACKDROP": os.environ.get(
        "IIIFCOLLBROWSE_THUMBNAIL_BACKDROP",
        "#D6D6CE"
    )
}


DEFAULT_COLLECTION = config['DEFAULT_COLLECTION']
VIEWER_URL = config['VIEWER_URL']
REQUESTS_TIMEOUT = float(config['REQUESTS_TIMEOUT'])
NO_THUMB_IMG_URL = config['NO_THUMB_IMG_URL']
COLORS = {
    "contrast_color": config['CONTRAST_COLOR'],
    "thumbnail_backdrop": config['THUMBNAIL_BACKDROP']
}


def threaded_thumbnails(identifier, result, index):
    """
    Wraps get_thumbnail() for multi-threaded solutions

    The array should be "initialized" to the correct size,
    and each thread should deposit it's thumbnail into the
    appropriate index.

    :rtype: None
    """
    result[index] = get_thumbnail(identifier)


def build_collection_url(ident, page=1):
    """
    Builds the URL to render a collection record
    in this interface.

    :param str ident: The record identifier (a URL)
    :param str/int page: The page number to render, if using
        the thumbnail view.

    :rtype: str
    :returns: The URL which will render the collection record at
        the provided URL.
    """
    return url_for(".collection") + "?record={}&page={}".format(ident, str(page))


def record_compatible(rec):
    """
    Determines if a collection record is compatible with the interface

    :rtype: bool
    :returns: True if record is compatible, otherwise False.
    """
    # TODO
    # NOTE: This is primarily meant to be a method to provide
    # for graceful failure. What we do in this case is up in the air.
    # Link the user to the JSON?
    # Display a sad-face emoji?
    # Let the provider register a callback to run?
    return True


@BLUEPRINT.route("/")
def collection():
    # Try to pull the collection record, else a default, else error
    if not request.args.get('record'):
        if DEFAULT_COLLECTION:
            c_url = DEFAULT_COLLECTION
        else:
            raise NoCollectionParameterError()
    else:
        c_url = request.args['record']

    try:
        resp = requests.get(c_url, timeout=REQUESTS_TIMEOUT)
        resp.raise_for_status()
        rj = resp.json()
    # TODO: No bare excepts
    # (until then, quiet linter)
    except Exception as e:
        raise NoCollectionFoundError(
            "Could not find a collection JSON record at {}".format(c_url)
        )
    for x in ('@id', 'label'):
        if not rj.get(x):
            raise InvalidCollectionRecordError(
                "Could not find '@id' and 'label' keys in the JSON at {}".format(
                    c_url
                )
            )

    # Be sure the interface can render this record,
    # as some valid records may be unrenderable due
    # to technical constraints.
    if not record_compatible(rj):
        raise IncompatibleRecordError()

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
        x['t_url'] = build_collection_url(x['@id'])
    for x in members:
        if x['@type'] == "sc:Collection":
            x['t_url'] = build_collection_url(x['@id'])
    # Get if the current request is paginated or not
    page = request.args.get("page", 1)
    try:
        page = int(page)
    # TODO: No bare excepts
    # (until then, quiet linter)
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
        list_view = build_collection_url(rj['@id'], page=-1)
        if end > total:
            next_page = None
        else:
            next_page = build_collection_url(rj['@id'], page=page+1)
        prev_page = None
        if page > 1:
            prev_page = build_collection_url(rj['@id'], page=page-1)
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
            thumbnail_view = build_collection_url(rj['@id'], page=1)
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
