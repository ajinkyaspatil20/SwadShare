from flask import session
from models.dbModel import DbModel
from passlib.hash import sha256_crypt


class AuthorModel(DbModel):
    TableName = 'authors'

    def __init__(self, mongo):
        super().__init__(mongo, self.TableName)

    def get_by_username(self, username: str):
        username = username.lower()
        return self.get_one_by_attr('username', username)

    def register(self, data: dict):
        self.db.insert_one(data)

    def authenticate(self, data: dict):
        user = self.get_by_username(data['username'])
        if user and 'password' in user:
            try:
                if sha256_crypt.verify(data['password'], user['password']):
                    return user
            except:
                pass
        return False

    @staticmethod
    def is_logged():
        return 'user' in session and type(session['user']) is dict

    def logged_as(self):
        return session['user'] if self.is_logged() else False
