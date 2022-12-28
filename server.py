from libreproperty.app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=8888, use_reloader=True)

