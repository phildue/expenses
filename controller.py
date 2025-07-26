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
            return self.view.get_tab_layout(selected_csv=selected_csv)
        
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
                category = pie_click['points'][0]['label']
                filtered = self.model.expense_in_category(selected_csv, category)
                filtered = filtered[['Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum']]
                return f"Details for category: {category}", filtered.to_dict('records')
        
            if triggered == 'bar-fig' and bar_click and 'label' in bar_click['points'][0]:
                group = bar_click['points'][0]['label']
                if group == 'Expense':
                    df = self.model.expenses(selected_csv)
                    df = df[['Zahlungsempfänger*in', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum']]
                    df = df.sort_values(by='Betrag (€)')
                    return f"Expenses", df.to_dict('records')
                else:
                    df = self.model.income(selected_csv)
                    df = df[['Zahlungspflichtige*r', 'Verwendungszweck', 'Betrag (€)', 'Buchungsdatum']]
                    df = df.sort_values(by='Betrag (€)', ascending=False)
                    return f"Income", df.to_dict('records')

            return "Click a category to see details", []

        