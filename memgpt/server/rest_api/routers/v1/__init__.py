from memgpt.server.rest_api.routers.v1.agents import router as agents_router
from memgpt.server.rest_api.routers.v1.blocks import router as blocks_router
<<<<<<< HEAD
from memgpt.server.rest_api.routers.v1.jobs import router as jobs_router
from memgpt.server.rest_api.routers.v1.llms import router as llm_router
=======
from memgpt.server.rest_api.routers.v1.humans import router as humans_router
from memgpt.server.rest_api.routers.v1.large_language_models import router as llm_router
from memgpt.server.rest_api.routers.v1.personas import router as personas_router
>>>>>>> refs/heads/integration-block-fixes
from memgpt.server.rest_api.routers.v1.sources import router as sources_router
from memgpt.server.rest_api.routers.v1.tools import router as tools_router

ROUTERS = [
    tools_router,
    sources_router,
    agents_router,
    llm_router,
<<<<<<< HEAD
    blocks_router,
    jobs_router,
=======
    personas_router,
    humans_router,
    blocks_router,
>>>>>>> refs/heads/integration-block-fixes
]
