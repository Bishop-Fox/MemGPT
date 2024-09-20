<<<<<<< HEAD
from typing import TYPE_CHECKING, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from memgpt.schemas.api_key import APIKey, APIKeyCreate
from memgpt.schemas.user import User, UserCreate
from memgpt.server.rest_api.utils import get_memgpt_server

# from memgpt.server.schemas.users import (
#     CreateAPIKeyRequest,
#     CreateAPIKeyResponse,
#     CreateUserRequest,
#     CreateUserResponse,
#     DeleteAPIKeyResponse,
#     DeleteUserResponse,
#     GetAllUsersResponse,
#     GetAPIKeysResponse,
# )

if TYPE_CHECKING:
=======
from typing import TYPE_CHECKING, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from memgpt.server.rest_api.utils import get_memgpt_server
from memgpt.server.schemas.users import (
    CreateAPIKeyRequest,
    CreateAPIKeyResponse,
    CreateUserRequest,
    CreateUserResponse,
    DeleteAPIKeyResponse,
    DeleteUserResponse,
    GetAllUsersResponse,
    GetAPIKeysResponse,
)

if TYPE_CHECKING:
    from uuid import UUID

>>>>>>> refs/heads/integration-block-fixes
    from memgpt.schemas.user import User
    from memgpt.server.server import SyncServer


router = APIRouter(prefix="/users", tags=["users", "admin"])


<<<<<<< HEAD
@router.get("/", tags=["admin"], response_model=List[User], operation_id="list_users")
def get_all_users(
    cursor: Optional[str] = Query(None),
    limit: Optional[int] = Query(50),
    server: "SyncServer" = Depends(get_memgpt_server),
=======
@router.get("/users", tags=["admin"], response_model=GetAllUsersResponse)
def get_all_users(
    cursor: Optional["UUID"] = Query(None),
    limit: Optional[int] = Query(50),
    server: SyncServer = Depends(get_memgpt_server),
>>>>>>> refs/heads/integration-block-fixes
):
    """
    Get a list of all users in the database
    """
    try:
<<<<<<< HEAD
        next_cursor, users = server.ms.get_all_users(cursor=cursor, limit=limit)
        # processed_users = [{"user_id": user.id} for user in users]
=======
        next_cursor, users = server.ms.get_all_users(cursor, limit)
        processed_users = [{"user_id": user.id} for user in users]
>>>>>>> refs/heads/integration-block-fixes
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
<<<<<<< HEAD
    return users


@router.post("/", tags=["admin"], response_model=User, operation_id="create_user")
def create_user(
    request: UserCreate = Body(...),
    server: "SyncServer" = Depends(get_memgpt_server),
=======
    return GetAllUsersResponse(cursor=next_cursor, user_list=processed_users)


@router.post("/users", tags=["admin"], response_model=CreateUserResponse)
def create_user(
    request: Optional[CreateUserRequest] = Body(None),
    server: SyncServer = Depends(get_memgpt_server),
>>>>>>> refs/heads/integration-block-fixes
):
    """
    Create a new user in the database
    """
<<<<<<< HEAD

    user = server.create_user(request)
    return user


@router.delete("/", tags=["admin"], response_model=User, operation_id="delete_user")
def delete_user(
    user_id: str = Query(..., description="The user_id key to be deleted."),
    server: "SyncServer" = Depends(get_memgpt_server),
=======
    if request is None:
        request = CreateUserRequest()

    new_user = User(
        id=None if not request.user_id else request.user_id,
        # TODO can add more fields (name? metadata?)
    )

    try:
        server.ms.create_user(new_user)

        # make sure we can retrieve the user from the DB too
        new_user_ret = server.ms.get_user(new_user.id)
        if new_user_ret is None:
            raise HTTPException(status_code=500, detail=f"Failed to verify user creation")

        # create an API key for the user
        token = server.ms.create_api_key(user_id=new_user.id, name=request.api_key_name)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
    return CreateUserResponse(user_id=new_user_ret.id, api_key=token.token)


@router.delete("/users", tags=["admin"], response_model=DeleteUserResponse)
def delete_user(
    user_id: "UUID" = Query(..., description="The user_id key to be deleted."),
    server: SyncServer = Depends(get_memgpt_server),
>>>>>>> refs/heads/integration-block-fixes
):
    # TODO make a soft deletion, instead of a hard deletion
    try:
        user = server.ms.get_user(user_id=user_id)
        if user is None:
            raise HTTPException(status_code=404, detail=f"User does not exist")
        server.ms.delete_user(user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}")
<<<<<<< HEAD
    return user


@router.post("/keys", response_model=APIKey, operation_id="create_api_key")
def create_new_api_key(
    create_key: APIKeyCreate = Body(...),
=======
    return DeleteUserResponse(message="User successfully deleted.", user_id_deleted=user_id)


@router.post("/keys", response_model=CreateAPIKeyResponse)
def create_new_api_key(
    create_key: CreateAPIKeyRequest = Body(...),
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Create a new API key for a user
    """
<<<<<<< HEAD
    api_key = server.create_api_key(create_key)
    return api_key


@router.get("/keys", response_model=List[APIKey], operation_id="list_api_keys")
def get_api_keys(
    user_id: str = Query(..., description="The unique identifier of the user."),
=======
    token = server.ms.create_api_key(user_id=create_key.user_id, name=create_key.name)
    return CreateAPIKeyResponse(api_key=token.token)


@router.get("/keys", response_model=GetAPIKeysResponse)
def get_api_keys(
    user_id: "UUID" = Query(..., description="The unique identifier of the user."),
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Get a list of all API keys for a user
    """
    if server.ms.get_user(user_id=user_id) is None:
        raise HTTPException(status_code=404, detail=f"User does not exist")
<<<<<<< HEAD
    api_keys = server.ms.get_all_api_keys_for_user(user_id=user_id)
    return api_keys


@router.delete("/keys", response_model=APIKey, operation_id="delete_api_key")
=======
    tokens = server.ms.get_all_api_keys_for_user(user_id=user_id)
    processed_tokens = [t.token for t in tokens]
    return GetAPIKeysResponse(api_key_list=processed_tokens)


@router.delete("/keys", response_model=DeleteAPIKeyResponse)
>>>>>>> refs/heads/integration-block-fixes
def delete_api_key(
    api_key: str = Query(..., description="The API key to be deleted."),
    server: "SyncServer" = Depends(get_memgpt_server),
):
<<<<<<< HEAD
    return server.delete_api_key(api_key)
=======
    server.get_current_user()
    token = server.ms.get_api_key(api_key=api_key)
    if token is None:
        raise HTTPException(status_code=404, detail=f"API key does not exist")
    server.ms.delete_api_key(api_key=api_key)
    return DeleteAPIKeyResponse(message="API key successfully deleted.", api_key_deleted=api_key)
>>>>>>> refs/heads/integration-block-fixes
