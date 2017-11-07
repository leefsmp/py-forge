from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import Response
from pyramid.view import view_config
from bson.objectid import ObjectId
from .Memo import Memo
import requests
import os

#////////////////////////////////////////////////////////////////////
# /home route handler
#
#////////////////////////////////////////////////////////////////////
@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):

    models = request.db['gallery.models'].find().sort('name', 1)

    return {
        'title': 'Models',
        'models': models
    }

#////////////////////////////////////////////////////////////////////
# /viewer route handler
#
#////////////////////////////////////////////////////////////////////
@view_config(route_name='viewer', renderer='templates/viewer.jinja2')
def viewer_view(request):

    try:

        model_id = request.params['id']

        model_info = request.db['gallery.models'].find_one({
            '_id': ObjectId(model_id)
        })

        if model_info is None:
            return HTTPFound(location='/404')

        return {
            'token_url': '/forge/token',
            'model_info': model_info
        }

    except:

        return HTTPFound(location='/404')


# ////////////////////////////////////////////////////////////////////
# /viewer?id route handler
#
# ////////////////////////////////////////////////////////////////////
@view_config(route_name='not_found', renderer='templates/404.jinja2')
def not_found_view(request):

    return {
        'requested_url': '/404'
    }

#////////////////////////////////////////////////////////////////////
# Get Forge credentials from settings
#
#////////////////////////////////////////////////////////////////////
def getCredentials (settings) :

    return {
        'id': os.environ[settings['forge_env_client_id']],
        'secret': os.environ[settings['forge_env_client_secret']]
    }

#////////////////////////////////////////////////////////////////////
# Get Forge token
#
#////////////////////////////////////////////////////////////////////
def get_token(client_id, client_secret):

    base_url = 'https://developer.api.autodesk.com'
    url_authenticate = base_url + '/authentication/v1/authenticate'

    data = {
        'grant_type': 'client_credentials',
        'client_secret': client_secret,
        'client_id': client_id,
        'scope': 'data:read'
    }

    r = requests.post(url_authenticate, data=data)

    if 200 == r.status_code:
        return r.json()

    return None

#////////////////////////////////////////////////////////////////////
# Caches current token for delay specified by timeout (in seconds)
#
#////////////////////////////////////////////////////////////////////
@Memo(timeout=3580)
def get_tokenMemo(client_id, client_secret):

    return get_token(client_id, client_secret)

#////////////////////////////////////////////////////////////////////
# /forge/token route
#
#////////////////////////////////////////////////////////////////////
@view_config(route_name='forge-token', renderer='json')
def forge_token(request):

    credentials = getCredentials(request.registry.settings)

    return get_token (credentials['id'], credentials['secret'])

#////////////////////////////////////////////////////////////////////
# Get Forge thumbnail
#
#////////////////////////////////////////////////////////////////////
def get_thumbnail(token, urn):

    base_url = 'https://developer.api.autodesk.com'

    url = base_url + '/modelderivative/v2/designdata/{}/thumbnail?{}'

    query = 'width=400&height=400'

    headers = {
        'Authorization': 'Bearer ' + token['access_token']
    }

    r = requests.get(url.format(urn, query), headers=headers)

    if 200 == r.status_code:
        return r.content

    return None

# ////////////////////////////////////////////////////////////////////
# /forge/thumbnail?id route
#
# ////////////////////////////////////////////////////////////////////
@view_config(route_name='forge-thumbnail')
def forge_thumbnail(request):

    try:

        model_id = request.params['id']

        model_info = request.db['gallery.models'].find_one({
            '_id': ObjectId(model_id)
        })

        if model_info is None:
            return HTTPNotFound()

        urn = model_info['model']['urn']

        credentials = getCredentials(request.registry.settings)

        token = get_tokenMemo(credentials['id'], credentials['secret'])

        thumbnail = get_thumbnail(token, urn)

        return Response(thumbnail, content_type='image/png')

    except Exception as ex:

        return HTTPNotFound()

