from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional

<<<<<<< HEAD
import numpy as np
from sqlalchemy import (
    BINARY,
    Column,
    DateTime,
    Index,
    String,
    TypeDecorator,
    and_,
    asc,
    create_engine,
    desc,
    or_,
    select,
    text,
)
from sqlalchemy.orm import declarative_base, mapped_column, sessionmaker
from sqlalchemy.orm.session import close_all_sessions
=======
from sqlalchemy import and_, asc, desc, or_, select
>>>>>>> refs/heads/integration-block-fixes
from sqlalchemy.sql import func
from tqdm import tqdm

from memgpt.agent_store.storage import StorageConnector
from memgpt.config import MemGPTConfig
<<<<<<< HEAD
from memgpt.constants import MAX_EMBEDDING_DIM
from memgpt.metadata import EmbeddingConfigColumn, ToolCallColumn

# from memgpt.schemas.message import Message, Passage, Record, RecordType, ToolCall
from memgpt.schemas.message import Message
from memgpt.schemas.openai.chat_completions import ToolCall
=======
from memgpt.orm.document import Document as SQLDocument
from memgpt.orm.errors import NoResultFound
from memgpt.orm.message import Message as SQLMessage
from memgpt.orm.passage import Passage as SQLPassage
from memgpt.orm.utilities import get_db_session
from memgpt.schemas.enums import TableType
from memgpt.schemas.memgpt_base import MemGPTBase
>>>>>>> refs/heads/integration-block-fixes
from memgpt.schemas.passage import Passage

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

<<<<<<< HEAD
class CommonVector(TypeDecorator):
    """Common type for representing vectors in SQLite"""

    impl = BINARY
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(BINARY())

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        # Ensure value is a numpy array
        if isinstance(value, list):
            value = np.array(value, dtype=np.float32)
        # Serialize numpy array to bytes, then encode to base64 for universal compatibility
        return base64.b64encode(value.tobytes())

    def process_result_value(self, value, dialect):
        if not value:
            return value
        # Check database type and deserialize accordingly
        if dialect.name == "sqlite":
            # Decode from base64 and convert back to numpy array
            value = base64.b64decode(value)
        # For PostgreSQL, value is already in bytes
        return np.frombuffer(value, dtype=np.float32)


# Custom serialization / de-serialization for JSON columns


Base = declarative_base()


def get_db_model(
    config: MemGPTConfig,
    table_name: str,
    table_type: TableType,
    user_id: str,
    agent_id: Optional[str] = None,
    dialect="postgresql",
):
    # Define a helper function to create or get the model class
    def create_or_get_model(class_name, base_model, table_name):
        if class_name in globals():
            return globals()[class_name]
        Model = type(class_name, (base_model,), {"__tablename__": table_name, "__table_args__": {"extend_existing": True}})
        globals()[class_name] = Model
        return Model

    if table_type == TableType.ARCHIVAL_MEMORY or table_type == TableType.PASSAGES:
        # create schema for archival memory
        class PassageModel(Base):
            """Defines data model for storing Passages (consisting of text, embedding)"""

            __abstract__ = True  # this line is necessary

            # Assuming passage_id is the primary key
            id = Column(String, primary_key=True)
            user_id = Column(String, nullable=False)
            text = Column(String)
            doc_id = Column(String)
            agent_id = Column(String)
            source_id = Column(String)

            # vector storage
            if dialect == "sqlite":
                embedding = Column(CommonVector)
            else:
                from pgvector.sqlalchemy import Vector

                embedding = mapped_column(Vector(MAX_EMBEDDING_DIM))

            embedding_config = Column(EmbeddingConfigColumn)
            metadata_ = Column(MutableJson)

            # Add a datetime column, with default value as the current time
            created_at = Column(DateTime(timezone=True))

            Index("passage_idx_user", user_id, agent_id, doc_id),

            def __repr__(self):
                return f"<Passage(passage_id='{self.id}', text='{self.text}', embedding='{self.embedding})>"

            def to_record(self):
                return Passage(
                    text=self.text,
                    embedding=self.embedding,
                    embedding_config=self.embedding_config,
                    doc_id=self.doc_id,
                    user_id=self.user_id,
                    id=self.id,
                    source_id=self.source_id,
                    agent_id=self.agent_id,
                    metadata_=self.metadata_,
                    created_at=self.created_at,
                )

        """Create database model for table_name"""
        class_name = f"{table_name.capitalize()}Model" + dialect
        return create_or_get_model(class_name, PassageModel, table_name)

    elif table_type == TableType.RECALL_MEMORY:

        class MessageModel(Base):
            """Defines data model for storing Message objects"""

            __abstract__ = True  # this line is necessary

            # Assuming message_id is the primary key
            id = Column(String, primary_key=True)
            user_id = Column(String, nullable=False)
            agent_id = Column(String, nullable=False)

            # openai info
            role = Column(String, nullable=False)
            text = Column(String)  # optional: can be null if function call
            model = Column(String)  # optional: can be null if LLM backend doesn't require specifying
            name = Column(String)  # optional: multi-agent only

            # tool call request info
            # if role == "assistant", this MAY be specified
            # if role != "assistant", this must be null
            # TODO align with OpenAI spec of multiple tool calls
            # tool_calls = Column(ToolCallColumn)
            tool_calls = Column(ToolCallColumn)

            # tool call response info
            # if role == "tool", then this must be specified
            # if role != "tool", this must be null
            tool_call_id = Column(String)

            # Add a datetime column, with default value as the current time
            created_at = Column(DateTime(timezone=True))
            Index("message_idx_user", user_id, agent_id),

            def __repr__(self):
                return f"<Message(message_id='{self.id}', text='{self.text}')>"

            def to_record(self):
                # calls = (
                #    [ToolCall(id=tool_call["id"], function=ToolCallFunction(**tool_call["function"])) for tool_call in self.tool_calls]
                #    if self.tool_calls
                #    else None
                # )
                # if calls:
                #    assert isinstance(calls[0], ToolCall)
                if self.tool_calls and len(self.tool_calls) > 0:
                    assert isinstance(self.tool_calls[0], ToolCall), type(self.tool_calls[0])
                    for tool in self.tool_calls:
                        assert isinstance(tool, ToolCall), type(tool)
                return Message(
                    user_id=self.user_id,
                    agent_id=self.agent_id,
                    role=self.role,
                    name=self.name,
                    text=self.text,
                    model=self.model,
                    # tool_calls=[ToolCall(id=tool_call["id"], function=ToolCallFunction(**tool_call["function"])) for tool_call in self.tool_calls] if self.tool_calls else None,
                    tool_calls=self.tool_calls,
                    tool_call_id=self.tool_call_id,
                    created_at=self.created_at,
                    id=self.id,
                )

        """Create database model for table_name"""
        class_name = f"{table_name.capitalize()}Model" + dialect
        return create_or_get_model(class_name, MessageModel, table_name)

    else:
        raise ValueError(f"Table type {table_type} not implemented")
=======
    from memgpt.orm.sqlalchemy_base import SqlalchemyBase as SQLBase
>>>>>>> refs/heads/integration-block-fixes


class SQLStorageConnector(StorageConnector):
    """Storage via SQL Alchemy"""

    engine_type: str = "sql-generic"
    SQLModel: "SQLBase" = None
    db_session: "Session" = None

    def __init__(
        self, table_type: str, config: MemGPTConfig, user_id: str, agent_id: Optional[str] = None, db_session: Optional["Session"] = None
    ):
        super().__init__(table_type=table_type, config=config, user_id=user_id, agent_id=agent_id)

        match table_type:
            case TableType.ARCHIVAL_MEMORY:
                self.SQLModel = SQLPassage
            case TableType.RECALL_MEMORY:
                self.SQLModel = SQLMessage
            case TableType.DOCUMENTS:
                self.SQLModel = SQLDocument
            case TableType.PASSAGES:
                self.SQLModel = SQLPassage
            case _:
                raise ValueError(f"Table type {table_type} not implemented")

        self.db_session = db_session or get_db_session()

        # self.check_db_session()

    # def check_db_session(self):
    #    from sqlalchemy import text

    #    schema = self.db_session.execute(text("show search_path")).fetchone()[0]
    #    if "postgres" not in schema:
    #        raise ValueError(f"Schema: {schema}")

    def get_filters(self, filters: Optional[Dict] = {}):
        filter_conditions = {**self.filters, **(filters or {})}
        all_filters = [getattr(self.SQLModel, key) == value for key, value in filter_conditions.items() if hasattr(self.SQLModel, key)]
        return all_filters

    def get_all_paginated(self, filters: Optional[Dict] = {}, page_size: Optional[int] = 1000, offset=0):
        filters = self.get_filters(filters)
        while True:
            # Retrieve a chunk of records with the given page_size
            with self.db_session as session:
                db_record_chunk = session.query(self.SQLModel).filter(*filters).offset(offset).limit(page_size).all()

                # If the chunk is empty, we've retrieved all records
                if not db_record_chunk:
                    break

                # Yield a list of Record objects converted from the chunk
                yield [record.to_pydantic() for record in db_record_chunk]

                # Increment the offset to get the next chunk in the next iteration
                offset += page_size

    def get_all_cursor(
        self,
        filters: Optional[Dict] = {},
        after: str = None,
        before: str = None,
        limit: Optional[int] = 1000,
        order_by: str = "created_at",
        reverse: bool = False,
    ):
        """Get all that returns a cursor (record.id) and records"""
        filters = self.get_filters(filters)

        # generate query
        with self.db_session as session:
            query = select(self.SQLModel).filter(*filters).limit(limit)
            # query = query.order_by(asc(self.SQLModel.id))

            # records are sorted by the order_by field first, and then by the ID if two fields are the same
            if reverse:
                query = query.order_by(desc(getattr(self.SQLModel, order_by)), asc(self.SQLModel.id))
            else:
                query = query.order_by(asc(getattr(self.SQLModel, order_by)), asc(self.SQLModel.id))

            # cursor logic: filter records based on before/after ID
            if after:
                after_value = getattr(self.get(id=after), order_by)
                sort_exp = getattr(self.SQLModel, order_by) > after_value
                query = query.filter(
                    or_(sort_exp, and_(getattr(self.SQLModel, order_by) == after_value, self.SQLModel.id > after))  # tiebreaker case
                )
            if before:
                before_value = getattr(self.get(id=before), order_by)
                sort_exp = getattr(self.SQLModel, order_by) < before_value
                query = query.filter(or_(sort_exp, and_(getattr(self.SQLModel, order_by) == before_value, self.SQLModel.id < before)))

            # get records
            db_record_chunk = session.execute(query).scalars()

            if not db_record_chunk:
                return (None, [])
            records = [record.to_pydantic() for record in db_record_chunk]
            next_cursor = db_record_chunk[-1].id
            assert isinstance(next_cursor, str)

            # return (cursor, list[records])
            return (next_cursor, records)

    def get_all(self, filters: Optional[Dict] = {}, limit=None):
        filters = self.get_filters(filters)
        with self.db_session as session:
            query = select(self.SQLModel).filter(*filters)
            if limit:
                query = query.limit(limit)
            db_records = session.execute(query).scalars()

            return [record.to_pydantic() for record in db_records]

    def get(self, id: str):
        try:
            self.check_db_session()

            db_record = self.SQLModel.read(db_session=self.db_session, identifier=id)
        except NoResultFound:
            return None

        return db_record.to_pydantic()

    def size(self, filters: Optional[Dict] = {}) -> int:
        # return size of table
        filters = self.get_filters(filters)
        with self.db_session as session:
            return session.query(self.SQLModel).filter(*filters).count()

    def insert(self, record, exists_ok=True):
        self.insert_many([record], exists_ok=exists_ok)

    def insert_many(self, records, exists_ok=True, show_progress=False):
        match self.engine_type:
            case "sql-sqlite":
                from sqlalchemy.dialects.sqlite import insert
            case "sql-postgres":
                from sqlalchemy.dialects.postgresql import insert
            case _:
                from sqlalchemy.expression import insert

        if len(records) == 0:
            return
        if isinstance(records[0], Passage):
            with self.db_session as conn:
                db_records = [vars(record) for record in records]
                stmt = insert(self.SQLModel.__table__).values(db_records)
                if exists_ok:
                    upsert_stmt = stmt.on_conflict_do_update(
                        index_elements=["id"], set_={c.name: c for c in stmt.excluded}  # Replace with your primary key column
                    )
                    conn.execute(upsert_stmt)
                else:
                    conn.execute(stmt)
                conn.commit()
        else:
            with self.db_session as session:
                iterable = tqdm(records) if show_progress else records
                # Using SQLAlchemy Core is way faster than ORM Bulk Operations https://stackoverflow.com/a/34344200
                session.execute(self.SQLModel.__table__.insert(), [vars(record) for record in iterable])
                session.commit()

    def query(self, query: str, query_vec: List[float], top_k: int = 10, filters: Optional[Dict] = {}):
        filters = self.get_filters(filters)
        with self.db_session as session:
            query = select(self.SQLModel).filter(*filters).order_by(self.SQLModel.embedding.l2_distance(query_vec)).limit(top_k)
            results = session.execute(query).scalars()

            return [result.to_pydantic() for result in results]

    def update(self, record: MemGPTBase):
        """Updates a record in the database based on the provided Pydantic Record object."""
        self.SQLModel(**record.model_dump(exclude_none=True)).update(self.db_session)

    def list_data_sources(self):
        assert self.table_type == TableType.ARCHIVAL_MEMORY, f"list_data_sources only implemented for ARCHIVAL_MEMORY"
        with self.db_session as session:
            unique_data_sources = session.query(self.SQLModel.data_source).filter(*self.filters).distinct().all()
            return unique_data_sources

    def query_date(self, start_date, end_date, limit=None, offset=0):
        filters = self.get_filters({})
        with self.db_session as session:
            query = (
                select(self.SQLModel)
                .filter(*filters)
                .filter(self.SQLModel.created_at >= start_date)
                .filter(self.SQLModel.created_at <= end_date)
                .filter(self.SQLModel.role != "system")
                .filter(self.SQLModel.role != "tool")
                .offset(offset)
            )
            if limit:
                query = query.limit(limit)
            results = session.execute(query).scalars()
            return [result.to_pydantic() for result in results]

    def query_text(self, query, limit=None, offset=0):
        # todo: make fuzz https://stackoverflow.com/questions/42388956/create-a-full-text-search-index-with-sqlalchemy-on-postgresql/42390204#42390204
        filters = self.get_filters({})
        with self.db_session as session:
            query = (
                select(self.SQLModel)
                .filter(*filters)
                .filter(func.lower(self.SQLModel.text).contains(func.lower(query)))
                .filter(self.SQLModel.role != "system")
                .filter(self.SQLModel.role != "tool")
                .offset(offset)
            )
            if limit:
                query = query.limit(limit)
            results = session.execute(query).scalars()

            return [result.to_pydantic() for result in results]

    def delete(self, filters: Optional[Dict] = {}):
        # TODO: do we want to support soft deletes here?
        with self.db_session as session:
            session.query(self.SQLModel).filter(*self.get_filters(filters)).delete()
            session.commit()


class PostgresStorageConnector(SQLStorageConnector):
    """Storage via Postgres"""

    engine_type = "sql-postgres"

    # from pgvector.sqlalchemy import Vector
    # for c in self.SQLModel.__table__.columns:
    #     if c.name == "embedding":
    #         assert isinstance(c.type, Vector), f"Embedding column must be of type Vector, got {c.type}"

    def str_to_datetime(self, str_date: str) -> datetime:
        val = str_date.split("-")
        _datetime = datetime(int(val[0]), int(val[1]), int(val[2]))
        return _datetime

    def query_date(self, start_date, end_date, limit=None, offset=0):
        filters = self.get_filters({})
        _start_date = self.str_to_datetime(start_date) if isinstance(start_date, str) else start_date
        _end_date = self.str_to_datetime(end_date) if isinstance(end_date, str) else end_date
        with self.db_session as session:
            query = (
                select(self.SQLModel)
                .filter(*filters)
                .filter(self.SQLModel.created_at >= _start_date)
                .filter(self.SQLModel.created_at <= _end_date)
                .filter(self.SQLModel.role != "system")
                .filter(self.SQLModel.role != "tool")
                .offset(offset)
            )
            if limit:
                query = query.limit(limit)
            results = session.execute(query).scalars()

            return [result.to_pydantic() for result in results]


class SQLLiteStorageConnector(SQLStorageConnector):
    engine_type = "sql-sqlite"
