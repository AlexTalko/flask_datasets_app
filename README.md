# Flask EMG Data Analysis App

## Описание проекта

Веб-приложение для анализа данных электромиографии (EMG) с возможностью:
- Загрузки и хранения наборов данных в формате Excel
- Визуализации временных рядов EMG-сигналов и угловых показателей
- Автоматического обнаружения особых пиков в данных
- Предоставления статистики по наборам данных
- Доступа через веб-интерфейс и REST API

## Структура проекта

```
flask_datasets_app/
├── app/
│   ├── __init__.py             # Инициализация приложения
│   ├── models.py               # Модели БД: Dataset и DataPoint
│   ├── utils.py                # Алгоритмы анализа (count_special_peaks)
│   ├── main/                   # Веб-интерфейс
│   │   ├── __init__.py         
│   │   └── routes.py           # Маршруты: /, /dataset/, /add_dataset
│   ├── api/                    # REST API
│   │   ├── __init__.py         
│   │   └── routes.py           # Маршруты: /api/datasets
│   ├── templates/              # HTML шаблоны
│   │   ├── index.html          # Список наборов
│   │   ├── dataset.html        # Детали набора
│   │   └── add_dataset.html    # Форма загрузки
│   └── static/                 
│       └── style.css           # Стилизация
├── .env                        # Конфигурация
├── requirements.txt            # Зависимости
└── run.py                      # Точка входа
```

## Технологический стек

### Backend
- **Python 3.7+**
- **Flask** - веб-фреймворк
- **Flask-SQLAlchemy** - работа с БД
- **PostgreSQL** - хранение данных
- **Pandas** - обработка Excel-файлов
- **SciPy** - анализ сигналов
- **Plotly** - генерация графиков

### Frontend
- **HTML5** - структура страниц
- **Bootstrap** - адаптивный дизайн
- **CSS** - базовая стилизация

## Маршруты приложения

### Веб-интерфейс
| Маршрут              | Метод | Описание                          |
|----------------------|-------|-----------------------------------|
| `/`                  | GET   | Главная страница                  |
| `/dataset/<int:id>`  | GET   | Просмотр набора данных            |
| `/add_dataset`       | GET   | Форма загрузки данных             |
| `/add_dataset`       | POST  | Обработка загруженных данных      |

### REST API
| Маршрут                   | Метод | Описание                          |
|---------------------------|-------|-----------------------------------|
| `/api/datasets`           | GET   | Получить список наборов          |
| `/api/datasets`           | POST  | Загрузить новый набор            |
| `/api/datasets/<int:id>`  | GET   | Получить данные набора           |
| `/api/datasets/<int:id>`  | DELETE| Удалить набор данных             |

## Взаимодействие с приложением

### Через веб-интерфейс
1. Пользователь открывает главную страницу (`/`)
2. Сервер отображает список доступных наборов данных
3. При переходе на `/dataset/<id>`:
   - Сервер загружает данные из БД
   - Генерирует графики с помощью Plotly
   - Анализирует данные с помощью count_special_peaks()
   - Возвращает готовую HTML-страницу с результатами

### Через REST API
```mermaid
sequenceDiagram
    Клиент->>Сервер: POST /api/datasets (Excel-файл)
    Сервер->>Pandas: Чтение данных
    Сервер->>БД: Сохранение данных
    Сервер-->>Клиент: JSON с результатом
    
    Клиент->>Сервер: GET /api/datasets/1
    Сервер->>БД: Запрос данных
    БД-->>Сервер: Данные точек
    Сервер-->>Клиент: JSON с данными
```

## Установка и запуск

### Требования
- Python 3.7+
- PostgreSQL 12+
- pip

### Настройка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/AlexTalko/flask_datasets_app.git
cd flask_datasets_app
```

2. Настройте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/MacOS
venv\Scripts\activate    # Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env`:
```ini
DATABASE_URI=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
DEBUG=True
```

5. Запустите приложение:
```bash
python run.py
```

Приложение будет доступно по адресу: http://localhost:5000

## Тестирование API через Postman

В репозитории доступна готовая Postman-коллекция для тестирования API:  
`REST API basics- CRUD.postman_collection.json`

### Инструкция по импорту:

1. Скачайте коллекцию из репозитория
2. Откройте Postman
3. Нажмите "Import" и выберите файл коллекции
4. После импорта вы увидите 4 готовых запроса

### Доступные запросы:

1. **Get list datasets**  
   - Метод: GET  
   - URL: `http://127.0.0.1:5000/api/datasets`  
   - Проверяет статус 200 OK

2. **Get dataset id**  
   - Метод: GET  
   - URL: `http://127.0.0.1:5000/api/datasets/{id}`  
   - Замените {id} на реальный ID набора

3. **Add dataset**  
   - Метод: POST  
   - URL: `http://127.0.0.1:5000/api/datasets`  
   - Body: form-data с полями:
     - `file` (тип file) - Excel-файл с данными
     - `name` (опционально) - имя набора

4. **Delete dataset id**  
   - Метод: DELETE  
   - URL: `http://127.0.0.1:5000/api/datasets/{id}`  
   - Удаляет указанный набор

### Пример тестирования:

```bash
1. Запустите приложение: python run.py
2. В Postman выполните "Add dataset" для загрузки тестовых данных
3. Проверьте список через "Get list datasets"
4. Получите детали через "Get dataset id"
5. Протестируйте удаление через "Delete dataset id"
```