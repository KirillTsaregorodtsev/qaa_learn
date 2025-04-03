import typing as t
from requests import Session, Response
from requests.exceptions import HTTPError

class APIClient:
    def __init__(self, base_url: str, api_key: str, session: t.Optional[Session] = None) -> None:
        self.base_url = base_url
        self.api_key = api_key
        self.session = session or self._create_default_session()

    def _create_default_session(self) -> Session:
        session = Session()
        session.headers.update(self.get_headers())
        return session

    def get_headers(self) -> dict:
        return {
            "Authorization": f"APIKey {self.api_key}",
            "Content-Type": "application/json"
        }

    def handle_response(self, response: Response) -> t.Any:
        response.raise_for_status()
        try:
            return response.status_code, response.json()
        except ValueError:
            return response.text

    def request(self, method: str, path: str, **kwargs) -> t.Any:
        url = f"{self.base_url}{path}"
        try:
            headers = self.get_headers()
            response = self.session.request(method, url, headers=headers, **kwargs)
            return self.handle_response(response)
        except HTTPError as e:
            raise e