from flask import Flask
from flask.ext import restful
from flask.ext.restful import reqparse, abort, Api, Resource
from . import contestants, gameshows, projector, answers

app = Flask(__name__)
potent_api = Api(app)
potent_api.add_resource(gameshows.GameshowList, '/Gameshows')
potent_api.add_resource(gameshows.Gameshow, '/Gameshows/<gameshow_id>')
potent_api.add_resource(contestants.ContestantList, '/Gameshows/<gameshow_id>/Contestants')
potent_api.add_resource(contestants.Contestant, '/Gameshows/<gameshow_id>/Contestants/<contestant_id>')
potent_api.add_resource(projector.Projector, '/Gameshows/<gameshow_id>/Projector')
potent_api.add_resource(answers.AnswerList, '/Gameshows/<gameshow_id>/Answers')
potent_api.add_resource(answers.Answer, '/Gameshows/<gameshow_id>/Answers/<answer_id>')