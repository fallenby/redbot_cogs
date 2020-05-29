import urllib.request
import re

from redbot.core import commands, Config, checks
from pushover import Client
from bs4 import BeautifulSoup


class PushoverCog(commands.Cog):
    """Pushover notification bot"""
    def __init__(self):
        self.config = Config.get_conf(self, identifier=1234567890)

    @commands.group(aliases=["psend"], invoke_without_command=True)
    async def pushover(self, ctx, message="Message from Discord"):
        """Send a Pushover notification; [p]psend <message>"""

        title = "Message from {} Discord".format(ctx.guild.name)

        regex = re.compile(
            r'^(?:http|ftp)s?://' # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
            r'localhost|' #localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
            r'(?::\d+)?' # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        if re.match(regex, message) is not None:
            soup = BeautifulSoup(urllib.request.urlopen(message))
            title = soup.title.string

        client_token = await self.config.member(ctx.message.author).pushover_client_token()
        api_token = await self.config.guild(ctx.guild).pushover_api_token()

        if client_token is None:
            await ctx.send("No pushover client tokens found. Please set your tokens with [p]settoken <client_token>")
            return
        
        if api_token is None:
            await ctx.send("No pushover API tokens found. Please tell your server admin to set the Pushover API token with [p]setapitoken <api_token>.")
            return

        client = Client(client_token, api_token=api_token)

        if len(ctx.message.attachments) > 0:
            for attachment in ctx.message.attachments:
                if attachment.filename.split('.')[1] not in ['png']:
                    await ctx.send("Invalid message attachment. Psend can only send images.")
                    return

                req = urllib.request.Request(
                    attachment.url, 
                    data=None, 
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                    }
                )

                f = urllib.request.urlopen(req)

                client.send_message(message, title=title, attachment=f.read())
        else:
            client.send_message(message, title=title)

        await ctx.send("Push sent!")

    @commands.command()
    async def settoken(self, ctx, client_token):
        default_member = {
            "pushover_client_token": client_token,
        }

        self.config.register_member(**default_member)

        await ctx.send("Token set!")

    @commands.command()
    @checks.admin_or_permissions(manage_guild=True)
    async def setapitoken(self, ctx, api_token):
        default_guild = {
            "pushover_api_token": api_token,
        }

        self.config.register_guild(**default_guild)

        await ctx.send("Token set!")