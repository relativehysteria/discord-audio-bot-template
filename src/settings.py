from discord.ext import commands
import logging

## Settings for the primary logger

LOG_FILE        = r"naga.log"
LOG_LEVEL       = logging.INFO
LOG_FORMAT      = \
    "{asctime} | {levelname:^8} | {name} | ({filename}:{lineno}) >> {message}"
LOG_TIME_FORMAT = "%H:%M:%S"
USE_LOG_COLORS  = True   # Whether to use colored output in the terminal
LOG_TO_FILE     = True   # Whether to log into a file as well

## Settings for the bot

COMMAND_PREFIX = commands.when_mentioned
# Reaction emojis
REACTION_OK  = "\U0001f44d"
REACTION_ERR = "\U0001F44E"

## TOKEN

TOKEN_FILE = "TOKEN"
