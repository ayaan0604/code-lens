# service.py

from auth import authenticate
from auth import UserService

def foo():
    authenticate()

def bar():
    service = UserService()
    service.login()