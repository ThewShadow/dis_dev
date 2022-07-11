let faqItems = document.querySelector('.faq__items');
let details = document.querySelectorAll('.faq__items details');

faqItems.addEventListener('click', (e) => {
  if (e.target.nodeName === 'SUMMARY') {
    e.preventDefault();
    let parent = e.target.parentElement;
    let isOpenParent = parent.open;

    if (isOpenParent) {
      parent.open = false;
    } else {
      details.forEach((el) => (el.open = false));
      parent.open = true;
    }
  }
});
