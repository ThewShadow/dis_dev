const btnInfo = document.querySelector('.account__btn-info');
const btnSubscr = document.querySelector('.account__btn-subscr');
const blockInfo = document.querySelector('.account__info');
const blockSubscr = document.querySelector('.account__subscr');
const allElems = [btnInfo, btnSubscr, blockInfo, blockSubscr];

const navBlock = document.querySelector('.account__nav');

btnInfo.addEventListener('click', (e) => toggleBlocks(e.target));
btnSubscr.addEventListener('click', (e) => toggleBlocks(e.target));

function toggleBlocks(curent) {
  if (!curent.classList.contains('active')) {
    allElems.forEach((el) => el.classList.toggle('active'));
  }
}

navBlock.addEventListener('click', () => navBlock.classList.toggle('opened'));
