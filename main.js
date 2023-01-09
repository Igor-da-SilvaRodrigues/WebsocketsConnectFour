import { createBoard, playMove, PLAYER1, PLAYER2 } from "./connect4.js";

let last_player = PLAYER2;

window.addEventListener("DOMContentLoaded", () => {
    // Initialize the UI.
    const board = document.querySelector(".board");
    createBoard(board);

    const websocket = new WebSocket("ws://localhost:8001/");
    receiveMoves(board, websocket);
    sendMoves(board, websocket);

});

function sendMoves(board, websocket) {
    // When clicking a column, send a "play" event for a move in that column.
    board.addEventListener("click", ({ target }) => {
        const column = target.dataset.column;
        // Ignore clicks outside a column.
        if (column === undefined) {
            return;
        }

        last_player = last_player == PLAYER1 ? PLAYER2 : PLAYER1;
        
        const event = {
            type: "play",
            column: parseInt(column, 10),
            player: last_player
        };
        websocket.send(JSON.stringify(event));
    });
}



function showMessage(message) {
    window.setTimeout(() => window.alert(message), 50);
}

function receiveMoves(board, websocket) {
    websocket.addEventListener("message", ({ data }) => {
        const event = JSON.parse(data);
        switch (event.type) {
            case "play":
                // Update the UI with the move.
                playMove(board, event.player, event.column, event.row);
                break;
            case "win":
                showMessage(`Player ${event.player} wins!`);
                // No further messages are expected; close the WebSocket connection.
                websocket.close(1000);
                break;
            case "error":
                showMessage(event.message);
                break;
            default:
                throw new Error(`Unsupported event type: ${event.type}.`);
        }
    });
}