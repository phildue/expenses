import argparse
from classifier import Classifier
from plot import Plot
import os
import yaml
import glob

def main():
    parser = argparse.ArgumentParser(description="Classify transactions and plot results.")
    parser.add_argument("input_folder", help="Path to input folder containing CSV files")
    parser.add_argument("output_path", help="Path to output directory", default=".")
    args = parser.parse_args()
    
    os.makedirs(args.output_path, exist_ok=True)
    with open("config/categories.yaml", "r") as f:
        categories = yaml.safe_load(f)
    categories = categories.get("Categories", {})
    classifier = Classifier(categories=categories)

    csv_files = glob.glob(os.path.join(args.input_folder, "*.csv"))
    for csv_file in csv_files:
        base_name = os.path.splitext(os.path.basename(csv_file))[0]
        classified_file = os.path.join(args.output_path, f"{base_name}_classified.csv")
        classifier.classify_file(csv_file, classified_file)

        plotter = Plot(csv_file=classified_file)
        output_plot = os.path.join(args.output_path, f"{base_name}_expenses.jpg")
        plotter.save_plot(output_file=output_plot)

if __name__ == "__main__":
    main()
