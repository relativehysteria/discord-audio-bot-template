from discord.ext import commands
import logging


## Settings for the primary logger

USE_LOG_COLORS  = True   # Whether to use colored output in the terminal
LOG_TO_FILE     = True   # Whether to log into a file
LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE        = r"naga.log"
LOG_LEVEL       = logging.DEBUG
LOG_FORMAT      = \
    "{asctime} | {levelname:^8} | {name} | ({filename}:{lineno}) >> {message}"


## Settings for the bot

TOKEN_FILE = "TOKEN"
