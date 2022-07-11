// ---------------------------MOBILE MENU---------------------------

const btnMenu = document.querySelector('.btn-menu');
const menuContent = document.querySelector('.header__content');
const menuLink = document.querySelectorAll('.menu__link');

if (btnMenu != null) {
	btnMenu.addEventListener('click', function () {
		btnMenu.classList.toggle('opened');
		menuContent.classList.toggle('opened');
		lockBody('lock');
	});
}

for (link of menuLink) {
	link.addEventListener('click', () => {
		btnMenu.classList.remove('opened');
		menuContent.classList.remove('opened');
		lockBody('unlock');
	});
}

// function need for 1)mobile menu 2) popup
function lockBody(action) {
	const body = document.querySelector('body');

	if (action == 'lock') {
		body.classList.toggle('lock');
	} else if (action == 'unlock') {
		body.classList.remove('lock');
	}
}

//^ submenu

let subMenuItems = document.querySelectorAll('.submenu-block');

subMenuItems.forEach((el) => {
	el.addEventListener('click', (e) => {
		let element = e.target;
		let parent = element.parentElement;

		if (element.classList.contains('submenu-block__head')) {
			if (parent.classList.contains('opened')) {
				closeAllSubMenu();
			} else {
				closeAllSubMenu();
				parent.classList.add('opened');
			}
		}
	});
});

window.addEventListener('click', (e) => {
	if (!e.target.closest('.submenu-block')) {
		closeAllSubMenu();
	}
});

function closeAllSubMenu() {
	subMenuItems.forEach((el) => el.classList.remove('opened'));
}

// ^ service__period

let servicePeriod = document.querySelector('.service__period');

if (servicePeriod != null) {
	servicePeriod.addEventListener('click', () => {
		let periods = servicePeriod.querySelectorAll('button');
		periods.forEach((el) => el.classList.toggle('active'));
	});
}
//^ show/hide input password

let inputBlockPassword = document.querySelectorAll('.popup__input-password');

if (inputBlockPassword != null) {
	inputBlockPassword.forEach((inputBlock) => {
		inputBlock.addEventListener('click', (e) => {
			if (e.target.nodeName === 'BUTTON') {
				e.target.classList.toggle('hide');

				let input = inputBlock.querySelector('input');
				if (input.type == 'text') {
					input.type = 'password';
				} else if (input.type == 'password') {
					input.type = 'text';
				}
			}
		});
	});
}




window.addEventListener('load', setPayment);


function setPayment() {

	//^ style custom selects

	$('.select').each(function () {
		// Variables
		var $this = $(this),
			selectOption = $this.find('option'),
			selectOptionLength = selectOption.length,
			selectedOption = selectOption.filter(':selected'),
			selectedOptionValue = selectedOption.attr('value').toUpperCase();
		dur = 500;

		$this.hide();
		// Wrap all in select box
		$this.wrap('<div class="select"></div>');
		// Style box
		$('<div>', {
			class: 'select__gap',
			text: selectedOptionValue,
		}).insertAfter($this);

		var selectGap = $this.next('.select__gap'),
			caret = selectGap.find('.caret');
		// Add ul list
		$('<ul>', {
			class: 'select__list',
		}).insertAfter(selectGap);

		var selectList = selectGap.next('.select__list');
		// Add li - option items
		for (var i = 0; i < selectOptionLength; i++) {
			$('<li>', {
				class: 'select__item',
				html: $('<span>', {
					text: selectOption.eq(i).text().toUpperCase(),
				}),
			})
				.attr('data-value', selectOption.eq(i).val())
				.appendTo(selectList);
		}
		// Find all items
		var selectItem = selectList.find('li');

		selectList.slideUp(0);
		selectGap.on('click', function () {
			if (!$(this).hasClass('on')) {
				$(this).addClass('on');
				selectList.slideDown(dur);

				selectItem.on('click', function () {
					var chooseItem = $(this).data('value');

					$('select').val(chooseItem).attr('selected', 'selected');
					selectGap.text($(this).attr('data-value'));

					selectList.slideUp(dur);
					selectGap.removeClass('on');
					selectGap.parent().parent().submit()
				});
			} else {
				$(this).removeClass('on');
				selectList.slideUp(dur);
			}
		});
	});



	//^ set payment & blockchain

	const selectCurrency = document.querySelectorAll('.select-currency');

	const listCurrency = {
		'bitcoin': ['Blockchain BTC network', 'Blockchain Solana network', 'Blockchain BSC network',],
		'ethereum': ['Blockchain ETH network', 'Blockchain Solana network', 'Blockchain BSC network',],
		'usdt': ['Blockchain ERC20 network', 'Blockchain Solana network', 'Blockchain BSC network',],
	}

	if (selectCurrency !== null) {
		selectCurrency.forEach(el => {
			let parent = el.closest('div.select')
			let list = parent.querySelector('.select__list')
			list.addEventListener('click', (e) => {
				let chooseCurrency = e.target.innerText.toLowerCase();
				setBlockchains(chooseCurrency)
			})
		})
	}

	function setBlockchains(selectedCurrency) {

		selectCurrency.forEach((select) => {

			let selectedBlockchains = listCurrency[selectedCurrency]
			let mainWrap = select.closest('.popup__selects')

			let blockchain = mainWrap.querySelector('.select-blockchain')
			let blockchainOptions = blockchain.querySelectorAll('option')

			let blockchainWrap = blockchain.closest('div.select')
			let fakeBlockchainOptions = blockchainWrap.querySelectorAll('.select__item')
			let fakeBlockchainHead = blockchainWrap.querySelector('.select__gap')

			blockchainOptions.forEach((el, i) => {
				el.value = selectedBlockchains[i]
				el.innerText = selectedBlockchains[i]
			})
			fakeBlockchainOptions.forEach((el, i) => {
				el.setAttribute('data-value', selectedBlockchains[i])
				el.querySelector('span').innerText = selectedBlockchains[i]
			})
			fakeBlockchainHead.innerText = listCurrency[selectedCurrency][0];
		});
	}
}


//^ toggle services

const sudscribeWrap = document.querySelector('.subscribe__items')
let sudscribeItems = document.querySelectorAll('.subscribe__item')
const preview = document.querySelector('.subscribe__preview')
const previewImage = document.querySelector('.subscribe__preview img')



sudscribeWrap.addEventListener('click', (e) => {
	let widthWindow = document.body.clientWidth;
	if (widthWindow > 768) {
		let current = e.target.closest('.subscribe__item')
		if (current) {
			toggleClass(current, sudscribeItems, 'active')
			togglePreview(current)
		}
	}
})



function toggleClass(current, list, cssClass) {
	list.forEach((el) => el.classList.remove(cssClass));
	current.classList.add(cssClass);
}

function togglePreview(current) {
	let color = current.querySelector('.subscribe__item-img').style.background;
	let logo = current.querySelector('.subscribe__item-img img').src

	preview.style.backgroundColor = color;
	previewImage.src = logo;

}
