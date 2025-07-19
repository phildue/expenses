import argparse
from classifier import Classifier
from plot import Plot
import os
import yaml

def main():
    parser = argparse.ArgumentParser(description="Classify transactions and plot results.")
    parser.add_argument("input_file", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output directory or file", default=".")
    args = parser.parse_args()
    
    os.makedirs(args.output_path, exist_ok=True)
    classified_transactions = os.path.join(args.output_path, "classified_transactions.csv")
    # Assuming Classifier and Plot are imported or defined above
    with open("config/categories.yaml", "r") as f:
        categories = yaml.safe_load(f)
    categories = categories.get("Categories", {})
    classifier = Classifier(categories=categories)
    classifier.classify_file(args.input_file, classified_transactions)  # or whatever method triggers classification

    plotter = Plot(csv_file=classified_transactions)
    output_plot = os.path.join(args.output_path, "expenses.jpg")
    plotter.save_plot(output_file=output_plot)  # or whatever method creates the plot

if __name__ == "__main__":
    main()
