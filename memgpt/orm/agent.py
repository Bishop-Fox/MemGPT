from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from memgpt.orm.sqlalchemy_base import SqlalchemyBase
from memgpt.orm.mixins import OrganizationMixin
from memgpt.data_types import LLMConfig, EmbeddingConfig

if TYPE_CHECKING:
    from memgpt.orm.organization import Organization
    from memgpt.orm.source import Source
    from memgpt.orm.user import User
    from memgpt.orm.tool import Tool

class Agent(SqlalchemyBase, OrganizationMixin):
    __tablename__ = 'agent'

    name:Mapped[Optional[str]] = mapped_column(String, nullable=True, doc="a human-readable identifier for an agent, non-unique.")
    persona: Mapped[str] = mapped_column(doc="the persona text for the agent, current state.")
    # todo: this doesn't allign with 1:M agents to users!
    human: Mapped[str] = mapped_column(doc="the human text for the agent and the current user, current state.")
    preset: Mapped[str] = mapped_column(doc="the preset text for the agent, current state.")

    llm_config: Mapped[LLMConfig] = mapped_column(JSON, doc="the LLM backend configuration object for this agent.")
    embedding_config: Mapped[EmbeddingConfig] = mapped_column(JSON, doc="the embedding configuration object for this agent.")

    # relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="agents")
    users: Mapped[List["User"]] = relationship("User",
                                               back_populates="agents",
                                               secondary="users_agents")
    sources: Mapped[List["Source"]] = relationship("Source", secondary="sources_agents")
    tools: Mapped[List["Tool"]] = relationship("Tool", secondary="tools_agents")