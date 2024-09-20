from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException

<<<<<<< HEAD
from memgpt.schemas.tool import Tool, ToolCreate, ToolUpdate
=======
from memgpt.schemas.tool import Tool, ToolCreate
>>>>>>> refs/heads/integration-block-fixes
from memgpt.server.rest_api.utils import get_memgpt_server
from memgpt.server.server import SyncServer

router = APIRouter(prefix="/tools", tags=["tools"])


<<<<<<< HEAD
@router.delete("/{tool_id}", operation_id="delete_tool")
=======
@router.delete("/{tool_id}")
>>>>>>> refs/heads/integration-block-fixes
def delete_tool(
    tool_id: str,
    server: SyncServer = Depends(get_memgpt_server),
):
    """
    Delete a tool by name
    """
<<<<<<< HEAD
    # actor = server.get_current_user()
    server.delete_tool(tool_id=tool_id)


@router.get("/{tool_id}", response_model=Tool, operation_id="get_tool")
=======
    actor = server.get_current_user()

    server.ms.delete_tool(id=tool_id, user_id=actor.id)


@router.get("/{tool_id}", tags=["tools"], response_model=Tool)
>>>>>>> refs/heads/integration-block-fixes
def get_tool(
    tool_id: str,
    server: SyncServer = Depends(get_memgpt_server),
):
    """
<<<<<<< HEAD
    Get a tool by ID
    """
    # actor = server.get_current_user()

    tool = server.get_tool(tool_id=tool_id)
    if tool is None:
        # return 404 error
        raise HTTPException(status_code=404, detail=f"Tool with id {tool_id} not found.")
    return tool


@router.get("/name/{tool_name}", response_model=str, operation_id="get_tool_id_by_name")
def get_tool_id(
    tool_name: str,
    server: SyncServer = Depends(get_memgpt_server),
):
    """
    Get a tool ID by name
    """
    actor = server.get_current_user()

    tool_id = server.get_tool_id(tool_name, user_id=actor.id)
    if tool_id is None:
        # return 404 error
        raise HTTPException(status_code=404, detail=f"Tool with name {tool_name} not found.")
    return tool_id


@router.get("/", response_model=List[Tool], operation_id="list_tools")
=======
    Get a tool by name
    """
    actor = server.get_current_user()
    # Clear the interface

    if tool := server.ms.get_tool(tool_id=tool_id, user_id=actor.id):
        return tool
    # return 404 error
    # TODO issue #13 in the big spreadsheet: Standardize errors and correct error codes
    raise HTTPException(status_code=404, detail=f"Tool with id {tool_id} not found.")


@router.get("/", tags=["tools"], response_model=List[Tool])
>>>>>>> refs/heads/integration-block-fixes
def list_all_tools(
    server: SyncServer = Depends(get_memgpt_server),
):
    """
    Get a list of all tools available to agents created by a user
    """
    actor = server.get_current_user()
<<<<<<< HEAD
    actor.id

    # TODO: add back when user-specific
    return server.list_tools(user_id=actor.id)
    # return server.ms.list_tools(user_id=None)


@router.post("/", response_model=Tool, operation_id="create_tool")
=======
    # Clear the interface

    return server.ms.list_tools(user_id=actor.id)


@router.post("/", tags=["tools"], response_model=Tool)
>>>>>>> refs/heads/integration-block-fixes
def create_tool(
    tool: ToolCreate = Body(...),
    update: bool = False,
    server: SyncServer = Depends(get_memgpt_server),
):
    """
    Create a new tool
    """
    actor = server.get_current_user()
<<<<<<< HEAD

    return server.create_tool(
        request=tool,
        # update=update,
        update=True,
        user_id=actor.id,
    )


@router.patch("/{tool_id}", response_model=Tool, operation_id="update_tool")
def update_tool(
    tool_id: str,
    request: ToolUpdate = Body(...),
    server: SyncServer = Depends(get_memgpt_server),
):
    """
    Update an existing tool
    """
    assert tool_id == request.id, "Tool ID in path must match tool ID in request body"
    server.get_current_user()
    return server.update_tool(request)
=======
    return server.create_tool(
        request=tool,
        update=update,
        user_id=actor.id,
    )
>>>>>>> refs/heads/integration-block-fixes
