import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend for file output
import matplotlib.pyplot as plt

class Plot:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.data = pd.read_csv(csv_file)

    def plot(self):
        df = self.data[self.data['Betrag (€)'] < 0].copy()
        df['Betrag (€)'] = df['Betrag (€)'].abs()
        category_sums = df.groupby('Kategorie')['Betrag (€)'].sum()
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct * total / 100.0))
                return f'{val} €'
            return my_autopct
        return category_sums.plot.pie(autopct=make_autopct(category_sums), figsize=(8, 8), ylabel='')
    
    def show_plot(self):
        ax = self.plot()
        plt.title('Total Amount per Category')
        plt.show()

    def save_plot(self, output_file):
        ax = self.plot()
        plt.title('Total Amount per Category')
        plt.savefig(output_file)
        plt.close()
        
        
if __name__ == "__main__":
    plotter = Plot("test_output.csv")
    plotter.show_plot()
    # To save the plot, uncomment the next line
    # plotter.save_plot("category_distribution.png")