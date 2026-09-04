import os
import time
from datetime import datetime

from flask import Flask, redirect, render_template_string, request, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError

app = Flask(__name__)


def get_database_uri():
    url = os.getenv("DATABASE_URL", "").strip()
    if not url:
        basedir = os.path.abspath(os.path.dirname(__file__))
        return "sqlite:///" + os.path.join(basedir, "tasks.db")
    if url.startswith("postgres://"):
        return "postgresql://" + url[len("postgres://") :]
    return url


app.config["SQLALCHEMY_DATABASE_URI"] = get_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    author = db.Column(db.String(50), default="От кого")
    assignee = db.Column(db.String(50), default="Кому")


HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>Список задач</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #0b0a0f;
            color: #e8e4f0;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
            padding-top: max(20px, env(safe-area-inset-top));
            padding-bottom: max(20px, env(safe-area-inset-bottom));
        }

        .container {
            max-width: 820px;
            width: 100%;
            background: #13111a;
            padding: 40px 36px 48px;
            border-radius: 28px;
            border: 1px solid #2a2438;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
        }

        h1 {
            font-size: 30px;
            font-weight: 700;
            margin-bottom: 32px;
            color: #c4b5fd;
            text-shadow: 0 0 40px rgba(139, 92, 246, 0.15);
            text-align: center;
            letter-spacing: -0.02em;
        }

        .card {
            background: #0c0a12;
            border: 1px solid #2a2438;
            border-radius: 18px;
            padding: 28px 30px;
            margin-bottom: 24px;
            transition: border-color 0.25s;
        }

        .card:hover {
            border-color: #4a3a6a;
        }

        label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: #8b83a0;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 18px;
            margin-bottom: 6px;
        }

        label:first-of-type {
            margin-top: 0;
        }

        input[type="text"],
        textarea {
            width: 100%;
            padding: 14px 18px;
            background: #0b0a0f;
            border: 1px solid #2a2438;
            border-radius: 14px;
            color: #e8e4f0;
            font-size: 15px;
            font-family: inherit;
            transition: 0.25s;
        }

        input[type="text"]:focus,
        textarea:focus {
            outline: none;
            border-color: #8b5cf6;
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
            background: #100d1a;
        }

        textarea {
            min-height: 80px;
            resize: vertical;
        }

        .btn {
            border: none;
            border-radius: 14px;
            padding: 12px 20px;
            min-height: 44px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: 0.2s;
            text-align: center;
            color: #fff;
            width: 100%;
            -webkit-tap-highlight-color: transparent;
        }

        .btn-primary {
            background: #8b5cf6;
            padding: 14px 28px;
            font-size: 15px;
            margin-top: 20px;
        }

        .btn-primary:hover {
            background: #7c3aed;
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.25);
            transform: scale(1.01);
        }

        .btn-success {
            background: #1a7a3a;
        }

        .btn-success:hover {
            background: #229a4a;
        }

        .btn-danger {
            background: #7a1a1a;
        }

        .btn-danger:hover {
            background: #9a2222;
        }

        .btn-undo {
            background: #4a3a6a;
        }

        .btn-undo:hover {
            background: #5a4a8a;
        }

        .empty {
            text-align: center;
            color: #4a3a5a;
            padding: 24px 0 8px;
            font-size: 16px;
        }

        .task {
            display: flex;
            justify-content: space-between;
            gap: 24px;
            align-items: stretch;
            background: #0c0a12;
            border: 1px solid #2a2438;
            border-radius: 18px;
            padding: 24px 28px;
            margin-bottom: 18px;
            transition: 0.25s;
            flex-wrap: wrap;
        }

        .task:hover {
            border-color: #4a3a6a;
            background: #100d1a;
        }

        .task.done {
            background: #0d1a0d;
            border-color: #2a5a3a;
        }

        .task-content {
            flex: 1 1 60%;
            min-width: 220px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .task-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            flex-wrap: wrap;
        }

        .task-title {
            margin: 0;
            font-size: 19px;
            font-weight: 600;
            color: #f0ecf5;
            overflow-wrap: anywhere;
            word-break: break-word;
            flex: 1;
            min-width: 0;
        }

        .task.done .task-title {
            text-decoration: line-through;
            color: #7a9a7a;
        }

        .task-description {
            color: #8b83a0;
            font-size: 15px;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
            word-break: break-word;
            line-height: 1.6;
            margin: 0;
            padding: 4px 0;
        }

        .task.done .task-description {
            text-decoration: line-through;
            color: #7a9a7a;
        }

        .task-meta-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 6px 20px;
            margin-top: 8px;
            padding-top: 10px;
            border-top: 1px solid #1a1822;
        }

        .meta-item {
            display: flex;
            flex-wrap: wrap;
            gap: 4px 6px;
            font-size: 13px;
            line-height: 1.6;
            color: #5a4a6a;
        }

        .meta-label {
            color: #6a5a7a;
            font-weight: 500;
            letter-spacing: 0.02em;
        }

        .meta-value {
            color: #b0a8c0;
            word-break: break-all;
            overflow-wrap: break-word;
        }

        .badge {
            display: inline-block;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 14px;
            border-radius: 30px;
            white-space: nowrap;
            letter-spacing: 0.02em;
        }

        .badge-done {
            background: #1a3a2a;
            color: #6aca8a;
            border: 1px solid #2a5a3a;
        }

        .badge-pending {
            background: #1a1822;
            color: #8a7aaa;
            border: 1px solid #2a2438;
        }

        .actions {
            display: flex;
            flex-direction: column;
            gap: 10px;
            min-width: 140px;
            flex: 0 0 auto;
            justify-content: flex-start;
            padding-top: 4px;
        }

        .actions .btn {
            margin: 0;
            padding: 10px 16px;
            font-size: 14px;
            width: 100%;
            min-width: 120px;
        }

        @media (max-width: 700px) {
            .task {
                flex-direction: column;
                align-items: stretch;
                padding: 20px 18px;
            }

            .task-content {
                flex: 1 1 auto;
                min-width: 0;
            }

            .task-header {
                flex-direction: column;
                align-items: flex-start;
            }

            .actions {
                flex-direction: row;
                flex-wrap: wrap;
                justify-content: stretch;
                min-width: 0;
                width: 100%;
                gap: 8px;
                padding-top: 12px;
                border-top: 1px solid #1a1822;
            }

            .actions .btn {
                flex: 1 1 45%;
                min-width: 80px;
                padding: 10px 12px;
                font-size: 13px;
            }

            .task-meta-grid {
                grid-template-columns: 1fr 1fr;
            }

            .container {
                padding: 24px 16px 32px;
            }

            h1 {
                font-size: 24px;
            }

            .card {
                padding: 18px 16px;
            }
        }

        @media (max-width: 450px) {
            .task-meta-grid {
                grid-template-columns: 1fr;
            }

            .actions {
                flex-direction: column;
            }

            .actions .btn {
                flex: 1 1 auto;
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Список задач</h1>

        <section class="card">
            <form action="{{ url_for('add_task') }}" method="post">
                <label for="title">Название</label>
                <input type="text" id="title" name="title" required placeholder="Что нужно сделать?">

                <label for="description">Описание</label>
                <textarea id="description" name="description" placeholder="Подробности"></textarea>

                <label for="author">Кто добавил</label>
                <input type="text" id="author" name="author" placeholder="Ваше имя">

                <label for="assignee">Кому надо сделать</label>
                <input type="text" id="assignee" name="assignee" placeholder="Кому назначено">

                <button class="btn btn-primary" type="submit">Добавить задачу</button>
            </form>
        </section>

        {% if tasks %}
            {% for task in tasks %}
                <article class="card task {% if task.completed %}done{% endif %}">
                    <div class="task-content">
                        <div class="task-header">
                            <h2 class="task-title">{{ task.title }}</h2>
                            <div class="task-status">
                                {% if task.completed %}
                                    <span class="badge badge-done">✓ Выполнено</span>
                                {% else %}
                                    <span class="badge badge-pending">○ В процессе</span>
                                {% endif %}
                            </div>
                        </div>
                        {% if task.description %}
                            <p class="task-description">{{ task.description }}</p>
                        {% endif %}
                        <div class="task-meta-grid">
                            <div class="meta-item">
                                <span class="meta-label">Автор:</span>
                                <span class="meta-value">{{ task.author }}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Исполнитель:</span>
                                <span class="meta-value">{{ task.assignee }}</span>
                            </div>
                            <div class="meta-item">
                                <span class="meta-label">Создана:</span>
                                <span class="meta-value">{{ task.created_at.strftime('%d.%m.%Y %H:%M') }}</span>
                            </div>
                        </div>
                    </div>
                    <div class="actions">
                        {% if task.completed %}
                            <form action="{{ url_for('undo_task', id=task.id) }}" method="post">
                                <button class="btn btn-undo" type="submit">↩ Вернуть</button>
                            </form>
                        {% else %}
                            <form action="{{ url_for('complete_task', id=task.id) }}" method="post">
                                <button class="btn btn-success" type="submit">✓ Выполнено</button>
                            </form>
                        {% endif %}
                        <form action="{{ url_for('delete_task', id=task.id) }}" method="post">
                            <button class="btn btn-danger" type="submit">✕ Удалить</button>
                        </form>
                    </div>
                </article>
            {% endfor %}
        {% else %}
            <section class="card">
                <p class="empty">Пока нет задач. Добавьте первую задачу.</p>
            </section>
        {% endif %}
    </div>
</body>
</html>
"""


@app.route("/")
def index():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return render_template_string(HTML_TEMPLATE, tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = (request.form.get("title") or "").strip()
    description = (request.form.get("description") or "").strip() or None
    author = (request.form.get("author") or "Аноним").strip()
    assignee = (request.form.get("assignee") or "Не назначен").strip()
    if title:
        db.session.add(Task(
            title=title,
            description=description,
            author=author,
            assignee=assignee,
        ))
        db.session.commit()
    return redirect(url_for("index"))


@app.route("/complete/<int:id>", methods=["POST"])
def complete_task(id):
    task = Task.query.get_or_404(id)
    task.completed = True
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/undo/<int:id>", methods=["POST"])
def undo_task(id):
    task = Task.query.get_or_404(id)
    task.completed = False
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:id>", methods=["POST"])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("index"))


def init_db():
    for _ in range(30):
        try:
            db.create_all()
            return
        except OperationalError:
            time.sleep(2)
    db.create_all()


with app.app_context():
    init_db()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
