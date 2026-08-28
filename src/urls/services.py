from repository import UrlRepository

class UrlService:
    def __init__(self, conn):
        self.conn = conn
        self.repository = UrlRepository(conn)