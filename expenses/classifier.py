from openai import OpenAI
import os
import yaml
import csv
import pandas as pd
import argparse
import glob


class Classifier:
    def __init__(self, categories):
        self.categories = categories
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def classify(self, text):
        text_lower = text.lower()
        max_overlap = 0
        best_category = None

        for category, info in self.categories.items():
            keywords = info.get("keywords", [])
            overlap = sum(1 for kw in keywords if kw.lower() in text_lower)
            if overlap > max_overlap:
                max_overlap = overlap
                best_category = category

        if best_category is not None and max_overlap > 0:
            return best_category
        else:
            print(f"No category found with keyword overlap for text: '{text}'")
            return "sonstiges"
    
    def classify_file(self, input_file, output_file):
        try:
            df = pd.read_csv(input_file, delimiter=';', encoding='utf-8')
        except Exception as e:
            df = pd.read_csv(input_file, delimiter=';', encoding='utf-8', skiprows=4)
        # Drop rows with any missing values in the selected columns
        #df = df.dropna()
        #df = df[~df['Zahlungsempfänger*in'].isin(['Julia Sperger', 'Philipp Dürnay'])]
        categories = []
        for _, row in df.iterrows():
            if any(column not in row for column in ['Zahlungsempfänger*in', 'Verwendungszweck']):
                categories.append(None)
                continue
            line_text = " ".join(str(item) for item in row[["Zahlungsempfänger*in", 'Verwendungszweck']])
            try:
                category = self.classify(line_text)
                categories.append(category)
            except ValueError as e:
                print(e)
                categories.append(None)
        df['Kategorie'] = categories
        df.to_csv(output_file, index=False, encoding='utf-8', sep=';')
        
    def convert_betrag_column(self, df):
        """Convert 'Betrag (€)' column from German to standard decimal notation."""
        if 'Betrag (€)' in df.columns:
            df['Betrag (€)'] = (
                df['Betrag (€)']
                .str.replace('.', '', regex=False)   # Remove thousand separator
                .str.replace(',', '.', regex=False)  # Replace decimal comma with dot
            )
            df['Betrag (€)'] = pd.to_numeric(df['Betrag (€)'], errors='coerce')
        return df


def main():
    parser = argparse.ArgumentParser(description="Classify transactions and plot results.")
    parser.add_argument("input_folder", help="Path to input folder containing CSV files")
    parser.add_argument("output_path", help="Path to output directory", default=".")
    args = parser.parse_args()
    
    os.makedirs(args.output_path, exist_ok=True)
    with open("config/categories.yaml", "r") as f:
        categories_yaml = yaml.safe_load(f)
    categories_list = categories_yaml.get("Categories", [])
    # Convert list of dicts to dict with category name as key
    categories = {cat["name"]: {"keywords": cat["keywords"]} for cat in categories_list}
    classifier = Classifier(categories=categories)

    csv_files = glob.glob(os.path.join(args.input_folder, "*.csv"))
    for csv_file in csv_files:
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        classified_file = os.path.join(args.output_path, f"{base_name}_classified.csv")
        print(f"Classifying {csv_file} and saving to {classified_file}")
        classifier.classify_file(csv_file, classified_file)


if __name__ == "__main__":
    main()
