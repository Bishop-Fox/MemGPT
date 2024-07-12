import uuid
from functools import partial
from typing import List, Literal, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel, Field

from memgpt.constants import BASE_TOOLS
from memgpt.memory import ChatMemory
from memgpt.models.pydantic_models import (
    AgentStateModel,
    EmbeddingConfigModel,
    LLMConfigModel,
    PresetModel,
)
from memgpt.server.rest_api.auth_token import get_current_user
from memgpt.server.rest_api.interface import QueuingInterface
from memgpt.server.server import SyncServer
from memgpt.settings import settings

router = APIRouter()


class ListAgentsRequest(BaseModel):
    after: Optional[uuid.UUID] = Field(None, description="Unique agent ID to start the query range at.")
    before: Optional[uuid.UUID] = Field(None, description="Unique agent ID to end the query range at.")
    # TODO should these be 'optional'?
    limit: int = Field(20, description="How many results to include in the response.")
    order: Literal["asc", "desc"] = Field("desc", description="Sort order, asc for ascending order and desc for descending order.")


class CreateAgentRequest(BaseModel):
    # TODO: modify this (along with front end)
    config: dict = Field(..., description="The agent configuration object.")


class CreateAgentResponse(BaseModel):
    agent_state: AgentStateModel = Field(..., description="The state of the newly created agent.")
    preset: PresetModel = Field(..., description="The preset that the agent was created from.")


def setup_agents_index_router(server: SyncServer, interface: QueuingInterface, password: str):
    get_current_user_with_server = partial(partial(get_current_user, server), password)

    @router.get("/agents", tags=["agents"], response_model=List[AgentStateModel])
    def list_agents(
        request: ListAgentsRequest = Depends(),  # NOTE: using depends here, since all the pieces have defaults
        user_id: uuid.UUID = Depends(get_current_user_with_server),
    ):
        """
        List all agents associated with a given user.

        This endpoint retrieves a list of all agents and their configurations associated with the specified user ID.
        """
        interface.clear()
        return server.list_agents(
            user_id=user_id,
            after=request.after,
            before=request.before,
            limit=request.limit,
            order=request.order,
        )

    # TODO(swooders) - "stripify"
    @router.get("/agents/count", tags=["agents"], response_model=int)
    def count_agents(
        user_id: uuid.UUID = Depends(get_current_user_with_server),
    ):
        return server.ms.count_agents(user_id=user_id)

    @router.post("/agents", tags=["agents"], response_model=CreateAgentResponse)
    def create_agent(
        request: CreateAgentRequest = Body(...),
        user_id: uuid.UUID = Depends(get_current_user_with_server),
    ):
        """
        Create a new agent with the specified configuration.
        """
        interface.clear()

        # Parse request
        # TODO: don't just use JSON in the future
        human_name = request.config["human_name"] if "human_name" in request.config else None
        human = request.config["human"] if "human" in request.config else None
        persona_name = request.config["persona_name"] if "persona_name" in request.config else None
        persona = request.config["persona"] if "persona" in request.config else None
        request.config["preset"] if ("preset" in request.config and request.config["preset"]) else settings.default_preset
        tool_names = request.config["function_names"]
        metadata = request.config["metadata"] if "metadata" in request.config else {}
        metadata["human"] = human_name
        metadata["persona"] = persona_name

        # TODO: remove this -- should be added based on create agent fields
        if isinstance(tool_names, str):  # TODO: fix this on clinet side?
            tool_names = tool_names.split(",")
        if tool_names is None or tool_names == "":
            tool_names = []
        for name in BASE_TOOLS:  # TODO: remove this
            if name not in tool_names:
                tool_names.append(name)
        assert isinstance(tool_names, list), "Tool names must be a list of strings."

        # TODO: eventually remove this - should support general memory at the REST endpoint
        memory = ChatMemory(persona=persona, human=human)

        try:
            agent_state = server.create_agent(
                user_id=user_id,
                # **request.config
                # TODO turn into a pydantic model
                name=request.config["name"],
                memory=memory,
                # persona_name=persona_name,
                # human_name=human_name,
                # persona=persona,
                # human=human,
                # llm_config=LLMConfigModel(
                # model=request.config['model'],
                # )
                # tools
                tools=tool_names,
                metadata=metadata,
                # function_names=request.config["function_names"].split(",") if "function_names" in request.config else None,
            )
            llm_config = LLMConfigModel(**vars(agent_state.llm_config))
            embedding_config = EmbeddingConfigModel(**vars(agent_state.embedding_config))

            return CreateAgentResponse(
                agent_state=AgentStateModel(
                    id=agent_state.id,
                    name=agent_state.name,
                    user_id=agent_state.user_id,
                    llm_config=llm_config,
                    embedding_config=embedding_config,
                    state=agent_state.state,
                    created_at=int(agent_state.created_at.timestamp()),
                    tools=tool_names,
                    system=agent_state.system,
                    metadata=agent_state._metadata,
                ),
                preset=PresetModel(  # TODO: remove (placeholder to avoid breaking frontend)
                    name="dummy_preset",
                    id=agent_state.id,
                    user_id=agent_state.user_id,
                    description="",
                    created_at=agent_state.created_at,
                    system=agent_state.system,
                    persona="",
                    human="",
                    functions_schema=[],
                ),
            )
        except Exception as e:
            print(str(e))
            raise HTTPException(status_code=500, detail=str(e))

    return router
