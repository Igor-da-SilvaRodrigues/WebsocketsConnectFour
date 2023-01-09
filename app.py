#!/usr/bin/env python

import asyncio
import json
import websockets
from connect4 import PLAYER1, PLAYER2
from connect4 import Connect4

from events import create_error, create_play, create_winner

async def handler(websocket):
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
            websocket.send(create_error('Illegal move type!'))

async def main():
    async with websockets.serve(handler, "", 8001):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())