from requests import Session

from api.api_client import APIClient
import typing as t

class Users:
    def __init__(self, api_client: APIClient) -> None:
        self.api_client = api_client

    def get_users(self):
        return self.api_client.request(
            method="GET",
            path="/api/users"
        )
    def add_user(self, body):
        return self.api_client.request(
            method="POST",
            path="/api/users",
            json=body
        )

    def edit_user(self, user_id, body):
        return self.api_client.request(
            method="PATCH",
            path=f"/api/users/{user_id}",
            json=body
        )

    def delete_user(self, user_id):
        return self.api_client.request(
            method="DELETE",
            path=f"/api/users/{user_id}"
        )

class ReqresIn:
    def __init__(self, base_url: str, api_key: str, session: t.Optional[Session] = None) -> None:
        self.api_client = APIClient(base_url=base_url, api_key=api_key, session=session)

    @property
    def users(self) -> Users:
        return Users(self.api_client)