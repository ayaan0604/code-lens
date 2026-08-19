import os
from auth import authenticate

class UserService:

    def login(self, username):
        token = authenticate(username)
        print(token)
        return token


def logout(user):
    print(user)

logout("hello")