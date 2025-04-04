import pytest

from api.endpoints import ReqresIn
from models.response import UsersList, CreatedUser


@pytest.fixture
def reqresin():
    return ReqresIn(base_url="https://reqres.in", api_key="")


@pytest.mark.positive
@pytest.mark.parametrize("page", [1, 2, 3])  # Проверим 3 страницы
def test_get_users(reqresin, page):
    response = reqresin.users.get_users(page=page)
    assert response[0] == 200, f"Expected 200, got {response[0]}"

    validated_data = UsersList(**response[1])

    assert validated_data.page == page, f"Expected page {page}, got {validated_data.page}"
    assert validated_data.per_page > 0, "per_page should be > 0"
    assert validated_data.total >= validated_data.per_page, "total should be >= per_page"

    for user in validated_data.data:
        assert user.id > 0, "ID Should be a positive number"
        assert user.first_name.strip() != "", "Name should not be empty"
        assert user.last_name.strip() != "", "Last name should not be empty"
        assert user.avatar.startswith("https://"), f"Wrong avatar URL: {user.avatar}"

@pytest.mark.positive
def test_add_user(reqresin):
    body = {
        "name": "morpheus",
        "job": "leader"
    }
    response = reqresin.users.add_user(body=body)
    assert response[0] == 201, f"Expected 201, got {response[0]}"

    validated_data = CreatedUser(**response[1])