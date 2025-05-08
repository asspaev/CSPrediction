const form = document.querySelector(".form");
const resultDiv = document.getElementById("result");

function updateFormSpacing() {
const empty = resultDiv.textContent.trim() === "";
form.classList.toggle("hide-result-gap", empty);
}

// Срабатывает при любом HTMX обновлении
document.body.addEventListener("htmx:afterSettle", updateFormSpacing);

// Также при загрузке
document.addEventListener("DOMContentLoaded", updateFormSpacing);