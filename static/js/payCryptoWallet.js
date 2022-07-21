let stepsNumber = document.querySelectorAll('.pay-crypto__progress-step')
let stepsAction = document.querySelectorAll('.pay-crypto__action-step')
let congratsBlock = document.querySelector('.pay-crypto__congrats')
let btnNext = document.querySelector('.action-next')
let btnPrew = document.querySelector('.action-prew')

let maxCount = stepsNumber.length + 1
let count = 1

btnNext.addEventListener('click', () => {
	count++
	setCountAndButtons()
	renderSteps()
	console.log(count, maxCount)
})

btnPrew.addEventListener('click', () => {
	count--
	setCountAndButtons()
	renderSteps()
})



function setCountAndButtons() {
	if (count <= 1) {
		count = 1
		btnPrew.style.display = 'none'
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


setCountAndButtons()