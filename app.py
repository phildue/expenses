import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import os

# Path to your classified CSV
CSV_PATH = "test_output/classified_transactions.csv"

# Load data
def load_data():
    if not os.path.exists(CSV_PATH):
        return pd.DataFrame()
    df = pd.read_csv(CSV_PATH)[['Buchungsdatum', 'Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Kategorie']]
    # Only consider expenses (negative amounts)
    df = df[df['Betrag (€)'] < 0].copy()
    df['Betrag (€)'] = df['Betrag (€)'].abs()
    return df

df = load_data()
# Parse dates
dates = pd.to_datetime(df['Buchungsdatum'], format='%d.%m.%y')
min_date = dates.min()
max_date = dates.max()
if pd.notnull(min_date) and pd.notnull(max_date):
    date_span = f"{min_date.strftime('%d.%m.%Y')} bis {max_date.strftime('%d.%m.%Y')}"
else:
    date_span = "Zeitraum unbekannt"

total = df['Betrag (€)'].sum()

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Expense Overview"),
    html.H3(f"Total expenses: {total:.2f} € ({date_span})", style={"color": "#444"}),
    dcc.Graph(
        id='category-pie',
        figure=px.pie(
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
    ),
    html.H2(id='details-title', children="Click a category to see details"),
    dash_table.DataTable(
        id='details-table',
        columns=[
            {"name": col, "id": col} for col in df.columns
        ],
        data=df.to_dict('records'),
        page_size=10,
        style_table={'overflowX': 'auto'},
    )
])

@app.callback(
    Output('details-title', 'children'),
    Output('details-table', 'data'),
    Input('category-pie', 'clickData')
)
def show_details(clickData):
    if not clickData or 'label' not in clickData['points'][0]:
        return "Click a category to see details", []
    category = clickData['points'][0]['label']
    filtered = df[df['Kategorie'] == category]
    return f"Details for category: {category}", filtered.to_dict('records')

if __name__ == "__main__":
    app.run(debug=True)