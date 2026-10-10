from flask import Flask, jsonify, request
from config import Config
from database import db, migrate
from routers.tasks import task_bp
from routers.user import user_bp
from routers.auth import auth_bp

app = Flask(__name__)
app.json.ensure_ascii = False
app.config.from_object(Config)
db.init_app(app)
migrate.init_app(app, db)

app.register_blueprint(task_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)



@app.route('/')
def hello():
    return jsonify({'message': 'Hello, Flask!'})

if __name__ == '__main__':
    app.run(debug=True)
