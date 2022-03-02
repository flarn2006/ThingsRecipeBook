function inIframe()
{
	try {
		return window.self !== window.top;
	} catch (e) {
		return true;
	}
}

window.onload = function() {
	if (inIframe()) {
		document.querySelector('nav').style.display = 'none';
	}

	const search = document.getElementById('search');
	const tbody = document.querySelector('tbody');
	var xhr = null;
	const doSearch = function() {
		if (search.value.length === 0) {
			xhr = null;
			tbody.innerHTML = '';
		} else {
			xhr = new XMLHttpRequest();
			xhr.open('GET', '/recipe/' + encodeURIComponent(search.value));
			xhr.addEventListener('load', function() {
				if (this !== xhr) return;
				tbody.innerHTML = '';
				const json = JSON.parse(this.responseText);
				json.recipes.forEach(function(recipe) {
					const tr = document.createElement('tr');
					const fields = [
						{text: recipe.product.name, link: false},
						{text: recipe.ingredients[0].name, link: true},
						{text: recipe.ingredients[1].name, link: true},
						{text: recipe.means, link: false}
					];
					fields.forEach(function(field) {
						const td = document.createElement('td');
						if (field.link) {
							const a = document.createElement('a');
							a.innerText = field.text;
							a.href = '#' + encodeURIComponent(field.text);
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
		}
	};
	search.addEventListener('input', doSearch);
	search.addEventListener('blur', function() {
		location.hash = '#' + encodeURIComponent(search.value);
	});
	window.addEventListener('hashchange', function() {
		search.value = decodeURIComponent(location.hash.slice(1));
		doSearch();
	});
};
