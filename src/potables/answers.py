from flask.ext.restful import reqparse, abort, Api, Resource

instance_parser = reqparse.RequestParser()
class Answer(Resource):
    def get(self, gameshow_id, answer_id):
        args = instance_parser.parse_args()
        return None

list_parser = reqparse.RequestParser()
class AnswerList(Resource):
    def get(self, gameshow_id):
        args = instance_parser.parse_args()
        return None
