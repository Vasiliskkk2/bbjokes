import random
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, jsonify, request
from collections import defaultdict
import time
from os import listdir
from os.path import isfile, join

app = Flask(__name__)

# Данные для хранения анекдотов и количества лайков/дизлайков с IP-адресами
jokes_data = defaultdict(lambda: {"joke": "", "likes": 0, "dislikes": 0, "rated_ips": {}})
top_jokes = []
rate_limit = defaultdict(lambda: {"last_request_time": 0, "count": 0})

# Эндпоинт для парсинга случайного анекдота с сайта
@app.route("/api/get_joke")
def get_joke():
    url = "https://anekdot.ru/random/anekdot/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем текст анекдота в нужном блоке
        joke_element = soup.find("div", class_="text")
        joke = joke_element.text.strip() if joke_element else "Не удалось получить анекдот"

        # Если анекдот новый, добавляем его в данные
        if joke not in jokes_data:
            jokes_data[joke] = {"joke": joke, "likes": 0, "dislikes": 0, "rated_ips": {}}

        return jsonify({"joke": joke})
    except requests.RequestException:
        return jsonify({"error": "Не удалось получить анекдот"}), 503

# Функция для ограничения частоты запросов с одного IP
def rate_limit_check(ip):
    current_time = time.time()
    if current_time - rate_limit[ip]["last_request_time"] < 5:  # Ограничение 5 секунд между запросами
        rate_limit[ip]["count"] += 1
    else:
        rate_limit[ip] = {"last_request_time": current_time, "count": 1}
    return rate_limit[ip]["count"] <= 5

# Эндпоинт для добавления лайка анекдоту с проверкой IP-адреса
@app.route("/api/like_joke", methods=["POST"])
def like_joke():
    data = request.json
    joke_text = data.get("joke")
    ip_address = request.remote_addr

    # Проверка частоты запросов с одного IP
    if not rate_limit_check(ip_address):
        return jsonify({"error": "Слишком много запросов. Подождите и попробуйте снова."}), 429

    # Проверка анекдота в базе данных
    if joke_text in jokes_data:
        # Проверка, оценивал ли уже этот IP-адрес анекдот
        if ip_address in jokes_data[joke_text]["rated_ips"]:
            return jsonify({"error": "Вы уже оценили этот анекдот"}), 403
        # Увеличение лайков и добавление IP-адреса в список оценивших
        jokes_data[joke_text]["likes"] += 1
        jokes_data[joke_text]["rated_ips"][ip_address] = "like"
        update_top_jokes()  # Обновляем топ-10 анекдотов
        return jsonify({"likes": jokes_data[joke_text]["likes"], "dislikes": jokes_data[joke_text]["dislikes"]})
    return jsonify({"error": "Анекдот не найден"}), 404

# Эндпоинт для добавления дизлайка анекдоту с проверкой IP-адреса
@app.route("/api/dislike_joke", methods=["POST"])
def dislike_joke():
    data = request.json
    joke_text = data.get("joke")
    ip_address = request.remote_addr

    # Проверка частоты запросов с одного IP
    if not rate_limit_check(ip_address):
        return jsonify({"error": "Слишком много запросов. Подождите и попробуйте снова."}), 429

    # Проверка анекдота в базе данных
    if joke_text in jokes_data:
        # Проверка, оценивал ли уже этот IP-адрес анекдот
        if ip_address in jokes_data[joke_text]["rated_ips"]:
            return jsonify({"error": "Вы уже оценили этот анекдот"}), 403
        # Увеличение дизлайков и добавление IP-адреса в список оценивших
        jokes_data[joke_text]["dislikes"] += 1
        jokes_data[joke_text]["rated_ips"][ip_address] = "dislike"
        update_top_jokes()  # Обновляем топ-10 анекдотов
        return jsonify({"likes": jokes_data[joke_text]["likes"], "dislikes": jokes_data[joke_text]["dislikes"]})
    return jsonify({"error": "Анекдот не найден"}), 404

# Функция для обновления списка топ-10 анекдотов по количеству лайков
def update_top_jokes():
    global top_jokes
    # Сортируем по количеству лайков, без учета дизлайков
    sorted_jokes = sorted(jokes_data.values(), key=lambda x: x["likes"], reverse=True)
    top_jokes = sorted_jokes[:10]

# Эндпоинт для получения топ-10 анекдотов
@app.route("/api/top_jokes")
def get_top_jokes():
    return jsonify(top_jokes)

# Эндпоинт для проверки файлов в папке static/images
@app.route("/check_static")
def check_static():
    image_files = [f for f in listdir("static/images") if isfile(join("static/images", f))]
    return jsonify(image_files)

# Главная страница
@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

