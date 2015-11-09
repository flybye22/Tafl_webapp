from tafl.models import *
import json

def make_game(ruleset, black_player, white_player, waiting_player):
    g = Game(black_player=black_player, white_player=white_player, 
            waiting_player=waiting_player, turn=False, ruleset=ruleset)
    g.save()

    for row in range(ruleset.size):
        for col in range(ruleset.size):
            Square.objects.create(game=g, x_coord=row, y_coord=col)
            
    pieces = json.loads(ruleset.pieces)
    for piece in pieces:
        p = Piece.objects.create(game=g, p_type=piece[3], color=piece[0])
        s = Square.objects.get(game=g, x_coord=piece[1], y_coord=piece[2])
        s.member = p
        s.save()