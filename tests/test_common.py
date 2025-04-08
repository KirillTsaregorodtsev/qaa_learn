import allure
import pytest
from pydantic import ValidationError

from api.endpoints import ReqresIn
from models.response import UsersList, CreatedUser, UpdatedUser


@pytest.fixture
def reqresin():
    return ReqresIn(base_url="https://reqres.in", api_key="")

@allure.feature("Users API")
@allure.story("Get users list")
@allure.tag("api", "positive")
@allure.severity(allure.severity_level.NORMAL)
@pytest.mark.positive
@pytest.mark.parametrize("page", [1, 2, 3])  # Проверим 3 страницы
def test_get_users(reqresin, page):
    with allure.step(f"Send GET request to /api/users?page={page}"):
        response = reqresin.users.get_users(page=page)
        assert response[0] == 200, f"Expected 200, got {response[0]}"

    with allure.step("Validate structure response by Pydantic"):
        validated_data = UsersList(**response[1])
        allure.attach(str(response[1]), name="JSON Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Check response data"):
        assert validated_data.page == page, f"Expected page {page}, got {validated_data.page}"
        assert validated_data.per_page > 0, "per_page should be > 0"
        assert validated_data.total >= validated_data.per_page, "total should be >= per_page"

    with allure.step("Check user data"):
        for user in validated_data.data:
            assert user.id > 0, "ID Should be a positive number"
            assert user.first_name.strip() != "", "Name should not be empty"
            assert user.last_name.strip() != "", "Last name should not be empty"
            assert user.avatar.startswith("https://"), f"Wrong avatar URL: {user.avatar}"

@allure.feature("Users API")
@allure.story("Creating User")
@allure.tag("api", "positive")
@pytest.mark.positive
def test_add_user(reqresin):
    body = {
        "name": "morpheus",
        "job": "leader"
    }

    with allure.step("Send POST request to create new user"):
        response = reqresin.users.add_user(body=body)
        allure.attach(str(response[1]), name="Response JSON", attachment_type=allure.attachment_type.JSON)

    with allure.step("Check the status code"):
        assert response[0] == 201, f"Expected 201, got {response[0]}"

    with allure.step("Validation structure response by Pydantic"):
        try:
            validated_data = CreatedUser(**response[1])
        except ValidationError as e:
            allure.attach(str(e), name="Pydantic Validation Error", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Pydantic validation failed: {e}")

        assert validated_data.id > 0, "ID should be a positive number"

@allure.feature("Users API")
@allure.story("Upodaqte user")
@allure.tag("api", "positive")
@pytest.mark.positive
def test_edit_user(reqresin):
    body = {
        "name": "morpheus",
        "job": "zion resident"
    }

    with allure.step("Send PUT request to update user"):
        response = reqresin.users.edit_user(user_id=2, body=body)
        allure.attach(str(response[1]), name="Response JSON", attachment_type=allure.attachment_type.JSON)

    with allure.step("Check the status code"):
        assert response[0] == 200, f"Expected 200, got {response[0]}"

    with allure.step("Validation structure response by Pydantic"):
        try:
            validated_data = UpdatedUser(**response[1])
        except ValidationError as e:
            allure.attach(str(e), name="Pydantic Validation Error", attachment_type=allure.attachment_type.TEXT)
            pytest.fail(f"Pydantic validation failed: {e}")

        assert validated_data.name == body["name"], f"Expected name {body['name']}, got {validated_data.name}"
        assert validated_data.job == body["job"], f"Expected job {body['job']}, got {validated_data.job}"

@allure.feature("Users API")
@allure.story("Delete user")
@allure.tag("api", "positive")
@pytest.mark.positive
def test_delete_user(reqresin):
    with allure.step("Send DELETE request"):
        response = reqresin.users.delete_user(user_id=2)

    with allure.step("Check the status code"):
        assert response[0] == 204, f"Expected 204, got {response[0]}"

@allure.feature("Users API")
@allure.story("Get not existing user")
@allure.tag("api", "negative")
@pytest.mark.negative
def test_get_nonexistent_user(reqresin):
    user_id = 9999

    with allure.step(f"Send GET request to /api/users/{user_id}"):
        response = reqresin.users.get_user(user_id=user_id)
        allure.attach(str(response[1]), name="Response", attachment_type=allure.attachment_type.TEXT)

    with allure.step("Check, if API response status code 404"):
        assert response[0] == 404, f"Expected 404, got {response[0]}"

@allure.feature("Users API")
@allure.story("Creating user with empty body")
@allure.tag("api", "negative")
@pytest.mark.negative
def test_create_user_with_empty_body(reqresin):
    body = {}

    with allure.step("Send POST request to create new user with empty body"):
        response = reqresin.users.add_user(body=body)
        allure.attach(str(response[1]), name="Response", attachment_type=allure.attachment_type.JSON)

    with allure.step("Check if API response status code 400"):
        assert response[0] == 400, "Should be Bad request (400)"

@allure.feature("Users API")
@allure.story("Update user with invalid payload")
@allure.tag("api", "negative")
@pytest.mark.negative
def test_update_user_invalid_payload(reqresin):
    body = {
        "name": 123,
        "job": ["not", "a", "string"]
    }

    with allure.step("Send PUT request with invalid payload"):
        response = reqresin.users.edit_user(user_id=2, body=body)
        allure.attach(str(response[1]), name="Response JSON", attachment_type=allure.attachment_type.JSON)

    with allure.step("Check status code"):
        assert response[0] == 400, f"The current status code is {response[0]} but should be 400"
