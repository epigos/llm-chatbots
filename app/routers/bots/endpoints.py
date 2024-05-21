from fastapi import APIRouter, status

from app import deps, models
from app.routers.bots import schemas

router = APIRouter(prefix="/bots", tags=["Bots"])


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
