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

        embed = discord.Embed(title="COVID19 stats", description="Most recent stats for {}.".format(r["country"]["name"]), color=await ctx.embed_colour())
        embed.add_field(name="Date", value=r["country"]["mostRecent"]["date"], inline=False)
        embed.add_field(name="Confirmed", value=r["country"]["mostRecent"]["confirmed"], inline=False)
        embed.add_field(name="Recoveries", value=r["country"]["mostRecent"]["recovered"], inline=False)
        embed.add_field(name="Deaths", value=r["country"]["mostRecent"]["deaths"], inline=False)

        await ctx.send(embed=embed)