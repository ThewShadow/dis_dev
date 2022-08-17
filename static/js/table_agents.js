window.addEventListener('load', () => {
  const table = document.querySelector('.table-ref');
  let rows = table.querySelectorAll('li');

  rows.forEach((row) => {
    let include = row.querySelector('ul li');
    if (include !== null) {
      row.classList.add('in');
    }
    console.log(row);
    console.log(include);
  });

  table.addEventListener('click', (e) => {
    if (e.target.closest('li')) {
      let row = e.target.closest('li');

      if (row.classList.contains('in')) {
        row.classList.toggle('open');
      }
    }
  });
});
