Веб-приложение с нейросетью, которая определяет кошка на фото или собака.

## Что внутри

- нейросеть MobileNetV2 на TensorFlow
- бэкенд на FastAPI
- фронтенд на чистом HTML/CSS/JS
- история предсказаний

## Как запустить

Склонируй репозиторий:

```
git clone https://github.com/ned0ra/cat-vs-dog.git
cd cat-vs-dog
```
Создай виртуальное окружение:
```
python3 -m venv venv
source venv/bin/activate
```
Установи зависимости:
```
pip install -r requirements.txt
```
Обучи модель (если нет готовой):
python train.py
```
Запусти сервер:
```
python app.py
```
Открой в браузере: http://localhost:8000

Как пользоваться

перетащи фото в зону загрузки
или нажми "Выбрать файл"
через пару секунд увидишь результат и процент уверенности
все предсказания сохраняются в истории

Структура
```
.
app.py              # основной сервер
train.py            # обучение модели
models/             # сохраненная модель
static/             # стили и скрипты
templates/          # html страница
data/               # датасет https://www.kaggle.com/datasets/d4rklucif3r/cat-and-dogs
requirements.txt    # зависимости
```
Модель не найдена — сначала запусти python train.py

Порт занят — поменяй 8000 на другой в последней строке app.py
