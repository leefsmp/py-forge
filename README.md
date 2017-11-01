
# Py-Forge!

## Description

Just a Python web application using [Pyramid](https://trypyramid.com) and [Autodesk Forge Web APIs](https://developer.autodesk.com)

## Prerequisites

    * Python 3.x

    * MongoDB

## Database setup

The server expect a mongoDB database named forge-rcdb running on localhost:27017

You can change those settings in development.ini:

    [app:main]
    # ...
    mongo_uri = mongodb://localhost:27017/forge-rcdb

## Database schema

Populate your database with a collection named "gallery.models" with at least one model pointing to a translated URN.

    {
        "_id" : ObjectId("59f9aeedbcd28f9df393f760"),
        "name" : "Engine",
        "model" : {
            "urn" : "dXhaghj....(urn of translated model from Forge)"
        }
    }

See [Prepare a File for the Viewer](https://developer.autodesk.com/en/docs/model-derivative/v2/tutorials/prepare-file-for-viewer)

## Project Setup

    * > cd <directory containing this project>

    * > python -m venv .

    * > ./bin/pip install -e .

    * > ./bin/pserve development.ini --reload

## Live Demo

Coming soon ...

## License

[MIT License](http://opensource.org/licenses/MIT)

## Written by

Written by [Philippe Leefsma](http://twitter.com/F3lipek)

Forge Partner Development - [http://forge.autodesk.com](http://forge.autodesk.com)
