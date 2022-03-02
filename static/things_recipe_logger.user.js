// ==UserScript==
// @name     Things Recipe Logger
// @version  1.3
// @match    https://lab.latitude.io/main/things/*
// @grant    none
// ==/UserScript==

const console_prefix = '[Recipe Logger]';
const endpoint = 'http://127.0.0.1:8765';

var toast = null;
var toast_text;
var last_selected = [];

function callback(mutationsList, observer)
{
	if (toast.innerText != toast_text) {
		toast_text = toast.innerText;
		const json = {toast:toast_text, selected:last_selected};
		const usp = new URLSearchParams(location.search);
		const gameid = usp.get('gameId');
		if (gameid !== null) json.gameid = gameid;
		console.log(console_prefix, json);

		const xhr = new XMLHttpRequest();
		xhr.open('POST', endpoint + '/recipe');
		xhr.setRequestHeader('Content-Type', 'application/json');
		xhr.send(JSON.stringify(json));
	}
}

window.addEventListener('load', function() {
	setInterval(function() {
		const current_toast = document.querySelector('.things-result-toast');
		if (current_toast && current_toast !== toast) {
			toast = current_toast;
			console.log(console_prefix, 'Found result toast.');
			toast.style.textTransform = 'none';
			toast_text = toast.innerText;
			const observer = new MutationObserver(callback);
			observer.observe(toast, {subtree:true, childList:true, characterData:true});
		}
		
		const selected = [].map.call(document.querySelectorAll('.selected-thing .things-center-text'), element => element.innerHTML);
		if (selected.length > 0) last_selected = selected;
	}, 20);
});
