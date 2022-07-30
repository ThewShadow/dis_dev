const btnInfo = document.querySelector('.account__btn-info');
const btnSubscr = document.querySelector('.account__btn-subscr');
const blockInfo = document.querySelector('.account__info');
const blockSubscr = document.querySelector('.account__subscr');
const allElems = [btnInfo, btnSubscr, blockInfo, blockSubscr];

const navBlock = document.querySelector('.account__nav');

if (btnInfo !== null) {
	btnInfo.addEventListener('click', (e) => toggleBlocks(e.target));
}

if (btnInfo !== null) {
	btnSubscr.addEventListener('click', (e) => toggleBlocks(e.target));
}

function toggleBlocks(curent) {
	if (!curent.classList.contains('active')) {
		allElems.forEach((el) => el.classList.toggle('active'));
	}
}

if (navBlock !== null) {
	navBlock.addEventListener('click', () => navBlock.classList.toggle('opened'));
}
