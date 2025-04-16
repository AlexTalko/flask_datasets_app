from app import create_app

app = create_app()

# Точка входа для запуска приложения
if __name__ == '__main__':
    app.run(debug=True)
