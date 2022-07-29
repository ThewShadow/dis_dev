let stepsNumber = document.querySelectorAll('.pay-crypto__progress-step')
let stepsAction = document.querySelectorAll('.pay-crypto__action-step')
let congratsBlock = document.querySelector('.pay-crypto__congrats')
let btnNext = document.querySelector('.action-next')
let btnPrew = document.querySelector('.action-prew')

let maxCount = stepsNumber.length + 1
let count = 1

var previousStep = 0
var fail = false;


$('.action-prew').click((event) => {
	event.preventDefault();
	previousStep = count
	prev()
});

$('.action-next').click((event) => {
	event.preventDefault();
	previousStep = count

	if (count + 1 >= maxCount) {
		confirmProofHash()
	} else if (previousStep == 2 && count + 1 == 3) {
		renderQR();
		next()
	} else {
		next()
	}

});

function prev() {
	previousStep = count
	count--
	setCountAndButtons()
	renderSteps()
}

function next() {
	previousStep = count
	count++
	setCountAndButtons()
	renderSteps()
	console.log(count, maxCount)
}


function setCountAndButtons() {
	if (count <= 1) {
		count = 1
		if (btnPrew !== null) {
			btnPrew.style.display = 'none'
		}
	}

	else if (count >= maxCount) {
		count = maxCount
		btnNext.style.display = 'none'
		btnPrew.style.display = 'none'
		congratsBlock.style.display = 'block'
	}

	else {
		btnNext.style.display = 'block'
		btnPrew.style.display = 'block'
	}

}

function renderSteps() {
	for (let i = 1; i < maxCount; i++) {
		let currNum = stepsNumber[i - 1]
		let currAction = stepsAction[i - 1]

		if (i < count) {
			currNum.classList.remove('current')
			currNum.classList.add('done')
			currAction.classList.remove('active')
		}
		else if (i == count) {
			currNum.classList.add('current')
			currNum.classList.remove('done')
			currAction.classList.add('active')
		}
		else {
			currNum.classList.remove('current')
			currNum.classList.remove('done')
			currAction.classList.remove('active')
		}
	}
}


function confirmProofHash() {
	var data_array = $('#proof-form').serializeArray();
	var json = getJson(data_array);

	$.post(window.location.origin + "/service/crypto_payment_confirm/", json)
		.done((resp) => {
			next();
		}).fail((resp) => {
			showMessages(resp, 'proof-form');
		});
}

function renderQR() {

	var currency = $("input[name=currency]:checked")[0].value;
	var blockchain = $("input[name=blockchain]:checked")[0].value;
	var path = "/service/payments/crypto/create/"
	var json = {
		currency: currency,
		blockchain: blockchain
	}
	var res = undefined;
	$.post(document.location.origin + path, json)
		.done(function (resp) {
			$('#QR').attr('src', resp['qr'])
			$("#payment-link").html(resp["payment_link"])
			$("#blockchain-sum").html(resp["amount"])
			$("#blockchain-name").html(resp["blockchain_name"])

			var payInfo = [
				resp["blockchain_name"],
				resp["amount"],
				resp["payment_link"],
			];
			$("#pay-info").attr("value", payInfo.join())
		})
		.fail(function (resp) {
			res = resp;
		});
	return res;
}


//^ currency & blockchain

const inputsCurrency = document.querySelectorAll('#crypto_currency-form input')
const inputsBlockchain = document.querySelectorAll('#blockchain-form label')

const listCurrency = {
	'bitcoin': ['Blockchain BTC network', 'Blockchain Solana network', 'Blockchain BSC network',],
	'ethereum': ['Blockchain ETH network', 'Blockchain Solana network', 'Blockchain BSC network',],
	'usdt': ['Blockchain ERC20 network', 'Blockchain Solana network', 'Blockchain BSC network',],
}

if (inputsCurrency !== null) {
	inputsCurrency.forEach(input => {
		input.addEventListener('click', selectCurrency)
	})
}

function selectCurrency() {
	inputsCurrency.forEach(input => {
		if (input.checked) {
			let currentCurrency = input.value.toLowerCase();
			setBlockchain(currentCurrency)
			return
		}
	})
}

function setBlockchain(currentCurrency) {
	let arrBlockchain = listCurrency[currentCurrency]
	arrBlockchain.map((el, i) => {
		inputsBlockchain[i].querySelector('input').value = el
		inputsBlockchain[i].querySelector('span').innerText = el
	})
}

setCountAndButtons()

