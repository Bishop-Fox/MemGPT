<<<<<<< HEAD
import os
import tempfile
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends, Query, UploadFile

from memgpt.schemas.document import Document
from memgpt.schemas.job import Job
from memgpt.schemas.passage import Passage
from memgpt.schemas.source import Source, SourceCreate, SourceUpdate
from memgpt.server.rest_api.utils import get_memgpt_server
from memgpt.server.server import SyncServer

# These can be forward refs, but because Fastapi needs them at runtime the must be imported normally

=======
import tempfile
from typing import List

# These can be forward refs, but because Fastapi needs them at runtime the must be imported normally
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    UploadFile,
)
from sqlalchemy.exc import MultipleResultsFound, NoResultFound

from memgpt.schemas.job import Job
from memgpt.schemas.source import Source, SourceCreate
from memgpt.server.rest_api.utils import get_memgpt_server
from memgpt.server.schemas.sources import (
    GetSourceDocumentsResponse,
    GetSourcePassagesResponse,
)
from memgpt.server.server import SyncServer
>>>>>>> refs/heads/integration-block-fixes

router = APIRouter(prefix="/sources", tags=["sources"])


<<<<<<< HEAD
@router.get("/{source_id}", response_model=Source, operation_id="get_source")
def get_source(
=======
@router.get("/{source_id}", response_model=Source)
async def get_source(
>>>>>>> refs/heads/integration-block-fixes
    source_id: str,
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Get all sources
    """
<<<<<<< HEAD
    actor = server.get_current_user()

    return server.get_source(source_id=source_id, user_id=actor.id)


@router.get("/name/{source_name}", response_model=str, operation_id="get_source_id_by_name")
def get_source_id_by_name(
    source_name: str,
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Get a source by name
    """
    actor = server.get_current_user()

    source_id = server.get_source_id(source_name=source_name, user_id=actor.id)
    return source_id


@router.get("/", response_model=List[Source], operation_id="list_sources")
def list_sources(
=======

    return server.get_source(source_id=source_id, user_id=server.get_current_user().id)


@router.get("/", response_model=List[Source])
async def list_sources(
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    List all data sources created by a user.
    """
    actor = server.get_current_user()

    return server.list_all_sources(user_id=actor.id)


<<<<<<< HEAD
@router.post("/", response_model=Source, operation_id="create_source")
def create_source(
=======
@router.post("/", response_model=Source)
async def create_source(
>>>>>>> refs/heads/integration-block-fixes
    source: SourceCreate,
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Create a new data source.
    """
    actor = server.get_current_user()

    return server.create_source(request=source, user_id=actor.id)


<<<<<<< HEAD
@router.patch("/{source_id}", response_model=Source, operation_id="update_source")
def update_source(
    source_id: str,
    source: SourceUpdate,
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Update the name or documentation of an existing data source.
    """
    actor = server.get_current_user()
    assert source.id == source_id, "Source ID in path must match ID in request body"

    return server.update_source(request=source, user_id=actor.id)


@router.delete("/{source_id}", response_model=None, operation_id="delete_source")
def delete_source(
    source_id: str,
=======
@router.delete("/{source_id}")
async def delete_source(
    source_id: "str",
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Delete a data source.
    """
    actor = server.get_current_user()

    server.delete_source(source_id=source_id, user_id=actor.id)


<<<<<<< HEAD
@router.post("/{source_id}/attach", response_model=Source, operation_id="attach_agent_to_source")
def attach_source_to_agent(
    source_id: str,
    agent_id: str = Query(..., description="The unique identifier of the agent to attach the source to."),
=======
@router.post("/{source_id}/attach")
async def attach_source_to_agent(
    source_id: "str",
    agent_id: "str" = Query(..., description="The unique identifier of the agent to attach the source to."),
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Attach a data source to an existing agent.
    """
    actor = server.get_current_user()

    source = server.ms.get_source(source_id=source_id, user_id=actor.id)
<<<<<<< HEAD
    assert source is not None, f"Source with id={source_id} not found."
    source = server.attach_source_to_agent(source_id=source.id, agent_id=agent_id, user_id=actor.id)
    return source


@router.post("/{source_id}/detach", response_model=None, operation_id="detach_agent_from_source")
def detach_source_from_agent(
    source_id: str,
    agent_id: str = Query(..., description="The unique identifier of the agent to detach the source from."),
=======
    source = server.attach_source_to_agent(source_name=source.name, agent_id=agent_id, user_id=actor.id)
    return Source(
        name=source.name,
        description=None,  # TODO: actually store descriptions
        user_id=source.user_id,
        id=source.id,
        embedding_config=server.server_embedding_config,
        created_at=source.created_at,
    )


@router.post("/{source_id}/detach")
async def detach_source_from_agent(
    source_id: "UUID",
    agent_id: "UUID" = Query(..., description="The unique identifier of the agent to detach the source from."),
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
) -> None:
    """
    Detach a data source from an existing agent.
    """
    actor = server.get_current_user()
<<<<<<< HEAD

    server.detach_source_from_agent(source_id=source_id, agent_id=agent_id, user_id=actor.id)


@router.post("/{source_id}/upload", response_model=Job, operation_id="upload_file_to_source")
def upload_file_to_source(
    file: UploadFile,
    source_id: str,
=======
    server.detach_source_from_agent(source_id=source_id, agent_id=agent_id, user_id=actor.id)


@router.get("/status/{job_id}", response_model=Job)
async def get_job_status(
    job_id: "UUID",
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Get the status of a job.
    """
    try:
        return server.ms.get_job(job_id=job_id)
    except (MultipleResultsFound, NoResultFound) as e:
        raise HTTPException(status_code=404, detail=f"Job with id={job_id} not found.") from e


@router.post("/{source_id}/upload", response_model=Job)
async def upload_file_to_source(
    file: UploadFile,
    source_id: "UUID",
>>>>>>> refs/heads/integration-block-fixes
    background_tasks: BackgroundTasks,
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    Upload a file to a data source.
    """
    actor = server.get_current_user()

    source = server.ms.get_source(source_id=source_id, user_id=actor.id)
<<<<<<< HEAD
    assert source is not None, f"Source with id={source_id} not found."
    bytes = file.file.read()

    # create job
    job = Job(
        user_id=actor.id,
        metadata_={"type": "embedding", "filename": file.filename, "source_id": source_id},
        completed_at=None,
    )
=======
    bytes = file.file.read()

    # create job
    job = Job(user_id=actor.id, metadata={"type": "embedding", "filename": file.filename, "source_id": source_id})
>>>>>>> refs/heads/integration-block-fixes
    job_id = job.id
    server.ms.create_job(job)

    # create background task
<<<<<<< HEAD
    background_tasks.add_task(load_file_to_source_async, server, source_id=source.id, job_id=job.id, file=file, bytes=bytes)

    # return job information
    job = server.ms.get_job(job_id=job_id)
    assert job is not None, "Job not found"
    return job


@router.get("/{source_id}/passages", response_model=List[Passage], operation_id="list_source_passages")
def list_passages(
    source_id: str,
=======
    background_tasks.add_task(load_file_to_source_async, server, actor.id, source, job_id, file, bytes)

    # return job information
    job = server.ms.get_job(job_id=job_id)
    return job


@router.get("/{source_id}/passages")
async def list_passages(
    source_id: "UUID",
>>>>>>> refs/heads/integration-block-fixes
    server: SyncServer = Depends(get_memgpt_server),
):
    """
    List all passages associated with a data source.
    """
    actor = server.get_current_user()
    passages = server.list_data_source_passages(user_id=actor.id, source_id=source_id)
<<<<<<< HEAD
    return passages


@router.get("/{source_id}/documents", response_model=List[Document], operation_id="list_source_documents")
def list_documents(
    source_id: str,
=======
    return GetSourcePassagesResponse(passages=passages)


@router.get("/{source_id}/documents")
async def list_documents(
    source_id: "UUID",
>>>>>>> refs/heads/integration-block-fixes
    server: "SyncServer" = Depends(get_memgpt_server),
):
    """
    List all documents associated with a data source.
    """
    actor = server.get_current_user()
<<<<<<< HEAD

    documents = server.list_data_source_documents(user_id=actor.id, source_id=source_id)
    return documents
=======
    documents = server.list_data_source_documents(user_id=actor.id, source_id=source_id)
    return GetSourceDocumentsResponse(documents=documents)
>>>>>>> refs/heads/integration-block-fixes


def load_file_to_source_async(server: SyncServer, source_id: str, job_id: str, file: UploadFile, bytes: bytes):
    # write the file to a temporary directory (deleted after the context manager exits)
    with tempfile.TemporaryDirectory() as tmpdirname:
<<<<<<< HEAD
        file_path = os.path.join(str(tmpdirname), str(file.filename))
=======
        file_path = os.path.join(tmpdirname, file.filename)
>>>>>>> refs/heads/integration-block-fixes
        with open(file_path, "wb") as buffer:
            buffer.write(bytes)

        server.load_file_to_source(source_id, file_path, job_id)
