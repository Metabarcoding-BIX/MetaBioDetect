import matplotlib.pyplot as plt

# Read the result text file and parse the data
data = []
with open("C:/Users/hp/Desktop/grp3 gp/plantaligndb/honey1_97.txt", "r") as file:
    for line in file:
        parts = line.strip().split("\t")
        if len(parts) >= 2:
            asv_size = parts[0].split(";")
            species_name = parts[1].split("_")[0]
            if len(asv_size) >= 2:
                size = int(asv_size[1].split("=")[1])
                data.append((species_name, size))
        else:
            print("Skipping line:", line.strip())

# Sort the data based on size in descending order and select top 15
sorted_data = sorted(data, key=lambda x: x[1], reverse=True)[:15]

# Extract species and sizes
species = [entry[0] for entry in sorted_data]
sizes = [entry[1] for entry in sorted_data]

# Plot the pie chart
plt.figure(figsize=(10, 6))
plt.pie(sizes, labels=species, autopct='%1.1f%%', startangle=140)
plt.title('Top 15 Species by Size')
plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
plt.show()