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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Список задач</title>
    <style>
        :root {
            --bg: #0b0a0f;
            --card: #13111a;
            --text: #e8e4f0;
            --muted: #8b83a0;
            --accent: #8b5cf6;
            --accent-hover: #7c3aed;
            --done: #1a142b;
            --done-border: #6d28d9;
            --danger: #dc2626;
            --danger-hover: #b91c1c;
            --success: #8b5cf6;
            --success-hover: #7c3aed;
            --border: #2a2438;
            --shadow: 0 10px 30px rgba(0, 0, 0, 0.7);
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .container {
            max-width: 760px;
            width: 100%;
            margin: 0 auto;
        }

        h1 {
            margin: 0 0 28px;
            font-size: 32px;
            font-weight: 700;
            letter-spacing: -0.03em;
            text-align: center;
            color: #c4b5fd;
            text-shadow: 0 0 40px rgba(139, 92, 246, 0.15);
        }

        .card {
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            box-shadow: var(--shadow);
            padding: 24px;
            margin-bottom: 20px;
            transition: border-color 0.25s;
        }

        .card:hover {
            border-color: #4a3a6a;
        }

        form {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }

        label {
            font-size: 13px;
            font-weight: 600;
            color: var(--muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        input[type="text"],
        textarea {
            width: 100%;
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 12px 14px;
            font-size: 15px;
            font-family: inherit;
            color: var(--text);
            background: #0c0a12;
            transition: 0.25s;
        }

        input[type="text"]:focus,
        textarea:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 0 4px rgba(139, 92, 246, 0.15);
            background: #100d1a;
        }

        textarea {
            min-height: 88px;
            resize: vertical;
        }

        .btn {
            border: none;
            border-radius: 10px;
            padding: 10px 14px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s ease, transform 0.15s ease;
        }

        .btn-undo {
            background: #4a4a6a;
            color: #fff;
        }

        .btn-undo:hover {
            background: #5a5a8a;
        }

        .btn:hover {
            transform: translateY(-1px);
        }

        .btn-primary {
            background: var(--accent);
            color: #fff;
            padding: 12px 16px;
            margin-top: 4px;
        }

        .btn-primary:hover {
            background: var(--accent-hover);
            box-shadow: 0 0 30px rgba(139, 92, 246, 0.25);
        }

        .btn-success {
            background: var(--success);
            color: #fff;
        }

        .btn-success:hover {
            background: var(--success-hover);
        }

        .btn-danger {
            background: var(--danger);
            color: #fff;
        }

        .btn-danger:hover {
            background: var(--danger-hover);
        }

        .empty {
            text-align: center;
            color: var(--muted);
            padding: 16px 0 4px;
        }

        .task {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: flex-start;
            background: var(--card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 20px 22px;
            margin-bottom: 14px;
            transition: 0.25s;
        }

        .task:hover {
            border-color: #4a3a6a;
        }

        .task.done {
            background: var(--done);
            border-color: var(--done-border);
        }

        .task-title {
            margin: 0 0 6px;
            font-size: 18px;
            font-weight: 650;
            color: #e8e4f0;
        }

        .task.done .task-title,
        .task.done .task-description {
            text-decoration: line-through;
            color: #7a6a9a;
        }

        .task-description {
            margin: 0 0 10px;
            color: var(--muted);
            white-space: pre-wrap;
        }

        .task-meta {
            font-size: 12px;
            color: #4a3a5a;
        }

        .actions {
            display: flex;
            flex-direction: column;
            gap: 8px;
            min-width: 150px;
        }

        @media (max-width: 640px) {
            .task {
                flex-direction: column;
            }

            .actions {
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
    
    <label for="author">кто добавил</label>
    <input type="text" id="author" name="author" placeholder="Ваше имя">
    
    <label for="assignee">кому надо сделать</label>
    <input type="text" id="assignee" name="assignee" placeholder="Кому назначено">
    
    <button class="btn btn-primary" type="submit">Добавить задачу</button>
</form>
        </section>

        {% if tasks %}
            {% for task in tasks %}
                <article class="card task {% if task.completed %}done{% endif %}">
                    <div>
                        <h2 class="task-title">{{ task.title }}</h2>
                        {% if task.description %}
                            <p class="task-description">{{ task.description }}</p>
                        {% endif %}
                        <div class="task-meta">
    👤 {{ task.author }} → 👤 {{ task.assignee }}<br>
    {{ task.created_at.strftime('%d.%m.%Y %H:%M') }}
</div>
                    <div class="actions">
                        {% if task.completed %}
                            <form action="{{ url_for('undo_task', id=task.id) }}" method="post">
                                <button class="btn btn-undo" type="submit">Вернуть</button>
                            </form>
                        {% else %}
                            <form action="{{ url_for('complete_task', id=task.id) }}" method="post">
                                <button class="btn btn-success" type="submit">Выполнено</button>
                            </form>
                        {% endif %}
                        <form action="{{ url_for('delete_task', id=task.id) }}" method="post">
                            <button class="btn btn-danger" type="submit">Удалить</button>
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
            assignee=assignee
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
