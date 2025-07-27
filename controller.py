import dash
from dash import dcc, html, Input, Output, dash_table
from dash import callback_context

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

        