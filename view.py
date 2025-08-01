import dash
from dash import dcc, html, Input, Output, dash_table
import pandas as pd
import plotly.express as px
import os
class View:
    def __init__(self, model):
        self.model = model

    def main(self):
        csv_files = self.model.csv_files
        tabs = [dcc.Tab(label=" ".join(os.path.basename(csv_file).split("_")[:2]),value=csv_file) for csv_file in csv_files]

        return html.Div([
            html.H1("Expense Overview"),
            html.Div([
                dcc.Upload(
                    id='upload-csv',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select a CSV File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px 0'
                    },
                    multiple=False
                ),
                html.Div(id='upload-output'),
            ]),
            dcc.Tabs(
                id='csv-tabs',
                value=list(csv_files)[-1] if csv_files else None,
                children=tabs
            ),
            html.Div(id='tab-content')
        ])
    
    def tab(self, selected_csv):
        df_expenses = self.model.expenses(selected_csv).copy(deep=False)
        df_expenses['Betrag (€)'] = df_expenses['Betrag (€)'].abs()
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
            hovertemplate='%{label}: %{value:.2f} €<extra></extra>',
            
        )
        df = self.model.df(selected_csv).copy()
        df['Type'] = df['Betrag (€)'].apply(lambda x: 'Income' if x >= 0 else 'Expense')
        df['Betrag (€)'] = df['Betrag (€)'].abs()
        agg_type = df.groupby(['Type'])['Betrag (€)'].sum().reset_index()

        bar_fig = px.bar(agg_type, x='Type', y='Betrag (€)',title='Income vs Expense', color='Type',
                         labels={'Betrag (€)': 'Total Amount (€)', 'Type': 'Income/Expense'},
                         text='Betrag (€)')
        bar_fig = bar_fig.update_traces(texttemplate='%{text:.2f} €', textposition='outside', cliponaxis=False)
        bar_fig = bar_fig.update_traces(
            hovertemplate='Type: %{x}<br>Total: %{y:.2f} €<extra></extra>'
        )
        df_details = df[['Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum', 'Kategorie']]
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
        
    def detailed_expenses_in_category(self, selected_csv, category):
        df = self.model.expense_in_category(selected_csv, category)
        df = df[['Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum', 'Kategorie']]
        df = df.sort_values(by='Betrag (€)')
        return f"Details for category: {category}", df.to_dict('records')
    
    def detailed_expenses(self, selected_csv):
        df = self.model.expenses(selected_csv)
        df = df[['Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum', 'Kategorie']]
        df = df.sort_values(by='Betrag (€)')
        return f"Expenses", df.to_dict('records')
    
    def detailed_income(self, selected_csv):
        df = self.model.income(selected_csv)
        df = df[['Zahlungspflichtige*r', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum', 'Kategorie']]
        df = df.sort_values(by='Betrag (€)')
        return f"Income", df.to_dict('records')