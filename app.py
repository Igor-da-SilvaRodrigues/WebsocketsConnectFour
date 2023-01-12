#!/usr/bin/env python

import os
import signal
import asyncio
import json
import websockets
import secrets
from connect4 import PLAYER1, PLAYER2
from connect4 import Connect4

from events import create_error, create_play, create_winner

JOIN = {}

async def play(websocket, game, player, connected):

    async for message in websocket:
        dict = json.loads(message)
        if dict['type'] == 'play':
            #records a play and the landing
            landing = None
            try:
                landing = game.play(player, dict['column'])

                for ws in connected:
                    await ws.send(create_play(player, dict['column'], landing  ) )
            except RuntimeError:
                await websocket.send(create_error(f"Illegal move by player {player} on column {dict['column']}!"))
            if game.winner != None:
                for ws in connected:
                    await ws.send(create_winner(game.winner))
        else:
            for ws in connected:
                ws.send(create_error('Illegal move type!')) 

async def error(websocket, message):
    event = {
        "type":"error",
        "message":message,
    }
    await websocket.send(json.dumps(event))


async def join(websocket, join_key: str):
    
    #Find the connected four game
    try:
        game, connected = JOIN[join_key]
    except KeyError:
        await error(websocket, "Game not found.")
        return

    # Register to receive moves from this game.
    connected.add(websocket)
    try:

        print("second player joined game", id(game))
        await play(websocket, game, PLAYER2, connected)

    finally:
        connected.remove(websocket)



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

        print("first player started game", id(game))
        await play(websocket, game, PLAYER1, connected)

    finally:
        print(f"closing game {id(game)} because the last player disconnected.")
        del JOIN[join_key]

async def handler(websocket):
    # Receive and parse the "init" event from the UI.
    message = await websocket.recv()
    event = json.loads(message)
    assert event["type"] == "init"

    if "join" in event:
        # second player joins an existing game
        await join(websocket, event["join"])
    else:
        # First player starts a new game.
        await start(websocket)




async def main():
    #set the stop condition when receiving SIGTERM
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    port = int(os.environ.get("PORT","8001"))

    async with websockets.serve(handler, "", port):
        # await asyncio.Future()  # run forever
        await stop

if __name__ == "__main__":
    asyncio.run(main())