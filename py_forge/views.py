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

    model_id = request.params['id']

    model_info = request.db['gallery.models'].find_one({
        '_id': ObjectId(model_id)
    })

    return {
        'token_url': '/forge/token',
        'model_info': model_info
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
# /forge/token route
#
#////////////////////////////////////////////////////////////////////
@view_config(route_name='forge-token', renderer='json')
def forge_token(request):

    client_secret = os.environ['FORGE_DEV_CLIENT_SECRET']
    client_id = os.environ['FORGE_DEV_CLIENT_ID']

    token = get_token(client_id, client_secret)

    return token