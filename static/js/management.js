let showCountQuery = document.querySelector('.managment__show-count input');
let inputArrows = document.querySelectorAll('.managment__show-count-arrows span');
let search = document.querySelector('.managment__search input');

const localValue = localStorage.getItem('searchValue');

if (search !== null) {
	search.value = localValue || '';
}

search.addEventListener('change', (e) => {
	localStorage.setItem('searchValue', e.target.value);
});

inputArrows[0].addEventListener('click', () => (showCountQuery.value = +showCountQuery.value + 1));
inputArrows[1].addEventListener('click', () => {
	if (showCountQuery.value > 0) showCountQuery.value = +showCountQuery.value - 1;
});
