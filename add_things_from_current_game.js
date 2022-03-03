// Paste this into the developer console to add all of the things in the current game to the database.

things = [].map.call(document.querySelectorAll('.things-center-text'), element => element.innerHTML);
usp = new URLSearchParams(location.search);
gameid = usp.get('gameId');
xhr = new XMLHttpRequest();
xhr.open('POST', 'http://127.0.0.1:8765/things_in_game');
xhr.setRequestHeader('Content-Type', 'application/json');
xhr.send(JSON.stringify({things, gameid}));
