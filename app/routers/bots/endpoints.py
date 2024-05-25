import logging
import uuid

import fastapi
from fastapi import APIRouter, status

from app import deps, models, ports
from app.routers.bots import schemas

router = APIRouter(
    prefix="/bots", tags=["Bots"], dependencies=[fastapi.Depends(deps.get_token)]
)
logger = logging.getLogger(__name__)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
)
async def create_bot(
    data: schemas.BotCreate, bot_repo: deps.BotRepository
) -> schemas.BotOutput:
    """
    Endpoint to create a new bot
    """
    bot = models.Bot(
        name=data.name,
        welcome_message=data.welcome_message,
        avatar=data.avatar,
        data_source=data.data_source,
    )
    for ctx in data.contexts:
        bot.contexts.append(models.BotContext(role=ctx.role, content=ctx.content))

    await bot_repo.save(bot)

    bot = await bot_repo.get_by_id(bot.id)

    return schemas.BotOutput.model_validate(bot)


@router.get(
    "/",
)
async def list_bots(bot_repo: deps.BotRepository) -> list[schemas.BotOutput]:
    """
    Endpoint to fetch lists of bots
    """
    bots = await bot_repo.get_all()
    return [schemas.BotOutput.model_validate(bot) for bot in bots]


@router.get(
    "/{bot_id}/",
)
async def get_bot(
    bot_id: uuid.UUID,
    bot_repo: deps.BotRepository,
) -> schemas.BotOutput:
    """
    Endpoint to retrieve a bot
    """
    bot = await bot_repo.get_by_id(bot_id)

    return schemas.BotOutput.model_validate(bot)


@router.post(
    "/{bot_id}/chat/",
)
async def chat_bot(
    bot_id: uuid.UUID,
    data: schemas.ChatMessage,
    bot_repo: deps.BotRepository,
    agent_repo: deps.BotAgentRepository,
    vector_store: deps.VectorStore,
) -> schemas.ChatOutput:
    """
    Endpoint to fetch lists of bots
    """
    bot = await bot_repo.get_by_id(bot_id)
    chatbot_agent = agent_repo.get_agent(bot, vector_store=vector_store)

    content = await chatbot_agent.invoke(
        session_id=data.session_id, message=data.message
    )
    return schemas.ChatOutput(content=content)


@router.post("/{bot_id}/documents/", status_code=status.HTTP_201_CREATED)
async def create_bot_documents(
    bot_id: uuid.UUID,
    data: list[schemas.BotDocumentCreate],
    bot_repo: deps.BotRepository,
) -> list[schemas.BotDocumentOutput]:
    """
    Endpoint to fetch lists of bots
    """
    bot = await bot_repo.get_for_update(bot_id)
    doc_ids = []
    for doc in data:
        bot_doc = models.BotDocument(
            id=uuid.uuid4(),
            content=doc.content,
            filename=doc.filename,
            content_type=doc.content_type,
            doc_metadata=doc.metadata,
        )

        bot.documents.append(bot_doc)
        doc_ids.append(bot_doc.id)

    await bot_repo.save(bot)

    bot = await bot_repo.get_by_id(bot_id)
    return [
        schemas.BotDocumentOutput.model_validate(doc)
        for doc in bot.documents
        if doc.id in doc_ids
    ]


async def index_bot_documents_task(
    bot: models.Bot,
    vector_store: ports.VectorStore,
    bot_repo: ports.BotRepository,
) -> None:
    """
    Background task to index bot documents
    """
    logger.info("Indexing documents for %s", bot)

    await vector_store.index(bot)

    bot_for_update = await bot_repo.get_for_update(bot.id)
    bot_for_update.data_indexed = True

    await bot_repo.save(bot_for_update)


@router.post("/{bot_id}/index/", status_code=status.HTTP_202_ACCEPTED)
async def index_bot_documents(
    bot_id: uuid.UUID,
    bot_repo: deps.BotRepository,
    vector_store: deps.VectorStore,
    background_tasks: fastapi.BackgroundTasks,
) -> schemas.BotDocumentIndexOutput:
    """
    Endpoint to trigger indexing of bot documents
    """
    bot = await bot_repo.get_by_id(bot_id)
    background_tasks.add_task(index_bot_documents_task, bot, vector_store, bot_repo)

    return schemas.BotDocumentIndexOutput(id=bot_id, completed=False)
