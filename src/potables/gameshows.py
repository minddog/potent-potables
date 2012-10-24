from flask.ext.restful import reqparse, abort, Api, Resource, fields, marshal_with
from potables.db.gameshow import Game
from potables.paging import EfficientQueryPaginator

resource_fields = {
    'id':   fields.Integer,
    'uri':  fields.Url('gameshow'),
    'players': fields.Integer,
    'host': fields.String,
    'name': fields.String,
}

list_fields = {
    'gameshows': resource_fields,
}

def abort_if_games_does_not_exist(game):
    if not game:
        abort(404, message="Game: {} not found".format(gameshow_id))

instance_parser = reqparse.RequestParser()
class Gameshow(Resource):
    @marshal_with(resource_fields)
    def get(self, gameshow_id):
        args = instance_parser.parse_args()
        game = Game.qs.filter_by(id = gameshow_id).first()
        abort_if_games_does_not_exist(game)
        return game

    def delete(self, gameshow_id):
        game = Game.qs.filter_by(id = gameshow_id).first()
        abort_if_games_does_not_exist(game)
        Game.delete(game)
        return '', 204

    @marshal_with(resource_fields)
    def post(self, gameshow_id):
        args = instance_parser.parse_args()
        game = Game.qs.filter_by(id = gameshow_id).first()
        abort_if_games_does_not_exist(game)
        game.players = args.players
        Game.update(game)
        Game.qm.session.commit()
        return '', 200

list_parser = reqparse.RequestParser()
list_parser.add_argument('players', type=int, help="Number of players", default=0)
list_parser.add_argument('host', type=str, help="Name of the gameshow host")
list_parser.add_argument('name', type=str, help="Name of the gameshow")
class GameshowList(Resource):

    @marshal_with(resource_fields)
    def get(self):
        args = list_parser.parse_args()
        games = Game.qs
        if args['players'] > 0:
            games = games.filter_by(players=args['players'])
        if args['host']:
            games = games.filter_by(host=args['host'])
        if args['name']:
            games = games.filter_by(name=args['name'])

        page = EfficientQueryPaginator(games)
        page_data = page.metadata()
        games = page.page()
        if not games and page_data.get('page', 0) > 0:
            paging.abort_out_of_range()

        return games

    def post(self):
        create_parser = reqparse.RequestParser()
        create_parser.add_argument('players', type=int, required=True)
        create_parser.add_argument('host', type=str, required=True)
        create_parser.add_argument('name', type=str, required=True)
        args = create_parser.parse_args()
        Game.create(**args)
        Game.qm.session.commit()

