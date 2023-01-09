
import json

def create_winner(player):
    print(f"Player {player} won!")
    win={
        "type":"win",
        "player":player
    }

    return json.dumps(win)

def create_play(player, col, row):
    print(f"Player {player} played on hole ({row},{col})!")
    play={
        "type":"play",
        "player":player,
        "column":col,
        "row":row
    }

    return json.dumps(play)

def create_error(string):
    error = {
        "type":"error",
        "message":string
    }

    return json.dumps(error)

def create_init(join_key=None):
    init={
        "type":"init",
        "join_key": join_key
    }

    return json.dumps(init)