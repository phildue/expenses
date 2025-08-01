import dash
from dash import dcc, html, Input, Output, dash_table, State
from dash import callback_context
import base64
import io
import pandas as pd
import os

class Controller:
    def __init__(self,app, model, view):
        self.app = app
        self.model = model
        self.view = view
        self.register_callbacks()

    def register_callbacks(self):
        @self.app.callback(
        Output('tab-content', 'children'),
        Input('csv-tabs', 'value'))
        def render_tab(selected_csv):
            return self.view.tab(selected_csv=selected_csv)
        
        @self.app.callback(
            Output('details-title', 'children'),
            Output('details-table', 'data'),
            Input('category-pie-2', 'clickData'),
            Input('bar-fig', 'clickData'),
            Input('csv-tabs', 'value'))
        def show_details(pie_click,bar_click, selected_csv):
            ctx = callback_context
            triggered = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

            if triggered == 'category-pie-2' and pie_click and 'label' in pie_click['points'][0]:
                return self.view.detailed_expenses_in_category(selected_csv, category=pie_click['points'][0]['label'])
                
            if triggered == 'bar-fig' and bar_click and 'label' in bar_click['points'][0]:
                group = bar_click['points'][0]['label']
                if group == 'Expense':
                    return self.view.detailed_expenses(selected_csv)
                else:
                    return self.view.detailed_income(selected_csv)

            return "Click a category to see details", []

        @self.app.callback(
            Output('upload-output', 'children'),
            Output('csv-tabs', 'children'),
            Output('csv-tabs', 'value'),
            Input('upload-csv', 'contents'),
            State('upload-csv', 'filename'),
            State('csv-tabs', 'children'))
        def handle_upload(contents, filename, existing_tabs):
            if contents is None:
                return None, existing_tabs, existing_tabs[-1]['props']['value'] if existing_tabs else None

            try:
                # Decode the uploaded file
                content_type, content_string = contents.split(',')
                decoded = base64.b64decode(content_string)
                
                # Read the CSV file using the same simple logic as classifier.py
                csv_content = decoded.decode('utf-8')
                try:
                    df = pd.read_csv(io.StringIO(csv_content), delimiter=';', encoding='utf-8')
                except Exception:
                    df = pd.read_csv(io.StringIO(csv_content), delimiter=';', encoding='utf-8', skiprows=4)
                
                # Use the model to classify and save the file
                new_file_path = self.model.classify_and_save_file(df)
                output_filename = os.path.basename(new_file_path)
                
                # Update tabs
                new_tabs = [
                    dcc.Tab(
                        label=" ".join(os.path.basename(csv_file).split("_")[:2]),
                        value=csv_file
                    ) for csv_file in self.model.csv_files
                ]
                
                return html.Div([
                    html.P(f'Successfully processed and saved as {output_filename}', 
                           style={'color': 'green'})
                ]), new_tabs, new_file_path
                
            except Exception as e:
                return html.Div([
                    html.P(f'Error processing file: {str(e)}',
                           style={'color': 'red'})
                ]), existing_tabs, existing_tabs[-1]['props']['value'] if existing_tabs else None

