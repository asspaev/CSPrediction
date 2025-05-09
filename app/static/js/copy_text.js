function copyInput() {
    const input = document.getElementById("copyInput");
    navigator.clipboard.writeText(input.value).catch(err => {
        console.error("Ошибка копирования: ", err);
    });
}