import matplotlib.pyplot as plt
import argparse
import os


def generate_pie_chart(taxa_file, taxa_level):
    # Read the result text file and parse the data
    level_data = {}

    total_size = 0  # Variable to store the total size of all species

    with open(taxa_file, "r") as file:
        for line in file:
            parts = line.strip().split("\t")  # example: ['ASV279;size=1', 'Lomelosia-cretica_154147382', '+', '98.1']
            if len(parts) >= 2:
                # species_name = parts[1]
                taxa_name = parts[1]  # example: 'Lomelosia-cretica_154147382'
                if taxa_level.lower() == "genus":
                    taxa_name = parts[1].split("_")[0].split("-")[0]
                size = int(parts[0].split(";")[1].split("=")[1])
                if taxa_name not in level_data:
                    level_data[taxa_name] = 0
                level_data[taxa_name] += size
                total_size += size
    
    
    # Sort the data based on size in descending order and select top 15
    sorted_level_data = sorted(level_data.items(), key=lambda x: x[1], reverse=True)[:15]

    # Extract species and sizes
    top_taxa = [entry[0] for entry in sorted_level_data[:15]]
    top_sizes = [entry[1] for entry in sorted_level_data[:15]]

    # Calculate percentages
    percentages = [(size / total_size) * 100 for size in top_sizes]

    # Plot the pie chart
    plt.figure(figsize=(10, 6))
    patches, _ = plt.pie(top_sizes, startangle=140)

    # Add legend with species names and percentages
    taxa_legends = [taxa.split("_")[0] for taxa in top_taxa]
    labels = [f"{s} - {p:.1f}%" for s, p in zip(taxa_legends, percentages)]
    plt.legend(patches, labels, title="Taxa - Percentage", fontsize=10, loc='upper left', bbox_to_anchor=(1.15, 0.5))

    plt.title(f'Top 15 {taxa_level} vs Abundance for {os.path.basename(taxa_file)}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    img_name = taxa_file.split("vsearch_result/")[1].replace(".taxa.txt", f"_{taxa_level}.pie.png")
    img_dir = os.path.join(taxa_file.split("vsearch_result/")[0], "post_analysis_results")
    os.makedirs(img_dir, exist_ok=True)
    plt.savefig(os.path.join(img_dir, img_name))



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("taxa_file", help="")
    parser.add_argument("taxa_level", help="")
    args = parser.parse_args()
    
    taxa_file = args.taxa_file
    taxa_level = args.taxa_level
    print("-"*30)
    print(taxa_file)
    print("-"*30)
    generate_pie_chart(taxa_file, taxa_level)