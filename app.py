import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import os
import argparse
import sys
import glob
from format import convert_betrag_column

def load_data(csv_file):
    try:
        df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
    except Exception as e:
        df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', skiprows=4)
    df = convert_betrag_column(df)
    df=df[['Buchungsdatum', 'Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Kategorie']]
    # Drop rows with any missing values in the selected columns
    #df = df.dropna(subset=['Buchungsdatum', 'Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Kategorie'])
    df = df[~df['Zahlungsempfänger*in'].isin(['Julia Sperger', 'Philipp Dürnay'])]
    df = df[df['Betrag (€)'] < 0].copy()
    df['Betrag (€)'] = df['Betrag (€)'].abs()
    df = df.sort_values(by='Betrag (€)', ascending=False)
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

def create_app(csv_dir):
    csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
    csv_files = sorted(
        csv_files,
        key=lambda f: pd.to_datetime(
            load_data(f)['Buchungsdatum'], format='%d.%m.%y', errors='coerce'
        ).min()
    )
    tabs = []
    for csv_file in csv_files:
        tabs.append(
            dcc.Tab(label=" ".join(os.path.basename(csv_file).split("_")[:2]), value=csv_file)
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

    return app

def main():
    parser = argparse.ArgumentParser(description="Dash app for visualizing classified expense CSVs.")
    parser.add_argument(
        "--csv-dir",
        type=str,
        default="test_output",
        help="Directory containing classified CSV files"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to run the Dash app"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8050,
        help="Port to run the Dash app"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.csv_dir):
        print(f"CSV directory '{args.csv_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    app = create_app(args.csv_dir)
    app.run(debug=True, host=args.host, port=args.port)

if __name__ == "__main__":
    main()