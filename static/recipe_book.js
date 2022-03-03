function inIframe()
{
	try {
		return window.self !== window.top;
	} catch (e) {
		return true;
	}
}

function findGamesWithThing(thing_id)
{
	const xhr = new XMLHttpRequest();
	xhr.open('GET', '/thing/'+thing_id);
	xhr.addEventListener('load', function() {
		const json = JSON.parse(this.responseText);
		if (json.games.length == 0) {
			alert('“'+json.name+'” does not appear in any known games.');
		} else {
			document.getElementById('game_search_thing').innerText = json.name;
			const list = document.getElementById('game_search_list');
			list.innerHTML = '';
			document.getElementById('game_search').setAttribute('open', 'true');

			json.games.forEach(function(gameid) {
				const section = document.createElement('section');

				const h2 = document.createElement('h2');
				const a = document.createElement('a');
				a.href = 'https://lab.latitude.io/main/things/things-play?gameId=' + encodeURIComponent(gameid);
				a.target = '_blank';
				a.innerText = gameid;
				h2.appendChild(a);
				section.appendChild(h2);

				list.appendChild(section);

				const xhr = new XMLHttpRequest();
				xhr.open('GET', '/game/'+encodeURIComponent(gameid));
				xhr.addEventListener('load', function() {
					const json = JSON.parse(this.responseText);
					const ul = document.createElement('ul');
					json.things.forEach(function(thing) {
						const li = document.createElement('li');
						li.innerText = thing.name;
						if (thing.id == thing_id) {
							li.classList.add('highlight');
						}
						ul.appendChild(li);
					});
					section.appendChild(ul);
				});
				xhr.send();
			});
		}
	});
	xhr.send();
}

window.onload = function() {
	if (inIframe()) {
		document.querySelector('nav').style.display = 'none';
	}

	const search = document.getElementById('search');
	const tbody = document.querySelector('tbody');
	var xhr = null;
	const doSearch = function() {
		xhr = new XMLHttpRequest();
		if (search.value.length === 0) {
			xhr.open('GET', '/all_recipes');
		} else {
			xhr.open('GET', '/recipe/' + encodeURIComponent(search.value));
		}
		xhr.addEventListener('load', function() {
			if (this !== xhr) return;
			tbody.innerHTML = '';
			const json = JSON.parse(this.responseText);
			json.recipes.forEach(function(recipe) {
				const tr = document.createElement('tr');
				const fields = [
					{text: recipe.product.name, link: 'javascript:findGamesWithThing(' + recipe.product.id + ')', title: 'Find games containing this thing'}, //I'm not worried about XSS on a localhost server
					{text: recipe.ingredients[0].name, link: '##', title: 'Find recipes for this thing'},
					{text: recipe.ingredients[1].name, link: '##', title: 'Find recipes for this thing'},
					{text: recipe.means}
				];
				fields.forEach(function(field) {
					const td = document.createElement('td');
					if (field.link !== undefined) {
						const a = document.createElement('a');
						a.innerText = field.text;
						if (field.link === '##')
							a.href = '#' + encodeURIComponent(field.text);
						else
							a.href = field.link;
						a.title = field.title;
						td.appendChild(a);
					} else {
						td.innerText = field.text;
					}
					tr.appendChild(td);
				});
				tbody.appendChild(tr);
			});
		});
		xhr.send();
	};
	search.addEventListener('input', doSearch);
	search.addEventListener('change', function() {
		location.hash = '#' + encodeURIComponent(search.value);
	});

	const doSearchFromHash = function() {
		search.value = decodeURIComponent(location.hash.slice(1));
		doSearch();
	};
	window.addEventListener('hashchange', doSearchFromHash);
	doSearchFromHash();

	document.querySelector('#game_search button.close').addEventListener('click', function() {
		this.parentElement.removeAttribute('open');
	});
};
