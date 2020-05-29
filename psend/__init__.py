from .psend import PushoverCog


def setup(bot):
    bot.add_cog(PushoverCog())
