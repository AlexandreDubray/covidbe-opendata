# Inspired from https://covid19dashboards.com/covid-compare-permillion/
# and https://gist.github.com/gschivley/578c344461100071b7eef158efccce95

import dash_core_components as dcc
import dash_html_components as html
from pages import get_translation

import io

# config InlineBackend.figure_format = 'retina'

from graphs.deaths_per_million import lines_deaths_per_million
from pages.sources import display_source_providers, source_hopkins


def display_deaths_per_million():
    plot1 = lines_deaths_per_million()
    # Save html as a StringIO object in memory
    plot1_html = io.StringIO()
    plot1.save(plot1_html, 'html')

    return [
        html.H1(get_translation(
            en="""Deaths per million""",
            fr="""Morts par million""", )),
        dcc.Markdown(get_translation(
            en="""
                The number of reported deaths per million is a lower bound on the actual number of deaths per million inhabitants. Some countries have likely not reported all cases.
                """,
            fr="""
            Le nombre de décès signalés par million est une limite inférieure du nombre réel de décès par million d'habitants. Certains pays n'ont probablement pas signalé tous les cas.
            """,
        )),
        html.Iframe(
            id='plot',
            height='500',
            width='1000',
            sandbox='allow-scripts',

            # This is where we pass the html
            srcDoc=plot1_html.getvalue(),

            # Get rid of the border box
            style={'border-width': '0px'}
        ),
        display_source_providers(source_hopkins)
    ]


def callback_deaths_per_million(app):
    return None
