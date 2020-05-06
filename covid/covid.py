from redbot.core import commands

import quiz
import discord

class CovidCog(commands.Cog):
    """COVID19 stats bot"""

    @commands.command()
    async def covid(self, ctx, country = "South Africa"):
        """Fetch the most-recent COVID19 results for a given country."""

        query = """
        {
            country(name: "%s") {
                name
                mostRecent {
                date(format: "yyyy-MM-dd")
                confirmed
                recovered
                deaths
                }
            }
        }
        """ % (country)

        url = "https://covid19-graphql.now.sh/"

        r = await quiz.execute_async(query, url=url)

        embed = discord.Embed(title="COVID19", description="Stats for {} on {}.".format(r["country"]["name"], r["country"]["mostRecent"]["date"]), color=await ctx.embed_colour())
        embed.add_field(name="Confirmed", value=r["country"]["mostRecent"]["confirmed"], inline=True)
        embed.add_field(name="Recovered", value=r["country"]["mostRecent"]["recovered"], inline=True)
        embed.add_field(name="Deceased", value=r["country"]["mostRecent"]["deaths"], inline=True)
        embed.set_footer(text="https://github.com/fallenby/redbot_cogs/tree/master/covid", icon_url="https://github.com/fluidicon.png")

        await ctx.send(embed=embed)