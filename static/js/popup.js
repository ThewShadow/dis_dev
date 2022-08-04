// ---------------------------POPUPS---------------------------

const popupLinks = document.querySelectorAll('.popup-link');
const popupCloseIcon = document.querySelectorAll('.popup__btn-close');

// Если модалок много, скрипт открывает только одну по id
if (popupLinks.length > 0) {
  for (let index = 0; index < popupLinks.length; index++) {
    const popupLink = popupLinks[index];

    popupLink.addEventListener('click', function (e) {
      const popupName = popupLink.getAttribute('href').replace('#', '');
      const currentPopup = document.getElementById(popupName);
      popupOpen(currentPopup);
      e.preventDefault();
    });
  }
}

function popupOpen(currentPopup) {
  lockBody('lock');
  currentPopup.classList.add('open');

  currentPopup.addEventListener('click', function (e) {
    if (e.target.closest('.popup__overlay')) {
      popupClose(e.target.closest('.popup'));
    }
  });
}

function popupClose(activePopup) {
  lockBody('unlock');
  activePopup.classList.remove('open');
}

if (popupCloseIcon.length > 0) {
  for (let index = 0; index < popupCloseIcon.length; index++) {
    const el = popupCloseIcon[index];
    el.addEventListener('click', function (e) {
      popupClose(el.closest('.popup'));
      e.preventDefault();
    });
  }
}

document.addEventListener('keydown', function (e) {
  if (e.which === 27) {
    const activePopup = document.querySelector('.popup.open');
    popupClose(activePopup);
  }
});

function lockBody(action) {
  // function need for 1)mobile menu 2) popup

  const body = document.querySelector('body');

  if (action == 'lock') {
    body.classList.toggle('lock');
  } else if (action == 'unlock') {
    body.classList.remove('lock');
  }
}


//^ Input image file

const inputFileWrapper = document.querySelector('.popup__input-file');
const inputFile = inputFileWrapper.querySelector('input');
const showResult = inputFileWrapper.querySelector('.popup__input-file-preview');

const verifiedTypes = ['image/jpg', 'image/jpeg', 'image/png', 'image/gif'];

if (inputFileWrapper !== null) {
  inputFile.addEventListener('change', () => {
    let file = inputFile.files[0];
    if (!verifiedTypes.includes(file.type)) {
      showResult.innerHTML = 'Помилка. Дозволені тільки зображення';
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      showResult.innerHTML = `<img src="${e.target.result}" alt="upload image" />`;
    };
    reader.onerror = () => {
      showResult.innerHTML = 'Помилка. Спробуйте ще раз';
    };
    reader.readAsDataURL(file);
  });
}

//^ checkbox for text create/enter account

const isHaveAcc = document.querySelector('.checkbox-is-have-acc')
const textCreateAcc = document.querySelector('.prompt1')
const textEnterAcc = document.querySelector('.prompt2')
		
isHaveAcc.addEventListener('change', (e) => {
	textCreateAcc.classList.toggle('hide')
	textEnterAcc.classList.toggle('hide')
})