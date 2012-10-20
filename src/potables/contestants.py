from flask.ext.restful import reqparse, abort, Api, Resource

instance_parser = reqparse.RequestParser()
instance_parser.add_argument('name', type=str)
class Contestant(Resource):
    def get(self, gameshow_id, contestant_id):
        args = instance_parser.parse_args()
        return None

    def post(self, gameshow_id, contestant_id):
        args = instance_parser.parse_args()
        return None

list_parser = reqparse.RequestParser()
list_parser.add_argument('name', type=str)
class ContestantList(Resource):
    def get(self, gameshow_id):
        args = list_parser.parse_args()
        return None

    def post(self, gameshow_id):
        args = list_parser.parse_args()
        return None
