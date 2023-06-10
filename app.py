from flask_cors import CORS
from flask_restful import Api

from models import app
from resources import UserAuthentication, UserRefreshToken, UserRegistration, UserLogout, Todos, TodoResource

CORS(app)
api = Api(app)
api.add_resource(UserRegistration, '/register')
api.add_resource(UserAuthentication, '/login')
api.add_resource(UserRefreshToken, '/refresh')
api.add_resource(UserLogout, '/logout')
api.add_resource(Todos, '/todos')
api.add_resource(TodoResource, '/todo/<string:todo_id>')

if __name__ == '__main__':
  app.run(debug=True)