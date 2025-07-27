import pandas as pd
import argparse
import glob
import os


class Model:
    def __init__(self, csv_dir):
        csv_files = glob.glob(os.path.join(csv_dir, "*.csv"))
        csv_files = sorted(csv_files,
                            key=lambda f: pd.to_datetime(
                                self._load_data(f)['Buchungsdatum'], format='%d.%m.%y', errors='coerce'
                            ).min()
                            )
        self.csv_files = csv_files
        self.data = {csv_file: self._load_data(csv_file) for csv_file in csv_files}

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
    
    def _convert_betrag_column(self,df):
        """Convert 'Betrag (€)' column from German to standard decimal notation."""
        if 'Betrag (€)' in df.columns:
            df['Betrag (€)'] = (
                df['Betrag (€)']
                .str.replace('.', '', regex=False)   # Remove thousand separator
                .str.replace(',', '.', regex=False)  # Replace decimal comma with dot
            )
            df['Betrag (€)'] = pd.to_numeric(df['Betrag (€)'], errors='coerce')
        return df

    def _load_data(self, csv_file):
        try:
            df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
        except Exception as e:
            df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8', skiprows=4)
        df = self._convert_betrag_column(df)
        df = self._preprocess_income(df)
        return df
    
    def _preprocess_income(self, df):
        """Preprocess income data."""
        mask = df["Verwendungszweck"].str.contains("Ausgleich", case=True, na=False)

        matching_rows = df[mask]
        if matching_rows.empty:
            return df
        total_sum = matching_rows["Betrag (€)"].sum()
        summary_row = { "Buchungsdatum":[matching_rows["Buchungsdatum"].iloc[0]],
                       "Wertstellung": [matching_rows["Wertstellung"].iloc[0]],
                       "Status": [matching_rows["Status"].iloc[0]],
                       "Zahlungspflichtige*r":[""],
                       "Zahlungsempfänger*in":[""],
                       "Verwendungszweck": ["Ausgleich Verrechnet"],
                       "Umsatztyp":["Zusammenfassung"],
                       "IBAN":[""],
                       "Betrag (€)":[total_sum],
                       "Gläubiger-ID":[""],
                       "Mandatsreferenz":[""],
                       "Kundenreferenz":[""],
                       "Kategorie":["sonstiges"]}
        summary_row = pd.DataFrame(summary_row)
        df = df[~mask]
        df = pd.concat([df, summary_row], ignore_index=True)
        return df