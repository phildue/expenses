# Expense Tracker Dashboard

A Dash-based web application for visualizing and managing classified expense CSV files.

## Installation

### Development Installation

Clone the repository and install in development mode:

```bash
git clone <repository-url>
cd abrechnung
pip install -e .
```

### Production Installation

```bash
pip install expenses
```

## Package Structure

The project is organized as a Python package:

```
expenses/
├── __init__.py           # Package initialization
├── classifier.py         # Transaction classification logic
├── plot.py              # Plotting utilities
├── controller/          # Application controllers
│   ├── __init__.py
│   └── controller.py
├── model/              # Data models
│   ├── __init__.py
│   └── model.py
└── view/               # UI views
    ├── __init__.py
    └── view.py
```

## Features

- **Interactive Dashboard**: View expense data with pie charts and bar graphs
- **Category-based Analysis**: Click on categories to see detailed expense breakdowns
- **Income vs Expense Overview**: Visual comparison of income and expenses
- **Add New Entries**: Add new expense or income entries directly through the web interface
- **Editable Data Table**: View and edit existing entries in a table format

## Usage

### Running the Application

```bash
python app.py --csv-dir data --host 127.0.0.1 --port 8050 --debug
```

### Command Line Options

- `--csv-dir`: Directory containing classified CSV files (default: "test_output")
- `--host`: Host to run the Dash app (default: "127.0.0.1")
- `--port`: Port to run the Dash app (default: 8050)
- `--debug`: Enable debug mode

### Adding New Entries

1. Navigate to any CSV tab in the application
2. Click the "Add New Entry" button
3. Fill in the required fields:
   - **Buchungsdatum**: Booking date (DD.MM.YY format)
   - **Wertstellung**: Value date (DD.MM.YY format)
   - **Verwendungszweck**: Purpose/description
   - **Betrag (€)**: Amount in euros (use negative for expenses, positive for income)
   - **Kategorie**: Category for the entry
4. Optional fields:
   - **Zahlungspflichtige*r**: Payer name
   - **Zahlungsempfänger*in**: Payee name
   - **Umsatztyp**: Transaction type (Eingang/Ausgang)
5. Click "Add Entry" to save the new entry

### CSV File Format

The application expects CSV files with the following columns:
- `Buchungsdatum`: Booking date
- `Wertstellung`: Value date
- `Status`: Transaction status
- `Zahlungspflichtige*r`: Payer
- `Zahlungsempfänger*in`: Payee
- `Verwendungszweck`: Purpose
- `Umsatztyp`: Transaction type
- `IBAN`: IBAN number
- `Betrag (€)`: Amount in euros
- `Gläubiger-ID`: Creditor ID
- `Mandatsreferenz`: Mandate reference
- `Kundenreferenz`: Customer reference
- `Kategorie`: Category

## Architecture

The application follows the Model-View-Controller (MVC) pattern:

- **Model** (`model.py`): Handles data loading, processing, and saving
- **View** (`view.py`): Defines the UI components and layout
- **Controller** (`controller.py`): Manages user interactions and callbacks

## Dependencies

- `dash`: Web framework for building analytical web applications
- `pandas`: Data manipulation and analysis
- `plotly.express`: Interactive plotting library
- `matplotlib`: Static plotting library for additional visualizations
- `pyyaml`: YAML configuration file parsing

## Configuration

The application uses a YAML configuration file (`config/categories.yaml`) to define transaction categories and their associated keywords. Each category should have:
- `name`: The category name
- `keywords`: List of keywords to match against transactions

## Components

### Main Components
- **Model** (`model.py`): Handles data loading, processing, and saving
- **View** (`view.py`): Defines the UI components and layout
- **Controller** (`controller.py`): Manages user interactions and callbacks

### Additional Components
- **Classifier** (`classifier.py`): Automatically categorizes transactions based on configured keywords
- **Plot** (`plot.py`): Provides additional plotting capabilities for data visualization

## File Structure

```
abrechnung/
├── app.py              # Main application entry point
├── model.py           # Data model and processing
├── view.py            # UI components
├── controller.py      # User interaction handling
├── classifier.py      # Transaction classification logic
├── plot.py            # Additional plotting functionality
├── config/
│   └── categories.yaml # Category definitions and keywords
├── data/              # CSV data files
└── README.md          # This documentation
```

## Classification

To classify new transaction files:

```bash
python classifier.py <input_folder> <output_path>
```

The classifier will:
1. Read transaction CSV files from the input folder
2. Categorize transactions based on keywords defined in `config/categories.yaml`
3. Save classified files to the output path with "_classified" suffix