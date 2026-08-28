from flask import g
from psycopg2 import pool


class PostgreSQLPool:
    def __init__(self, app=None):
        self.pool = None
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.pool = pool.SimpleConnectionPool(
            minconn=app.config.get("DB_MIN_CONN", 1),
            maxconn=app.config.get("DB_MAX_CONN", 10),
            user= app.config["DB_USER"],
            password= app.config["DB_PASSWORD"],
            host= app.config["DB_HOST"],
            port=app.config["DB_PORT"],
            database=app.config["DB_NAME"]
        )

        app.teardown_appcontext(self.close_connection)

    @property
    def connection(self):
        if 'db_conn' not in g:
            g.db_conn = self.pool.getconn()
        return g.db_conn

    def close_connection(self, exception=None):
        conn = g.pop('db_conn', None)
        if conn is not None and self.pool is not None:
            self.pool.putconn(conn)