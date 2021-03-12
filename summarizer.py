#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 20:24:43 2021

@author: Eduardo
"""
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State


# Available languages

languages = """
    Czech
    English
    French
    German
    Italian
    Japanese
    Portuguese
    Slovak
    Spanish
    """

# External JS and CSS for the layout

external_scripts = [
    'https://www.google-analytics.com/analytics.js',
    {'src': 'https://cdn.polyfill.io/v2/polyfill.min.js'},
    {
        'src': 'https://cdnjs.cloudflare.com/ajax/libs/lodash.js/4.17.10/lodash.core.js',
        'integrity': 'sha256-Qqd/EfdABZUcAxjOkMi8eGEivtdTkh3b65xCZL4qAQA=',
        'crossorigin': 'anonymous'
    }
]

external_stylesheets = [
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    {
        'href': 'https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css',
        'rel': 'stylesheet',
        'integrity': 'sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO',
        'crossorigin': 'anonymous'
    }
]

# Dash app and server

app = dash.Dash(__name__,
                external_scripts=external_scripts,
                external_stylesheets=external_stylesheets)

app.title = 'AutoSummary'

server = app.server

# App layout

app.layout = html.Div([

    html.Br(),

    html.Div(style={'width': '1%',
                    'display': 'inline-block'}),

    html.Div([

        html.Div([

            html.H1([
                "AutoSummary"
                ], style={'fontSize': 20}
                ),

            html.Br(),

            html.P(
                "1. Select a language and enter the number of sentences for the summary"
                ),

            html.P(
                "2. Enter a URL starting with 'http', or paste plain text to be summarized"
                ),

        ], style={'display': 'inline-block',
                  'fontSize': 14}),

        # Language label

        html.Div([

            html.Label(['Language: '],
                       style={'fontFamily': 'Helvetica',
                              'fontSize': 14}),

        ], style={'text-align': 'right',
                  'width': '10%',
                  'display': 'inline-block'}
                  ),

        # Language dropdown menu

        html.Div([

            dcc.Dropdown(
                id='dropdown',
                options=[{'label': i, 'value': i.lower()}
                         for i in languages.split()],
                value='english',
                multi=False,
                searchable=True,
                clearable=False,
                style={'fontFamily': 'Helvetica',
                       'fontSize': 14}
                ),

        ], style={'width': '15%',
                  'display': 'inline-block',
                  'verticalAlign': 'middle'}
                  ),

        # Number of paragraphs label

        html.Div([

            html.Label(['Number or paragraphs: '],
                       style={'fontFamily': 'Helvetica',
                              'fontSize': 14}),

        ], style={'text-align': 'right',
                  'width': '15%',
                  'display': 'inline-block'}
                  ),

        # Number of paragraphs input box

        html.Div([

            dcc.Input(
                id='paragraphs-input', value=10, type='text'
                )

        ], style={'width': '5%',
                  'display': 'inline-block',
                  'fontSize': 14}
                  ),

        html.Br(),
        html.Br(),

        # Text area for text input and returned summary

        html.Div([

            dcc.Textarea(
                id='textarea',
                value="",
                style={'width': '100%',
                       'height': 160,
                       'fontFamily': 'Garamond',
                       'fontSize': 18},
            ),
            html.Button('Submit', id='textarea-button', n_clicks=0),
            html.Div(id='textarea-output',
                     style={'whiteSpace': 'pre-line',
                            'fontFamily': 'Garamond',
                            'fontSize': 20})

        ])

    ], style={'width': '98%',
              'display': 'inline-block'}),

    html.Div(style={'width': '1%',
                    'display': 'inline-block'})

])


@app.callback(
    Output('textarea-output', 'children'),
    [Input('textarea-button', 'n_clicks'),
     Input('dropdown', 'value'),
     Input('paragraphs-input', 'value')],
    State('textarea', 'value')
)
def update_summary(n_clicks, dropdown, sentences_count, textarea):
    """Update textbox with summary.

    Parameters must be passed in the same order as Inputs and State
    in the callback decorator.

    Parameters
    ----------
    n_clicks : int
        Button click: 0 if unclicked, 1 if clicked.
    dropdown : str
        Value (language) selected in the dropdown menu.
    sentences_count : int
        Number of sentences in the summary.
    textarea : str
        Input text: can be URL or plain text.

    Returns
    -------
    str
        Summary of the text, once the button is pressed.

    """
    if n_clicks > 0:

        # Summarize from URL
        if textarea.startswith('http'):
            parser = HtmlParser.from_url(textarea.strip(), Tokenizer(dropdown))

        # Summarize plain text
        else:
            parser = PlaintextParser.from_string(textarea, Tokenizer(dropdown))

        return summarize(textarea, dropdown, sentences_count, parser)


def summarize(text, language, sentences_count, parser):
    """Summarize text from input.

    Parameters
    ----------
    text : str
        Input that will be summarized.
    language : str
        Language selected in the dropdown menu.
    sentences_count : int
        Number of sentences in the summary.
    parser : sumy.parsers object
        Analyses the text depending on source.

    Returns
    -------
    str
        Summary of the text.

    """
    stemmer = Stemmer(language)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(language)

    sentences = [str(sentence)
                 for sentence in summarizer(parser.document, sentences_count)]

    return '\n' + '\n\n'.join(sentences)


if __name__ == '__main__':
    app.run_server(debug=True)
