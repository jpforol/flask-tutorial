import os
import tempfile

import pytest
from flaskr import create_app
from flaskr.db import get_db, init_db

with open(os.path.join(os.path.dirname(__file__), 'data.sql'), 'rb') as f:
    _data_sql = f.read().decode('utf8')


@pytest.fixture
def app():
    """ 
    tempfile.mkstemp() cria e abre um arquivo temporário, retornando o descritor do arquivo e o caminho para ele.
    O caminho DATABASE é substituído, portanto aponta para esse caminho temporário em vez da pasta da instância.
    Após definir o caminho, as tabelas do banco de dados são criadas e os dados de teste são inseridos. 
    Depois que o teste terminar, o arquivo temporário é fechado e removido. 
    """
    db_fd, db_path = tempfile.mkstemp()

    app = create_app(
        {
            'TESTING': True,
            'DATABASE': db_path,
        }
    )

    with app.app_context():
        init_db()
        get_db().executescript(_data_sql)

    yield app

    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, username='test', password='test'):
        return self._client.post(
            '/auth/login',
            data={'username': username, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)