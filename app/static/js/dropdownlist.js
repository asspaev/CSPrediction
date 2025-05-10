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

document.body.addEventListener('htmx:afterSwap', (evt) => {
  // Проверяем, что вставка прошла именно в нужный контейнер
  if (evt.detail.target.id === 'predict_result') {
    const input = document.querySelector('.dropdown-input');
    const list = document.getElementById('dropdownList');

    if (!input || !list) return;  // на всякий случай

    // Показываем список при фокусе
    input.addEventListener('focus', () => {
      list.style.display = 'block';
    });

    // Фильтруем опции по вводу
    input.addEventListener('input', () => {
      const value = input.value.toLowerCase();
      list.querySelectorAll('.dropdown-option').forEach(opt => {
        opt.style.display = opt.textContent.toLowerCase().includes(value)
          ? 'block'
          : 'none';
      });
    });

    // Прячем список при потере фокуса
    input.addEventListener('blur', () => {
      setTimeout(() => {
        list.style.display = 'none';
      }, 150);
    });

    // Подставляем значение при клике по опции
    list.addEventListener('mousedown', e => {
      if (e.target.classList.contains('dropdown-option')) {
        input.value = e.target.textContent;
      }
    });
  }
});