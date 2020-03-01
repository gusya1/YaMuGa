import logging
import logging.config
from discord.ext.commands import Context

logging.config.fileConfig('logger.conf')
logger = logging.getLogger("file")


# def error(ctx : Context, message: str):
#     logger.error(message)