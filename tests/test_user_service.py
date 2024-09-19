import pytest

from app.schemas.user_schema import CreateUser
from app.services.user_service import UserService


# @pytest.mark.asyncio
# async def test_create_user_service():
#     user_data = CreateUser(
#         first_name="Test",
#         last_name="User",
#         email="testuser@example.com",
#         password="testpass",
#         is_admin=False
#     )
#     user = await UserService.create_user_service(user_data)
#     assert user.email == "testuser@example.com"
#
#
# @pytest.mark.asyncio
# async def test_authenticate_user():
#     user = await UserService.authenticate_user("testuser@example.com", "testpass")
#     assert user is not None
#     assert user.email == "testuser@example.com"
#
#
# @pytest.mark.asyncio
# async def test_get_user_by_id():
#     user = await UserService.get_user_by_email("testuser@example.com")
#     retrieved_user = await UserService.get_user_by_id(user.id)
#     assert retrieved_user.email == "testuser@example.com"
