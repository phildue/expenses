import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import os

CSV_DIR = "test_output"

def get_csv_files():
    return [
        f for f in os.listdir(CSV_DIR)
        if f.endswith(".csv")
    ]

def load_data(csv_file):
    path = os.path.join(CSV_DIR, csv_file)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path)[['Buchungsdatum', 'Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Kategorie']]
    df = df[df['Betrag (€)'] < 0].copy()
    df['Betrag (€)'] = df['Betrag (€)'].abs()
    return df

def get_date_span(df):
    if df.empty:
        return "Zeitraum unbekannt"
    dates = pd.to_datetime(df['Buchungsdatum'], format='%d.%m.%y')
    min_date = dates.min()
    max_date = dates.max()
    if pd.notnull(min_date) and pd.notnull(max_date):
        return f"{min_date.strftime('%d.%m.%Y')} bis {max_date.strftime('%d.%m.%Y')}"
    return "Zeitraum unbekannt"

csv_files = get_csv_files()
tabs = []
for csv_file in csv_files:
    df = load_data(csv_file)
    date_span = get_date_span(df)
    tabs.append(
        dcc.Tab(label=f"{csv_file} ({date_span})", value=csv_file)
    )

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Expense Overview"),
    dcc.Tabs(
        id='csv-tabs',
        value=csv_files[0] if csv_files else None,
        children=tabs
    ),
    html.Div(id='tab-content')
])

@app.callback(
    Output('tab-content', 'children'),
    Input('csv-tabs', 'value')
)
def render_tab(selected_csv):
    if not selected_csv:
        return html.Div("No CSV files found.")
    df = load_data(selected_csv)
    date_span = get_date_span(df)
    total = df['Betrag (€)'].sum()
    pie_fig = px.pie(
        df,
        names='Kategorie',
        values='Betrag (€)',
        title='Expenses by Category',
        hole=0.4,
        custom_data=['Betrag (€)']
    ).update_traces(
        textinfo='label+value',
        hovertemplate='%{label}: %{value:.2f} €<extra></extra>'
    )
    return html.Div([
        html.H3(f"Total expenses: {total:.2f} € ({date_span})", style={"color": "#444"}),
        dcc.Graph(id='category-pie', figure=pie_fig),
        html.H2(id='details-title', children="Click a category to see details"),
        dash_table.DataTable(
            id='details-table',
            columns=[{"name": col, "id": col} for col in df.columns],
            data=df.to_dict('records'),
            page_size=10,
            style_table={'overflowX': 'auto'},
        )
    ])

@app.callback(
    Output('details-title', 'children'),
    Output('details-table', 'data'),
    Input('category-pie', 'clickData'),
    Input('csv-tabs', 'value')
)
def show_details(clickData, selected_csv):
    df = load_data(selected_csv)
    if not clickData or 'label' not in clickData['points'][0]:
        return "Click a category to see details", []
    category = clickData['points'][0]['label']
    filtered = df[df['Kategorie'] == category]
    return f"Details for category: {category}", filtered.to_dict('records')

if __name__ == "__main__":
    app.run(debug=True)