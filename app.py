#!/usr/bin/env python

import asyncio
import json
import websockets
import secrets
from connect4 import PLAYER1, PLAYER2
from connect4 import Connect4

from events import create_error, create_play, create_winner

JOIN = {}

async def start(websocket):
    # Initialize a Connect Four game, the set of WebSocket connections
    # receiving moves from this game, and secret access token.
    game = Connect4()
    connected = {websocket}

    join_key = secrets.token_urlsafe(12)
    JOIN[join_key] = game, connected

    try:
        # Send the secret access token to the browser of the first player,
        # where it'll be used for building a "join" link.
        event = {
            "type": "init",
            "join": join_key,
        }
        await websocket.send(json.dumps(event))

        # Temporary - for testing.
        print("first player started game", id(game))
        async for message in websocket:
            print("first player sent", message)

    finally:
        print(f"closing game {id(game)} because the last player disconnected.")
        del JOIN[join_key]

async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    # First player starts a new game.
    await start(websocket)

""" async def handler(websocket):
    game = Connect4()
    async for message in websocket:
        dict = json.loads(message)
        if dict['type'] == 'play':
            
            
            #records a play and the landing.
            landing = None
            try:
                landing = game.play(dict['player'],dict['column'])
                await websocket.send(create_play(dict['player'], dict['column'], landing))
            except RuntimeError:
                await websocket.send(create_error(f"Illegal move by player {dict['player']} on column {dict['column']}!"))
            if game.winner != None:
                await websocket.send(create_winner(game.winner))

        else:
            websocket.send(create_error('Illegal move type!')) """

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())