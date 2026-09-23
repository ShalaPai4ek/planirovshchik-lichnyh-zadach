# Планировщик личных задач (Task Planner)

Веб-приложение для управления личной продуктивностью. Позволяет структурировать задачи по категориям и приоритетам, отслеживать дедлайны и визуализировать загрузку в формате интерактивного календаря.

---

## Технологический стек

* **Backend:** Python (Flask, Flask-SQLAlchemy, Flask-Login, PyMySQL)
* **Frontend:** HTML5, CSS3, Vanilla JS
* **Database:** MySQL
* **DevOps:** Docker, Docker Compose

---

## Основной функционал

* **Авторизация и профиль:** безопасная регистрация и вход пользователей (`Flask-Login`, хэширование паролей).
* **Управление задачами (Task CRUD):** создание, редактирование, удаление и смена статусов (`pending`, `in_progress`, `completed`).
* **Категоризация:** разделение задач по направлениям (Работа, Учёба, Дом) с возможностью назначения цвета.
* **Приоритеты и сроки:** цветовая индикация приоритета (`low`, `medium`, `high`) и контрольные даты (`due_date`).
* **Фильтрация и сортировка:** удобный поиск задач по названию, статусу, категории и приоритету.
* **Календарь выполнения:** визуализация задач на сетке месяца/недели.

---

## 🗄 Структура базы данных (MySQL)

```mermaid
erDiagram
    USERS ||--o{ CATEGORIES : "создает"
    USERS ||--o{ TASKS : "владеет"
    CATEGORIES ||--o{ TASKS : "содержит"

    USERS {
        int id PK
        string username
        string email
        string password_hash
        timestamp created_at
    }

    CATEGORIES {
        int id PK
        int user_id FK
        string name
        string color
    }

    TASKS {
        int id PK
        int user_id FK
        int category_id FK
        string title
        text description
        enum priority
        enum status
        datetime due_date
        timestamp created_at
    }
