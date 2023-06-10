from flask_restful import Resource, reqparse, url_for, request
from models import Todo
from werkzeug.security import generate_password_hash
from models import User
from datetime import datetime
from decorators import jwt_required

parser = reqparse.RequestParser()
parser.add_argument('username', type=str)
parser.add_argument('password', type=str)
parser.add_argument('token', type=str)
parser.add_argument('body', type=str)
parser.add_argument('status', type=str)

class UserRegistration(Resource):
  ''' /register '''

  def post(self):
    data = parser.parse_args()
    username = data['username']
    password = data['password']
    if not username or not password:
      return {"message" : "Some parameters are missing. You need 'username' and 'password'."}, 400
    user_exists = User.fetch(username)
    if user_exists:
      return {"message" : f"{username} is already registered."}, 400
    new_user = User.create_new(username, password)
    return {"message":"Success. User created." , "username" : new_user.username, "created at" : str(datetime.now()) }, 200


class UserAuthentication(Resource):
  ''' /login '''
  
  def post(self):
    data = parser.parse_args()
    username = data['username']
    password = data['password']
    if not username or not password:
      return {"message" : "Some parameters are missing. You need 'username' and 'password'."}
    user_exists = User.fetch(username)
    if user_exists:
      if user_exists.check_password(password):
        return {"message" : "Success.", "token" : f"{user_exists.get_session_token()}", "expires" : { "in" : 3600 , "units" : "seconds"} }
      else: 
        return {"message" : "Invalid credentials."}
    else:
      return {"message" : f"{username} could not be found." }  

class UserRefreshToken(Resource):
  ''' /refresh '''

  @jwt_required
  def post(self):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    return {"logged in as": f"{user.username}", "message" : "Success.", "token" : f"{user.get_session_token()}", "expires" : { "in" : 3600 , "units" : "seconds"}}


class UserLogout(Resource):
  ''' /logout '''
  @jwt_required
  def post(self):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    user.delete_token()
    return {"message" : "Success. You have now logged out. Your token is now invalidated."}
      

class Todos(Resource):
  ''' /todos '''

  @jwt_required
  def get(self):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    todos_array = [{"id" : td.id, "status": td.status , "body" : td.body, "created" : f"{td.created_at}", "owner" : td.user.username} for td in user.get_todos()]
    return {"logged in as": f"{user.username}", "todos" : todos_array , "total": len(todos_array)}, 200

  @jwt_required
  def delete(self):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    user.delete_all_todos()
    return {"logged in as": f"{user.username}", "message": "Success. All todos deleted."}, 200
    
  @jwt_required
  def post(self):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    data = parser.parse_args()
    body = data['body']
    new_todo = Todo.create_new(body=body, creator_id=user.id, status="pending")
    return {"logged in as": f"{user.username}", "message":"Success. Todo created.", "todo": { "id" : new_todo.id, "body": new_todo.body, "status":new_todo.status, "owner":new_todo.user.username , "created": f"{new_todo.created_at}" }}, 201


class TodoResource(Resource):
  ''' /todo/<todo_id> '''
  @jwt_required
  def get(self, todo_id):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    todo = user.get_todo(todo_id=todo_id)
    if not todo:
      return {"message": f"Could not find todo with an id of '{todo_id}'."}, 404
    todo_details = {"id" : todo.id, "status": todo.status , "body" : todo.body, "created" : f"{todo.created_at}", "owner" : todo.user.username}
    return {"logged in as": f"{user.username}", "message" : "Success." , "todo" : todo_details}, 200

  @jwt_required
  def delete(self, todo_id):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    todo = user.get_todo(todo_id=todo_id)
    if not todo:
      return {"message": f"Could not find todo with an id of '{todo_id}'."}, 404
    user.delete_todo(todo_id)
    return {"logged in as": f"{user.username}", "message": f"Success. Todo id {todo_id} deleted."}, 200

  @jwt_required
  def put(self, todo_id):
    token = User.get_request_token(request)
    user = User.verify_session_token(token)
    data = parser.parse_args()
    new_status = data['status']
    if not new_status:
      return {"message": "Missing updated status for todo."}, 400
    if not user:
      return {"message": "Invalid or expired token. You need to re-authenticate."}, 401
    todo = user.get_todo(todo_id=todo_id)
    if not todo:
      return {"message": f"Could not find todo with an id of '{todo_id}'."}, 404
    td = user.update_todo(todo_id=todo_id, new_status=new_status)
    return {"logged in as": f"{user.username}","message" : "Success.", "todo" : {"id" : td.id, "status": td.status , "body" : td.body, "created" : f"{td.created_at}", "owner" : td.user.username }}


