from flask.ext.restful import reqparse, abort, Api, Resource

instance_parser = reqparse.RequestParser()
class Gameshow(Resource):
    def get(self, gameshow_id):
        args = instance_parser.parse_args()
        return None

list_parser = reqparse.RequestParser()
class GameshowList(Resource):
    def get(self):
        args = list_parser.parse_args()
        return None

