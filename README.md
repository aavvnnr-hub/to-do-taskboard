# Список задач (To-Do List)

Веб-приложение для управления задачами: добавление, отметка выполнения, возврат и удаление. По умолчанию используется SQLite. При заданной переменной `DATABASE_URL` приложение подключается к PostgreSQL.

Проект: [https://flask-todo-app.onrender.com](https://flask-todo-app.onrender.com)

## Стек технологий

- Python
- Flask
- SQLite (по умолчанию) / PostgreSQL
- Gunicorn
- Render

## Локальный запуск

1. Клонируйте репозиторий:

```bash
git clone <url-репозитория>
cd devops-project
```

2. Создайте виртуальное окружение и установите зависимости:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

3. Запустите приложение:

```bash
python app.py
```

Откройте [http://localhost:5000](http://localhost:5000)

Через Gunicorn:

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

## Деплой на Render

1. Запушьте репозиторий на GitHub.
2. Войдите в [Render](https://dashboard.render.com/) и создайте новый Blueprint (`New` → `Blueprint`).
3. Подключите репозиторий. Render прочитает `render.yaml` и создаст веб-сервис.
4. Дождитесь окончания сборки и откройте адрес сервиса.

Ручной деплой без Blueprint:

1. `New` → `Web Service`, укажите репозиторий.
2. Runtime: `Python`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn --bind 0.0.0.0:$PORT app:app`
5. Создайте сервис и дождитесь деплоя.

После деплоя приложение будет доступно по адресу:

[https://flask-todo-app.onrender.com](https://flask-todo-app.onrender.com)

Порт берётся из переменной `PORT`, её Render задаёт сам.

База по умолчанию — SQLite (`tasks.db`). На бесплатном плане Render файловая система временная: данные SQLite могут пропасть после рестарта. Чтобы перейти на PostgreSQL, создайте базу в Render и добавьте переменную окружения:

```text
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Приложение само заменит схему `postgres://` на `postgresql://`, если Render отдаст старый формат URL.

## Структура проекта

```text
.
├── app.py
├── requirements.txt
├── render.yaml
├── Dockerfile
├── docker-compose.yml
├── pip.conf
├── .env.example
├── .gitignore
└── README.md
```

## Скриншот работы приложения

![Скриншот приложения](docs/screenshot.png)

## Что я научился делать в этом проекте

- Собирать Flask-приложение с SQLAlchemy
- Делать CRUD-операции: добавление, выполнение, возврат и удаление
- Переключать SQLite и PostgreSQL через `DATABASE_URL`
- Запускать приложение через Gunicorn
- Деплоить сервис на Render по `render.yaml`

## Контакты

- GitHub: [github.com/your-username](https://github.com/your-username)
- Email: your.email@example.com
