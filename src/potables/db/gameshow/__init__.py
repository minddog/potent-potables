from .. import configuration
import base

__db_name__ = "gameshow"
__base_class__ = base.GameshowBase
configuration.setup_module(locals())

from games import Game
