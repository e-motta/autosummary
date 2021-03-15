#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 20:24:43 2021

@author: Eduardo
"""
from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.summarizers.luhn import LuhnSummarizer
from sumy.summarizers.text_rank import TextRankSummarizer
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
    Portuguese
    Slovak
    Spanish
    """

# Summarizers

all_summarizers = {
    'LSA': LsaSummarizer,
    'LexRank': LexRankSummarizer,
    'Luhn': LuhnSummarizer,
    'TextRank': TextRankSummarizer
    }

# External JS and CSS for the app

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

    # Left Border

    html.Div(style={'width': '1%',
                    'display': 'inline-block'}),

    # Main

    html.Div([

        # Header

        html.Div([

            html.H1([
                "AutoSummary"
                ], style={'fontSize': 20,
                          'fontFamily': 'Helvetica',
                          'margin-top': '0.3em'}
                ),

        ]),

        html.Hr(),

        # Language and sentence counter

        html.Div([

            html.Div([

                # Language label

                html.Div([

                    html.Label(['Language:⠀'],
                               style={'fontFamily': 'Helvetica',
                                      'fontSize': 14}),

                ], style={'text-align': 'left',
                          'width': '100%'}
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

                ], style={'width': '50%',
                          'verticalAlign': 'middle',
                          'text-align': 'left'}
                          ),


            ], style={'width': '100%',
                      'text-align': 'left'}
            ),

            html.Br(),

            html.Div([

                # Number of sentences label

                html.Div([

                    html.Label(['Number or sentences:⠀'],
                               style={'fontFamily': 'Helvetica',
                                      'fontSize': 14,
                                      'text-align': 'right'}),

                ], style={'text-align': 'left',
                          'width': '100%'}
                          ),

                # Number of sentences input box

                html.Div([

                    dcc.Input(
                        id='sentences-input', value=10, type='text'
                        )

                ], style={'width': '100%',
                          'fontSize': 14}
                          ),

            ], style={'width': '100%',
                      'text-align': 'left'}
            ),

        ], style={'width': '30%',
                  'display': 'inline-block',
                  'color': 'DarkSlateGray'}
        ),

        # Instructions

        html.Div([

            html.Br(),

            html.P(
                "1. Select a language and enter the number of sentences for the summary"
                ),

            html.P(
                "2. Enter a URL starting with 'http', or paste plain text to be summarized"
                ),

            html.P(
                "3. Select the summarization technique and click Submit"
                ),

        ], style={'display': 'inline-block',
                  'fontSize': 14,
                  'width': '70%',
                  'color': 'DarkSlateGray',
                  'verticalAlign': 'top'}
        ),

        html.Br(),
        html.Br(),

        # Text area for text input and returned summary

        html.Div([

            dcc.Textarea(
                id='textarea',
                value="",
                placeholder='http... or plain text',
                style={'width': '100%',
                       'height': 100,
                       'fontFamily': 'Garamond',
                       'fontSize': 18},
            ),

            dcc.RadioItems(
                options=[
                    {'label': '⠀LSA⠀⠀⠀⠀', 'value': 'LSA'},
                    {'label': '⠀Lex Rank⠀⠀⠀⠀', 'value': 'LexRank'},
                    {'label': '⠀Luhn⠀⠀⠀⠀', 'value': 'Luhn'},
                    {'label': '⠀Text Rank⠀⠀⠀⠀', 'value': 'TextRank'},
                ],
                id='summarizer',
                value='LSA',
                labelStyle={'display': 'inline-block',
                            'fontSize': 14}),

            html.Button('Submit', id='textarea-button', n_clicks=0),

            html.Div(id='textarea-output',
                     style={'whiteSpace': 'pre-line',
                            'fontFamily': 'Garamond',
                            'fontSize': 20})

        ])

    ], style={'width': '98%',
              'display': 'inline-block'}),

    # Right border

    html.Div(style={'width': '1%',
                    'display': 'inline-block'})

])


@app.callback(
    Output('textarea-output', 'children'),
    [Input('textarea-button', 'n_clicks'),
     Input('dropdown', 'value'),
     Input('sentences-input', 'value'),
     Input('summarizer', 'value')],
    State('textarea', 'value')
)
def update_summary(n_clicks, dropdown_language, sentences_count,
                   summarizer_opt, text_area):
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
    text_area : str
        Input text: can be URL or plain text.

    Returns
    -------
    str
        Summary of the text, once the button is pressed.

    """
    # Button is clicked
    if n_clicks > 0:

        # Summarize from URL
        if text_area.startswith('http'):
            parser = HtmlParser.from_url(text_area.strip(),
                                         Tokenizer(dropdown_language))

        # Summarize plain text
        else:
            parser = PlaintextParser.from_string(text_area,
                                                 Tokenizer(dropdown_language))

        stemmer = Stemmer(dropdown_language)

        summarizer = all_summarizers[summarizer_opt](stemmer)
        summarizer.stop_words = get_stop_words(dropdown_language)

        sentences = [str(sentence)
                     for sentence in summarizer(parser.document,
                                                sentences_count)]

        return '\n' + '\n\n'.join(sentences)


if __name__ == '__main__':
    app.run_server(debug=True)
