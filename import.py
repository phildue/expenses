import os
import argparse
import sys
import glob
import yaml
from datetime import datetime

from expenses.classifier import Classifier

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
