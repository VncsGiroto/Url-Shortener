
class HttpResponse:
    @staticmethod
    def success(data, message, status_code=200):
        response = {
            "status": "success",
            "message": message,
            "data": data
        }
        return response, status_code

    @staticmethod
    def error(message, status_code=400):
        response = {
            "status": "error",
            "message": message,
            "data": None
        }
        return response, status_code
