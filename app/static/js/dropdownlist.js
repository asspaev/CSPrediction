const input = document.querySelector('.dropdown-input');
const list = document.getElementById('dropdownList');

input.addEventListener('focus', () => {
  list.style.display = 'block';
});

input.addEventListener('input', () => {
  const value = input.value.toLowerCase();
  const options = list.querySelectorAll('.dropdown-option');
  options.forEach(opt => {
    opt.style.display = opt.textContent.toLowerCase().includes(value) ? 'block' : 'none';
  });
});

input.addEventListener('blur', () => {
  // Задержка, чтобы успел сработать клик по опции
  setTimeout(() => {
    list.style.display = 'none';
  }, 150);
});

list.addEventListener('mousedown', e => {
  if (e.target.classList.contains('dropdown-option')) {
    input.value = e.target.textContent;
  }
});
