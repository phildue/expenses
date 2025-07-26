import pandas as pd
import argparse

def convert_betrag_column(df):
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