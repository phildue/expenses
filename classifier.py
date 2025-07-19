from openai import OpenAI
import os
import yaml
import csv
import pandas as pd
import matplotlib.pyplot as plt

class Classifier:
    def __init__(self, categories):
        self.categories = categories
        self.client = OpenAI(
            # This is the default and can be omitted
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def classify(self, text):
        prompt = (
            f"Given the following categories: {list(self.categories)}, "
            f"and the text: '{text}', which category does the text belong to? "
            "Respond with only the category name."
        )

        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=10,
            n=1,
            stop=None,
            temperature=0
        )

        category = response.choices[0].message.content.strip().lower()
        if category in self.categories:
            return category
        else:
            raise ValueError(f"Category '{category}' not found in predefined categories: {list(self.categories)}")
    
    def classify_file(self, input_file, output_file):
        df = pd.read_csv(input_file, delimiter='\t', encoding='utf-8')
        categories = []
        for _, row in df.iterrows():
            line_text = " ".join(str(item) for item in row[["Zahlungsempfänger*in", 'Verwendungszweck']])
            try:
                category = self.classify(line_text)
                categories.append(category)
            except ValueError as e:
                print(e)
                categories.append(None)
        df['Kategorie'] = categories
        df.to_csv(output_file, index=False, encoding='utf-8')
        
if __name__ == "__main__":
    # Example usage
    with open("categories.yaml", "r") as f:
        categories = yaml.safe_load(f)
    categories = categories.get("Categories", {})
    classifier = Classifier(categories)
    classifier.classify_file("test.csv", "test_output.csv")