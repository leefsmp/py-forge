from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config
from bson.objectid import ObjectId
import requests
import os

#////////////////////////////////////////////////////////////////////
# /home route handler
#
#////////////////////////////////////////////////////////////////////
@view_config(route_name='home', renderer='templates/home.jinja2')
def home_view(request):

    models = request.db['gallery.models'].find()

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
# /viewer route handler
#
# ////////////////////////////////////////////////////////////////////
@view_config(route_name='not_found', renderer='templates/404.jinja2')
def not_found_view(request):

    return {
        'requested_url': '/404'
    }

#////////////////////////////////////////////////////////////////////
# Get Forge token
#
#////////////////////////////////////////////////////////////////////
def get_token(request):

    base_url = 'https://developer.api.autodesk.com'
    url_authenticate = base_url + '/authentication/v1/authenticate'

    settings = request.registry.settings

    client_secret = os.environ[settings['forge_env_client_secret']]
    client_id = os.environ[settings['forge_env_client_id']]

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
# /forge/token route
#
#////////////////////////////////////////////////////////////////////
@view_config(route_name='forge-token', renderer='json')
def forge_token(request):

    return get_token (request)

#////////////////////////////////////////////////////////////////////
# Get thumbnail
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
# /forge/token route
#
# ////////////////////////////////////////////////////////////////////
@view_config(route_name='forge-thumbnail')
def forge_thumbnail(request):

    try:

        model_id = request.params['id']

        model_info = request.db['gallery.models'].find_one({
            '_id': ObjectId(model_id)
        })

        urn = model_info['model']['urn']

        token = get_token(request)

        thumbnail = get_thumbnail(token, urn)

        return Response(thumbnail, content_type='image/png')

    except Exception as ex:

        return ex