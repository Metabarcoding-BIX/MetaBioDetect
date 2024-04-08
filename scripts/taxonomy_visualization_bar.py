import matplotlib.pyplot as plt

# Read the result text file and parse the data
species_data = {}

total_size = 0  # Variable to store the total size of all species

with open("C:/Users/hp/Desktop/grp3 gp/plantaligndb/honey4_97.txt", "r") as file:
    for line in file:
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            species_name = parts[1]
            size = int(parts[0].split(";")[1].split("=")[1])
            if species_name not in species_data:
                species_data[species_name] = 0
            species_data[species_name] += size
            total_size += size

# Sort the species data based on accumulated size in descending order
sorted_species_data = sorted(species_data.items(), key=lambda x: x[1], reverse=True)

# Extract top 15 species, accumulated sizes, and percentages
top_species = [entry[0] for entry in sorted_species_data[:15]]
top_sizes = [entry[1] for entry in sorted_species_data[:15]]
top_percentages = [(size / total_size) * 100 for size in top_sizes]

# Plot the bar chart for top 15 species
plt.figure(figsize=(12, 8))
barplot = plt.bar(top_species, top_sizes, color='skyblue')

# Add percentages as text on top of the bars
for i, percentage in enumerate(top_percentages):
    plt.text(barplot[i].get_x() + barplot[i].get_width() / 2, barplot[i].get_height() + 5,
             f"{percentage:.2f}%", ha='center')

plt.xlabel('Species')
plt.ylabel('Accumulated Size')
plt.title('Top 15 Species vs Accumulated Size for Honey sample 4 using plantalign db')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better visibility
plt.tight_layout()  # Adjust layout to prevent labels from getting clipped
plt.show()