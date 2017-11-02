from pyramid.config import Configurator
from urllib.parse import urlparse
from pymongo import MongoClient
from gridfs import GridFS

#////////////////////////////////////////////////////////////////////
# Server main
#
#////////////////////////////////////////////////////////////////////
def main(global_config, **settings):

    config = Configurator(settings=settings)

    config.include('pyramid_jinja2')

    config.add_static_view(
        'static', 'static',
        cache_max_age=settings['cache_max_age'])

    db_url = urlparse(settings['mongo_uri'])

    config.registry.db = MongoClient(
           host=db_url.hostname,
           port=db_url.port,
    )

    def add_db(request):
        db = config.registry.db[db_url.path[1:]]
        if db_url.username and db_url.password:
            db.authenticate(db_url.username, db_url.password)
        return db

    def add_fs(request):
        return GridFS(request.db)

    config.add_request_method(add_db, 'db', reify=True)
    config.add_request_method(add_fs, 'fs', reify=True)

    # Routes definition
    config.add_route('forge-token', '/forge/token')
    config.add_route('viewer', '/viewer')
    config.add_route('home', '/')

    config.scan()

    return config.make_wsgi_app()
