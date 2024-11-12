let currentJoke = "";
let jokeHistory = []; // Массив для хранения истории анекдотов
let currentJokeIndex = -1; // Индекс текущего анекдота

// Функция для получения анекдота
function fetchJoke() {
    fetch("/api/get_joke")
        .then(response => response.json())
        .then(data => {
            const joke = data.joke;
            if (!jokeHistory.includes(joke)) { // Проверка на уникальность анекдота
                jokeHistory.push(joke);
            }
            currentJokeIndex = jokeHistory.length - 1; // Обновляем текущий индекс
            displayJoke(joke); // Показываем анекдот
        })
        .catch(error => handleError("Ошибка при загрузке анекдота:", error));
}

// Функция для отображения анекдота на странице
function displayJoke(joke) {
    document.getElementById("joke").innerText = joke;
    document.getElementById("like-count").innerText = "Лайков: 0";
    document.getElementById("dislike-count").innerText = "Дизлайков: 0";
    currentJoke = joke;
}

// Функция для перехода к предыдущему анекдоту
function fetchPreviousJoke() {
    if (currentJokeIndex > 0) { // Проверка, если есть предыдущий анекдот
        currentJokeIndex--; // Переход к предыдущему анекдоту
        displayJoke(jokeHistory[currentJokeIndex]); // Показываем предыдущий анекдот
    }
}

// Обработка ошибок
function handleError(message, error) {
    console.error(message, error);
    alert(message);
}

// Функция для лайка анекдота с проверкой
function likeJoke() {
    handleLikeDislike("/api/like_joke", "like");
}

// Функция для дизлайка анекдота с проверкой
function dislikeJoke() {
    handleLikeDislike("/api/dislike_joke", "dislike");
}

// Универсальная функция для обработки лайков и дизлайков
function handleLikeDislike(endpoint, type) {
    const joke = jokeHistory[currentJokeIndex];
    const likeButton = document.querySelector(".like-button");
    const dislikeButton = document.querySelector(".dislike-button");

    // Деактивация кнопок для предотвращения быстрого повторного нажатия
    likeButton.disabled = true;
    dislikeButton.disabled = true;

    fetch(endpoint, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ joke })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                alert(data.error);
                throw new Error(data.error);
            });
        }
        return response.json();
    })
    .then(data => {
        document.getElementById("like-count").innerText = `Лайков: ${data.likes}`;
        document.getElementById("dislike-count").innerText = `Дизлайков: ${data.dislikes}`;
        fetchTopJokes(); // Обновляем топ-10 шуток после оценки
    })
    .catch(error => handleError(`Ошибка при ${type === "like" ? "лайке" : "дизлайке"} анекдота:`, error))
    .finally(() => {
        likeButton.disabled = false;
        dislikeButton.disabled = false;
    });
}

// Функция для получения топ-10 шуток
function fetchTopJokes() {
    fetch("/api/top_jokes")
        .then(response => response.json())
        .then(data => {
            const topJokesList = document.getElementById("top-jokes-list");
            topJokesList.innerHTML = "";
            data.forEach((joke, index) => {
                const listItem = document.createElement("li");
                listItem.textContent = `${index + 1}. ${joke.joke} — Лайков: ${joke.likes}, Дизлайков: ${joke.dislikes}`;
                topJokesList.appendChild(listItem);
            });
        })
        .catch(error => handleError("Ошибка при получении топ-10 шуток:", error));
}

// Загрузка анекдота при открытии страницы
document.addEventListener("DOMContentLoaded", () => {
    fetchJoke();
    fetchTopJokes();
});

// Анимация глаз для слежения за курсором
document.addEventListener("mousemove", (event) => {
    const eyes = document.querySelectorAll(".eye");
    window.requestAnimationFrame(() => {
        eyes.forEach((eye) => {
            const pupil = eye.querySelector(".pupil");
            const eyeRect = eye.getBoundingClientRect();
            const eyeCenterX = eyeRect.left + eyeRect.width / 2;
            const eyeCenterY = eyeRect.top + eyeRect.height / 2;
            const angle = Math.atan2(event.clientY - eyeCenterY, event.clientX - eyeCenterX);
            const maxOffset = 15;
            const pupilX = Math.cos(angle) * maxOffset;
            const pupilY = Math.sin(angle) * maxOffset;
            pupil.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
        });
    });
});







