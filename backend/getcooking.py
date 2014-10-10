from flask import Flask, jsonify
import settings

app = Flask(__name__)
app.config.from_object(settings)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/shopping_list')
def shopping_list():
    l = [
        {'name': 'Tomato', 'ean': 123},
        {'name': 'Cucumber', 'ean': 123}
    ]
    return jsonify(l)


if __name__ == '__main__':
    app.run()