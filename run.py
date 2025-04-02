from app import create_app

app = create_app()

if __name__ == '__main__':
    # Debug=True should be False in production!
    app.run(debug=True) 