import locale
import tempfile
import os
from datetime import datetime, timedelta

locale.setlocale(locale.LC_ALL, "en_US.UTF-8")

from redbot.core import commands
from redbot.core.utils import chat_formatting

import quiz
import discord
import pathlib
import matplotlib
import matplotlib.pyplot as plt


class CovidCog(commands.Cog):
    """COVID19 stats bot"""

    @commands.group(aliases=["cvd"], invoke_without_command=True)
    async def covid(self, ctx, country="South Africa"):
        """Fetch the most-recent COVID19 results for a given country."""

        fetching_message = await ctx.send(
            chat_formatting.info("Fetching COVID19 stats for {}..".format(country))
        )

        totals = await self.fetch_stats_for_date(country)

        c_date = datetime.now().date().strftime("%Y-%m-%d")

        # Construct the return embed chat message
        embed = discord.Embed(
            title="COVID19",
            description="Stats for {}.".format(c_date),
            color=await ctx.embed_colour(),
        )
        embed.add_field(name="---", value="**Worldwide stats**", inline=False)
        embed.add_field(
            name="Confirmed",
            value=f'{totals["world_confirmed"]:n}'
            + " ({})".format(
                self.prettify_delta_display(totals["world_confirmed_delta"])
            ),
            inline=True,
        )
        embed.add_field(
            name="Recovered",
            value=f'{totals["world_recovered"]:n}'
            + " ({})".format(
                self.prettify_delta_display(totals["world_recovered_delta"])
            ),
            inline=True,
        )
        embed.add_field(
            name="Deceased",
            value=f'{totals["world_deceased"]:n}'
            + " ({})".format(
                self.prettify_delta_display(totals["world_deceased_delta"])
            ),
            inline=True,
        )
        embed.add_field(
            name="Active cases",
            value=f'{totals["world_confirmed"] - totals["world_recovered"] - totals["world_deceased"]:n}'
            + " ({})".format(self.prettify_delta_display(totals["world_active_delta"])),
            inline=True,
        )
        embed.add_field(
            name="---",
            value="**{} stats (% of worldwide)**".format(country),
            inline=False,
        )
        embed.add_field(
            name="Confirmed",
            value=f'{totals["country_confirmed"]:n}'
            + " ({}, {}%)".format(
                self.prettify_delta_display(totals["country_confirmed_delta"]),
                totals["country_percent_of_world_confirmed"],
            ),
            inline=True,
        )
        embed.add_field(
            name="Recovered",
            value=f'{totals["country_recovered"]:n}'
            + " ({}, {}%)".format(
                self.prettify_delta_display(totals["country_recovered_delta"]),
                totals["country_percent_of_world_recovered"],
            ),
            inline=True,
        )
        embed.add_field(
            name="Deceased",
            value=f'{totals["country_deceased"]:n}'
            + " ({}, {}%)".format(
                self.prettify_delta_display(totals["country_deceased_delta"]),
                totals["country_percent_of_world_deceased"],
            ),
            inline=True,
        )
        embed.add_field(
            name="Active cases",
            value=f'{totals["country_confirmed"] - totals["country_recovered"] - totals["country_deceased"]:n}'
            + " ({}, {}%)".format(
                self.prettify_delta_display(totals["country_active_delta"]),
                totals["country_percent_of_world_active"],
            ),
            inline=True,
        )
        embed.set_footer(
            text="https://github.com/fallenby/redbot_cogs/tree/master/covid",
            icon_url="https://github.com/fluidicon.png",
        )

        await fetching_message.delete()

        await ctx.send(embed=embed)

    @covid.command(aliases=["g"])
    async def graph(self, ctx, country="South Africa"):
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
        """ % (
            country
        )

        url = "https://covid19-graphql.now.sh/"

        r = await quiz.execute_async(query, url=url)

        imagefile = tempfile.NamedTemporaryFile(mode="wb", suffix=".png")

        plt.plot([0, 1, 2, 3, 4], [0, 3, 5, 9, 11])
        plt.xlabel("Months")
        plt.ylabel("Books Read")
        plt.savefig(imagefile.name)

        dfile = discord.File(imagefile.name)

        await ctx.send(file=dfile)

    @covid.command(aliases=["c"])
    async def countries(self, ctx):
        """Fetch the most-recent COVID19 results for a given country."""

        query = """
        {
            countries {
                name
            }
        }
        """

        url = "https://covid19-graphql.now.sh/"
        m_count = 50
        m_pos = 0
        c_list = ""

        r = await quiz.execute_async(query, url=url)

        messages = []

        for result in r["countries"]:
            c_list += result["name"] + "\n"
            m_pos += 1

            if m_pos == m_count:
                messages.append(c_list)
                m_pos = 0
                c_list = ""
                continue

        messages.append(c_list)

        await ctx.send_interactive(messages)

    async def fetch_stats_for_date(self, country, date=None):
        url = "https://covid19-graphql.now.sh/"

        if date is None:
            date = datetime.now().date()

        # Data for results lags behind for 1 day
        result_date = date - timedelta(days=1)
        day_before_result_date = result_date - timedelta(days=1)

        query = """
        {
            results (date: { lt: "%s" }) {
                country {
                    name
                }
                date
                confirmed
                deaths
                recovered
                growthRate
            }
        }
        """ % (
            date.strftime("%Y-%m-%d")
        )

        results = await quiz.execute_async(query, url=url)

        # Worldwide total counts for latest date
        t_confirmed = 0
        t_recovered = 0
        t_deceased = 0

        # Worldwide total counts for the day before the latest date
        t_y_confirmed = 0
        t_y_recovered = 0
        t_y_deceased = 0

        for r_result in results["results"]:
            if (
                datetime.strptime(r_result["date"], "%Y-%m-%d").date()
                == day_before_result_date
            ):
                t_y_confirmed += r_result["confirmed"]
                t_y_recovered += r_result["recovered"]
                t_y_deceased += r_result["deaths"]

                if r_result["country"]["name"].lower() == country.lower():
                    c_y_confirmed = r_result["confirmed"]
                    c_y_recovered = r_result["recovered"]
                    c_y_deceased = r_result["deaths"]

            if datetime.strptime(r_result["date"], "%Y-%m-%d").date() == result_date:
                t_confirmed += r_result["confirmed"]
                t_recovered += r_result["recovered"]
                t_deceased += r_result["deaths"]

                if r_result["country"]["name"].lower() == country.lower():
                    c_confirmed = r_result["confirmed"]
                    c_recovered = r_result["recovered"]
                    c_deceased = r_result["deaths"]

        data = {
            "world_confirmed": t_confirmed,
            "world_recovered": t_recovered,
            "world_deceased": t_deceased,
            "world_active": t_confirmed - t_recovered - t_deceased,
            "country_confirmed": c_confirmed,
            "country_recovered": c_recovered,
            "country_deceased": c_deceased,
            "country_active": c_confirmed - c_recovered - c_deceased,
            "world_confirmed_delta": t_confirmed - t_y_confirmed,
            "world_recovered_delta": t_recovered - t_y_recovered,
            "world_deceased_delta": t_deceased - t_y_deceased,
            "world_active_delta": (t_confirmed - t_y_confirmed)
            - (t_recovered - t_y_recovered)
            - (t_deceased - t_y_deceased),
            "country_confirmed_delta": c_confirmed - c_y_confirmed,
            "country_recovered_delta": c_recovered - c_y_recovered,
            "country_deceased_delta": c_deceased - c_y_deceased,
            "country_active_delta": (c_confirmed - c_y_confirmed)
            - (c_recovered - c_y_recovered)
            - (c_deceased - c_y_deceased),
            "country_percent_of_world_confirmed": round(
                (float(c_confirmed) / float(t_confirmed)) * 100, 2
            ),
            "country_percent_of_world_recovered": round(
                (float(c_recovered) / float(t_recovered)) * 100, 2
            ),
            "country_percent_of_world_deceased": round(
                (float(c_deceased) / float(t_deceased)) * 100, 2
            ),
            "country_percent_of_world_active": round(
                (
                    float(c_confirmed - c_recovered - c_deceased)
                    / float(t_confirmed - t_recovered - t_deceased)
                )
                * 100,
                2,
            ),
        }

        return data

    def prettify_delta_display(self, delta):
        result = delta

        if delta > 0:
            result = "+" + str(f"{delta:n}")

        return str(result)
