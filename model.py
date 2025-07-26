import pandas as pd
import argparse
import glob
import os


class Model:
    def __init__(self, csv_dir):
        csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
        csv_files = sorted(csv_files,
                            key=lambda f: pd.to_datetime(
                                self.load_data(f)['Buchungsdatum'], format='%d.%m.%y', errors='coerce'
                            ).min()
                            )
        self.csv_files = csv_files
        self.data = {csv_file: self.load_data(csv_file) for csv_file in csv_files}
        
        
    def load_data(self, csv_file):
        try:
            df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
        except Exception as e:
            df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', skiprows=4)
        df = self.convert_betrag_column(df)
        df = df[df['Verwendungszweck']!='Ausgleich']
        return df

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
    
    def convert_betrag_column(self,df):
        """Convert 'Betrag (€)' column from German to standard decimal notation."""
        if 'Betrag (€)' in df.columns:
            df['Betrag (€)'] = (
                df['Betrag (€)']
                .str.replace('.', '', regex=False)   # Remove thousand separator
                .str.replace(',', '.', regex=False)  # Replace decimal comma with dot
            )
            df['Betrag (€)'] = pd.to_numeric(df['Betrag (€)'], errors='coerce')
        return df


def read_csv(input_file):
    """Read CSV with ; separator and all columns as string."""
    return pd.read_csv(input_file, sep=';', dtype=str)

def write_csv(df, output_file):
    """Write DataFrame to CSV with , separator and utf-8 encoding."""
    df.to_csv(output_file, sep=',', index=False, encoding='utf-8')

def main():
    parser = argparse.ArgumentParser(description="Convert German CSV to standard format.")
    parser.add_argument("input_file", help="Input CSV file")
    parser.add_argument("output_file", help="Output CSV file")
    args = parser.parse_args()

    df = read_csv(args.input_file)
    df = convert_betrag_column(df)
    write_csv(df, args.output_file)

if __name__ == "__main__":
    main()