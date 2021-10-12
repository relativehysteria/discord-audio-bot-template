#!/bin/env python
from discord.ext.commands import Bot
from settings import TOKEN_FILE
from bot import Naga

if __name__ == "__main__":
    # Read the token from the token file
    with open(TOKEN_FILE) as f:
        token = f.read().strip()

    # Run the bot
    naga = Bot("TODO MULTIPLE PREFIXES")
    naga.add_cog(Naga(naga))
    naga.run(token)
