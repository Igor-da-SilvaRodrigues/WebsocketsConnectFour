import { createBoard, playMove, PLAYER1, PLAYER2 } from "./connect4.js";

let last_player = PLAYER2;

// Main loop, triggered on content load...
window.addEventListener("DOMContentLoaded", () => {
    // Initialize the UI.
    const board = document.querySelector(".board");
    createBoard(board);

    const websocket = new WebSocket("ws://localhost:8001/");
    initGame(websocket);
    receiveMoves(board, websocket);
    sendMoves(board, websocket);

});

/**
 * Registers the event listener for player actions.
 * @param {*} board 
 * @param {WebSocket} websocket 
 */
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

/**
 * Registers the event listener for server messages
 * @param {*} board 
 * @param {WebSocket} websocket 
 */
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
            case "init":
                // Create link for inviting the second player.
                document.querySelector(".join").href = "?join=" + event.join;
                break;
            default:
                throw new Error(`Unsupported event type: ${event.type}.`);
        }
    });
}

/**
 * Sends an "init" event for the first player
 * @param {WebSocket} websocket 
 */
function initGame(websocket) {
    websocket.addEventListener("open", () => {
      // Send an "init" event for the first player.
      const event = { type: "init" };
      websocket.send(JSON.stringify(event));
    });
}

