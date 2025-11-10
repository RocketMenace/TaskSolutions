import json
import urllib.request
from urllib.error import HTTPError
from wsgiref.simple_server import make_server
from wsgiref.types import StartResponse, WSGIApplication


def wsgi_app(environ: dict, start_response: StartResponse) -> list[bytes]:
    path = environ.get("PATH_INFO", "").strip("/")
    if not path:
        status = "400 Bad Request"
        headers = [("Content-Type", "application/json")]
        start_response(status, headers)
        return [json.dumps({"error": "Currency code is required"}).encode()]

    currency = path.upper()

    api_url = f"https://api.exchangerate-api.com/v4/latest/{currency}"
    try:
        with urllib.request.urlopen(api_url) as response:
            if response.status == 200:
                data = json.loads(response.read().decode())
                status = "200 OK"
                headers = [("Content-Type", "application/json")]
                start_response(status, headers)
                return [json.dumps(data).encode()]
            else:
                error_data = {"error": f"API returned status {response.status}"}
                status = f"{response.status} Error"
                headers = [("Content-Type", "application/json")]
                start_response(status, headers)
                return [json.dumps(error_data).encode()]
    except HTTPError as e:
        error_data = {"error": f"HTTP error: {e.code} - {e.reason}"}
        status = f"{e.code} Error"
        headers = [("Content-Type", "application/json")]
        start_response(status, headers)
        return [json.dumps(error_data).encode()]
    except Exception as e:
        error_data = {"error": str(e)}
        status = "500 Internal Server Error"
        headers = [("Content-Type", "application/json")]
        start_response(status, headers)
        return [json.dumps(error_data).encode()]


def run_server(app: WSGIApplication, host: str = "localhost", port: int = 8000) -> None:
    with make_server(host=host, port=port, app=app) as server:
        print(f"Server running on http://{host}:{port}")
        server.serve_forever()


if __name__ == "__main__":
    run_server(wsgi_app)
