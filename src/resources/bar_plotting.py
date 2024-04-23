import matplotlib.pyplot as plt
import argparse
import os


def generate_bar_chart(taxa_file, taxa_level):
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
                
    # Sort the species data based on accumulated size in descending order
    sorted_level_data = sorted(level_data.items(), key=lambda x: x[1], reverse=True)

    # Extract top 15 species, accumulated sizes, and percentages
    top_taxa = [entry[0] for entry in sorted_level_data[:15]]
    top_sizes = [entry[1] for entry in sorted_level_data[:15]]
    top_percentages = [(size / total_size) * 100 for size in top_sizes]

    # Plot the bar chart for top 15 species
    plt.figure(figsize=(12, 8))
    barplot = plt.bar(top_taxa, top_sizes, color='skyblue')

    # Add percentages as text on top of the bars
    for i, percentage in enumerate(top_percentages):
        plt.text(barplot[i].get_x() + barplot[i].get_width() / 2, barplot[i].get_height() + 5,
                f"{percentage:.2f}%", ha='center')
        
    plt.xlabel(taxa_level)
    plt.ylabel('Abundance')
    plt.title(f'Top 15 {taxa_level} vs Abundance for {os.path.basename(taxa_file)}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    img_name = taxa_file.split("vsearch_result/")[1].replace(".taxa.txt", f"_{taxa_level}.bar.png")
    img_dir = os.path.join(taxa_file.split("vsearch_result/")[0], "post_analysis_results")
    os.makedirs(img_dir, exist_ok=True)
    img_path = os.path.join(img_dir, img_name)
    plt.savefig(img_path)
    return img_path



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
    img_path = generate_bar_chart(taxa_file, taxa_level)