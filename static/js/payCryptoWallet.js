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

	var currency = $("input[name=currency_id]:checked")[0].value;
	var blockchain = $("input[name=wallet_id]:checked")[0].value;
	var path = "/service/payments/crypto/create/"
	var json = {
		wallet_id: blockchain
	}
	var res = undefined;
	$.post(document.location.origin + path, json)
		.done(function (resp) {
		    payment_data = resp["payment_data"]
			$('#QR').attr('src', payment_data['qrcode'])
			$("#payment-link").html(payment_data["paycode"])
			$("#blockchain-sum").html(payment_data["price"]+" "+payment_data["currency"])
			$("#blockchain-name").html(payment_data["blockchain"])

			var payInfo = [
				payment_data["blockchain"],
				payment_data["price"],
				payment_data["paycode"],
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

const listCurrency1 = {
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
			// let currentCurrency = input.value.toLowerCase();
			let currentCurrency = input.value;
			setBlockchains(currentCurrency)
			//setBlockchain(currentCurrency)
			return
		}
	})
}
function setBlockchains(currentCurrency) {
    $.post(window.location.origin + '/service/blockchains/list/', {'currency_id': currentCurrency})
     .done((resp)=>{
        console.log(resp);
        $(".blockchain_el").remove();
        if (resp['success']) {
            resp['wallets'].forEach((element) => {
                  html_ = `<label class="blockchain_el">`
                            +`<input type="radio" name="wallet_id" value="${element["id"]}" checked>`
                            +`<span>${element["blockchain_name"]}</span>`;
                          +`</label>`;
                  $("#blockchain_list").append(html_)
            });
        }
     });
}

function setBlockchain(currentCurrency) {
	let arrBlockchain = listCurrency[currentCurrency]
	arrBlockchain.map((el, i) => {
		inputsBlockchain[i].querySelector('input').value = el
		inputsBlockchain[i].querySelector('span').innerText = el
	})
}

setCountAndButtons()
selectCurrency()
