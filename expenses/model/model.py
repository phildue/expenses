import pandas as pd
import argparse
import glob
import os
import yaml
from ..classifier import Classifier
from datetime import datetime


class Model:
    def __init__(self, csv_dir):
        self.csv_dir = csv_dir  # Store the csv_dir
        # Load categories configuration the same way as in classifier.py
        with open('config/categories.yaml', 'r', encoding='utf-8') as f:
            categories_yaml = yaml.safe_load(f)
        categories_list = categories_yaml.get("Categories", [])
        # Convert list of dicts to dict with category name as key
        categories = {cat["name"]: {"keywords": cat["keywords"]} for cat in categories_list}
        self.classifier = Classifier(categories)
        self.refresh_data()

    def refresh_data(self):
        """Refresh the list of CSV files and their data"""
        csv_files = glob.glob(os.path.join(self.csv_dir, "*.csv"))
        csv_files = sorted(csv_files,
                            key=lambda f: pd.to_datetime(
                                self._load_data(f)['Buchungsdatum'], format='%d.%m.%y', errors='coerce'
                            ).min()
                            )
        self.csv_files = csv_files
        self.data = {csv_file: self._load_data(csv_file) for csv_file in csv_files}

    def classify_and_save_file(self, df_raw, filename=None):
        """Classify a DataFrame and save it to the csv directory"""
        # Use the same simple logic as classifier.py
        df = df_raw.copy()
        
        # Apply classification using the same logic as classifier.py
        categories = []
        for _, row in df.iterrows():
            if any(column not in row for column in ['Zahlungsempfänger*in', 'Verwendungszweck']):
                categories.append(None)
                continue
            line_text = " ".join(str(item) for item in row[["Zahlungsempfänger*in", 'Verwendungszweck']])
            try:
                category = self.classifier.classify(line_text)
                categories.append(category)
            except ValueError as e:
                print(e)
                categories.append(None)
        
        df['Kategorie'] = categories
        
        # Generate output filename if not provided
        if filename is None:
            try:
                # Try to parse the first date to generate a meaningful filename
                first_date = df['Buchungsdatum'].iloc[0]
                current_date = pd.to_datetime(first_date, format='%d.%m.%y')
                filename = f"{current_date.year}_{current_date.strftime('%B')}_classified.csv"
            except:
                filename = f"classified_{datetime.now().strftime('%Y_%m_%d')}.csv"
        
        # Save the classified file
        output_path = os.path.join(self.csv_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8', sep=';')
        self.refresh_data()
        return output_path

    def add_classified_file(self, df, filename):
        """Save a new classified DataFrame to the csv directory"""
        output_path = os.path.join(self.csv_dir, filename)
        df.to_csv(output_path, index=False, encoding='utf-8', sep=';')
        self.refresh_data()
        return output_path

    def save(self):
        for csv_file, df in self.data.items():
            df.to_csv(csv_file, index=False, encoding='utf-8', sep=';')

    
    def df(self, csv_file):
        """Return a dictionary of DataFrames for each CSV file."""
        return self.data[csv_file]
            
    def expenses(self, csv_file):
        df = self.data[csv_file]
        return df[df['Betrag (€)'] < 0]
    
    def income(self, csv_file):
        df = self.data[csv_file]
        return df[df['Betrag (€)'] > 0]
    
    def expense_in_category(self, csv_file, category):
        df = self.data[csv_file]
        df = df[df['Kategorie'] == category]
        return df[df['Betrag (€)'] < 0]

    def get_date_span(self, df):
        if df.empty:
            return "Zeitraum unbekannt"
        dates = pd.to_datetime(df['Buchungsdatum'], format='%d.%m.%y')
        min_date = dates.min()
        max_date = dates.max()
        if pd.notnull(min_date) and pd.notnull(max_date):
            return f"{min_date.strftime('%d.%m.%Y')} bis {max_date.strftime('%d.%m.%Y')}"
        return "Zeitraum unbekannt"
    
    def _convert_betrag_column(self, df):
        """Convert 'Betrag (€)' column from German to standard decimal notation."""
        if 'Betrag (€)' in df.columns:
            # Convert to string and handle NaN values
            df['Betrag (€)'] = df['Betrag (€)'].astype(str).replace('nan', '0')
            
            # German format: 1.234,56 -> Standard format: 1234.56
            # First remove dots (thousand separators), then replace comma with dot (decimal)
            df['Betrag (€)'] = (
                df['Betrag (€)']
                .str.replace('.', '', regex=False)   # Remove thousand separator (dots)
                .str.replace(',', '.', regex=False)  # Replace decimal comma with dot
            )
            # Convert to numeric
            df['Betrag (€)'] = pd.to_numeric(df['Betrag (€)'], errors='coerce')
        return df

    def _load_data(self, csv_file):
        """Load CSV data with robust error handling for different formats"""
        df = None
        
        # Try different approaches to read the CSV file
        # Start with skiprows=4 since that's the most common format for bank exports
        for skip_rows in [4, 0, 1, 2, 3, 5]:
            try:
                df = pd.read_csv(
                    csv_file, 
                    delimiter=';', 
                    encoding='utf-8', 
                    skiprows=skip_rows,
                    on_bad_lines='skip',  # Skip problematic lines
                    quotechar='"'  # Handle quoted fields properly
                )
                # Check if we have the required columns
                if all(col in df.columns for col in ['Buchungsdatum', 'Betrag (€)']):
                    # Remove any completely empty rows
                    df = df.dropna(how='all')
                    break
                else:
                    df = None
            except Exception:
                continue
        
        # If still no success, try with the old method as fallback
        if df is None:
            try:
                df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', quotechar='"')
            except Exception:
                df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', skiprows=4, quotechar='"')
        
        df = self._convert_betrag_column(df)
        df = self._preprocess_income(df)
        return df
    
    def _preprocess_income(self, df):
        """Preprocess income data."""
        # Check if the required column exists
        if "Verwendungszweck" not in df.columns:
            return df
            
        # Handle potential missing values in the column
        mask = df["Verwendungszweck"].fillna("").str.contains("Ausgleich", case=True, na=False)

        matching_rows = df[mask]
        if matching_rows.empty:
            return df
            
        try:
            total_sum = matching_rows["Betrag (€)"].sum()
            
            # Get the first row's values safely
            first_row = matching_rows.iloc[0]
            
            summary_row = { 
                "Buchungsdatum": [first_row.get("Buchungsdatum", "")],
                "Wertstellung": [first_row.get("Wertstellung", "")],
                "Status": [first_row.get("Status", "")],
                "Zahlungspflichtige*r": [""],
                "Zahlungsempfänger*in": [""],
                "Verwendungszweck": ["Ausgleich Verrechnet"],
                "Umsatztyp": ["Zusammenfassung"],
                "IBAN": [""],
                "Betrag (€)": [total_sum],
                "Gläubiger-ID": [""],
                "Mandatsreferenz": [""],
                "Kundenreferenz": [""],
                "Kategorie": ["sonstiges"]
            }
            
            # Only include columns that exist in the original dataframe
            summary_row = {k: v for k, v in summary_row.items() if k in df.columns}
            
            summary_row_df = pd.DataFrame(summary_row)
            df = df[~mask]
            df = pd.concat([df, summary_row_df], ignore_index=True)
        except Exception as e:
            print(f"Error in _preprocess_income: {e}")
            # If there's an error, just return the original dataframe
            return df
            
        return df
