import json
import argparse
import matplotlib.pyplot as plt
import pandas as pd

def load_results(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def plot_category_distribution(results, output_file=None):
    df = pd.DataFrame(results)
    counts = df["category"].value_counts()

    # Plot bar chart
    counts.plot(kind="bar", color=["#4CAF50", "#FF5722", "#2196F3"])
    plt.title("Bias Evaluation Results by Category")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    if output_file:
        plt.savefig(output_file)
        print(f"Saved chart to {output_file}")
    else:
        plt.show()

def main():
    parser = argparse.ArgumentParser(description="Visualise bias evaluation results from JSON")
    parser.add_argument("input_file", type=str, help="Path to JSON results file")
    parser.add_argument("--output", type=str, default=None, help="Optional path to save chart as PNG")
    args = parser.parse_args()

    results = load_results(args.input_file)
    plot_category_distribution(results, args.output)

if __name__ == "__main__":
    main()
