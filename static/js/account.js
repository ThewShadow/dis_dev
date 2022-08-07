const account = document.querySelector('.account')
const navLinksBody = document.querySelector('.account__nav');
const navLinks = document.querySelectorAll('.account__nav  a[data-link]');
const navBlocks = document.querySelectorAll('.account__edit-data div[data-block');

if (account !== null) {
	navLinks.forEach((link) => {
		link.addEventListener('click', (e) => {
		  navLinks.forEach((link) => link.classList.remove('active'));
		  e.currentTarget.classList.add('active');
		  navBlocks.forEach((block) => {
			if (block.getAttribute('data-block') === e.currentTarget.getAttribute('data-link')) {
			  block.classList.add('active');
			} else {
			  block.classList.remove('active');
			}
		  });
		});
	  });
	  
	  navLinksBody.addEventListener('click', () => navLinksBody.classList.toggle('opened'));  
}

