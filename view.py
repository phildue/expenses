import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import os
class View:
    def __init__(self, model):
        self.model = model

    def get_layout(self):
        csv_files = self.model.csv_files
        tabs = [dcc.Tab(label=" ".join(os.path.basename(csv_file).split("_")[:2]),value=csv_file) for csv_file in csv_files]

        return html.Div([
            html.H1("Expense Overview"),
            dcc.Tabs(
                id='csv-tabs',
                value=list(csv_files)[-1] if csv_files else None,
                children=tabs
            ),
            html.Div(id='tab-content')
        ])
    
    def get_tab_layout(self, selected_csv):
        df_expenses = self.model.expenses(selected_csv)
        df_expenses['Betrag (€)'] = df_expenses['Betrag (€)'].abs()  # Ensure amounts are positive for pie chart
        if df_expenses.empty:
            return html.Div("No expenses found for this CSV file.")
        date_span = self.model.get_date_span(df_expenses)
        pie_fig = px.pie(
            df_expenses,
            names='Kategorie',
            values='Betrag (€)',
            title='Expenses by Category',
            hole=0.4,
            custom_data=['Betrag (€)']
        ).update_traces(
            textinfo='label+value',
            hovertemplate='%{label}: %{value:.2f} €<extra></extra>'
        )
        df = self.model.df(selected_csv).copy()
        df['Type'] = df['Betrag (€)'].apply(lambda x: 'Income' if x >= 0 else 'Expense')
        df['Betrag (€)'] = df['Betrag (€)'].abs()
        agg_type = df.groupby(['Type'])['Betrag (€)'].sum().reset_index()

        bar_fig = px.bar(agg_type, x='Type', y='Betrag (€)',title='Income vs Expense', color='Type',
                         labels={'Betrag (€)': 'Total Amount (€)', 'Type': 'Income/Expense'},
                         text='Betrag (€)').update_traces(texttemplate='%{text:.2f} €', textposition='outside')
        df_details = df[['Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum']]
        return html.Div([
            html.H3(f"{date_span}", style={"color": "#444"}),
            html.Div([
                dcc.Graph(id='bar-fig', figure=bar_fig),
                dcc.Graph(id='category-pie-2', figure=pie_fig)
                ], style={'display': 'flex', 'justifyContent': 'space-around'}),
            html.H2(id='details-title', children="Click a category to see details"),
            dash_table.DataTable(
                id='details-table',
                columns=[{"name": col, "id": col} for col in df_details.columns],
                data=df_details.to_dict('records'),
                page_size=10,
                style_table={'overflowX': 'auto'},
            )
        ])