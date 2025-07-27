
import os
import argparse
import sys
import glob
import pandas as pd
import dash
from dash import dcc, html, Input, Output, dash_table

from view import View
from model import Model
from controller import Controller


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

    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    if not os.path.isdir(args.csv_dir):
        print(f"CSV directory '{args.csv_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    model = Model(args.csv_dir)

    app = dash.Dash(__name__)
    view = View(model)

    app.layout = view.main()
    controller = Controller(app, model, view)

    app.run(debug=args.debug, host=args.host, port=args.port)

if __name__ == "__main__":
    main()