from extensions import db
from services import UrlService
from src.commom.http import HttpResponse

class UrlController:
    @staticmethod
    def create_url(data):
        try:
            conn = db.connection
            service = UrlService(conn)

        except ValueError as e:
            return HttpResponse.error(str(e), 400)
        except Exception as e:
            return HttpResponse.error("Internal server error", 500)