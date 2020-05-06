import locale
import tempfile
import os

locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')

from redbot.core import commands

import quiz
import discord
import pathlib
import matplotlib
import matplotlib.pyplot as plt

class CovidCog(commands.Cog):
    """COVID19 stats bot"""

    @commands.group(aliases=["cvd"], invoke_without_command=True)
    async def covid(self, ctx, country = "South Africa"):
        """Fetch the most-recent COVID19 results for a given country."""

        world_query = """
        {
            countries {
                name
                mostRecent {
                    date(format: "yyyy-MM-dd")
                    confirmed
                    recovered
                    deaths
                }
            }
        }
        """

        url = "https://covid19-graphql.now.sh/"

        r_world = await quiz.execute_async(world_query, url=url)

        t_confirmed = 0
        t_recovered = 0
        t_deceased = 0

        for r_country in r_world["countries"]:
            t_confirmed += r_country["mostRecent"]["confirmed"]
            t_recovered += r_country["mostRecent"]["recovered"]
            t_deceased += r_country["mostRecent"]["deaths"]

            if r_country["name"].lower() == country.lower():
                c_date = r_country["mostRecent"]["date"]
                c_confirmed = r_country["mostRecent"]["confirmed"]
                c_recovered = r_country["mostRecent"]["recovered"]
                c_deceased = r_country["mostRecent"]["deaths"]

        embed = discord.Embed(title="COVID19", description="Stats for {}.".format(c_date), color=await ctx.embed_colour())
        embed.add_field(name="---", value="**Worldwide stats**", inline=False)
        embed.add_field(name="Confirmed", value=f'{t_confirmed:n}', inline=True)
        embed.add_field(name="Recovered", value=f'{t_recovered:n}', inline=True)
        embed.add_field(name="Deceased", value=f'{t_deceased:n}', inline=True)
        embed.add_field(name="---", value="**{} stats**".format(country), inline=False)
        embed.add_field(name="Confirmed", value=f'{c_confirmed:n}', inline=True)
        embed.add_field(name="Recovered", value=f'{c_recovered:n}', inline=True)
        embed.add_field(name="Deceased", value=f'{c_deceased:n}', inline=True)
        embed.set_footer(text="https://github.com/fallenby/redbot_cogs/tree/master/covid", icon_url="https://github.com/fluidicon.png")

        await ctx.send(embed=embed)

    @covid.command(aliases=["g"])
    async def graph(self, ctx, country = "South Africa"):
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

        imagefile = tempfile.NamedTemporaryFile(mode="wb", suffix = '.png')

        plt.plot([0, 1, 2, 3, 4], [0, 3, 5, 9, 11])
        plt.xlabel('Months')
        plt.ylabel('Books Read')
        plt.savefig(imagefile.name)

        dfile = discord.File(imagefile.name)

        await ctx.send(file=dfile)