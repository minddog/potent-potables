from flask.ext.restful import reqparse, abort, Api, Resource

instance_parser = reqparse.RequestParser()
class Projector(Resource):
    def get(self, gameshow_id):
        args = instance_parser.parse_args()
        return None
