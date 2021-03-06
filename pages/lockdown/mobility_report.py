import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from flask_babel import get_locale, gettext

from graphs.google_mobility import google_mobility_plot_eu
from graphs.apple_mobility import apple_mobility_plot_eu
from pages.sources import display_source_providers, source_google_mobility, source_apple_mobility


def display_mobility():
    return [
        html.H2(gettext("Google Mobility Report Europe")),
        dbc.Row([
            dbc.Col(dcc.Graph(id='google mobility report eu',
                              figure=google_mobility_plot_eu(),
                              config=dict(locale=str(get_locale())))),
        ]),
        display_source_providers(source_google_mobility),
        html.H2(gettext("Apple Mobility Report Europe")),
        dbc.Row([
            dbc.Col(dcc.Graph(id='apple mobility report eu',
                              figure=apple_mobility_plot_eu(),
                              config=dict(locale=str(get_locale())))),
        ]),
        display_source_providers(source_apple_mobility)
    ]
