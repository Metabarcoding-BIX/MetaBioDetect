import matplotlib.pyplot as plt
import fpdf.fpdf as fpdf
import os
from bar_plotting import generate_bar_chart
import argparse
import sys
# To import packages from it
app_resources_folder = os.path.join(os.path.dirname(__file__), 'resources')
sys.path.append(app_resources_folder)
from ASV_summary import calculate_stats


def read_assigned_species(filename):
    """Function to read assigned species names and their sizes."""
    total_size = 0
    species_data = {}
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split("\t")
            if len(parts) >= 2:
                species_name = parts[1].split("_")[0]
                size = int(parts[0].split(";")[1].split("=")[1])
                if species_name not in species_data:
                    species_data[species_name] = size
                else:
                    species_data[species_name] += size
                total_size += size
                
    # Sort species by abundance (size) in descending order
    sorted_species_data = sorted(species_data.items(), key=lambda x: x[1], reverse=True)
    return sorted_species_data, total_size

# Function to generate species table
def generate_species_table(species_data):
    table_content = [["Species", "Abundance (count)"]]
    for species, abundance in species_data:
        table_content.append([species, f"{abundance:.2f}"])
    return table_content

class PDF(fpdf.FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'MetaBioDetect Analysis Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', '', 14)
        self.cell(0, 10, title, 0, 1, 'C')
    
    def chapter_body(self, body):
        self.set_font('Arial', 'B', 12)
        self.multi_cell(0, 5, body)
        self.ln()
        
    def chapter_table(self, table):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 5, table)
        self.ln()
        
    def stat_summary(self, summary):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, summary)
        self.ln()
        
    def footer(self):
        footnote1 = "*In the context of sequence analysis, 'abundance' refers to the number of times a particular sequence (e.g., a unique read or OTU) appears in a dataset."
        footnote2 = "This can be thought of as the frequency or count of a sequence within a sample or a set of samples."
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        # Select Arial italic 8
        self.set_font('Arial', 'I', 8)
        # Print centered page number
        self.cell(0, 5, footnote1, 0, 0, 'L')
        self.cell(-63, 10, footnote2, 0, 0, 'R')


def generate_report(assigned_taxa_file, unassigned_fasta_file):
    # Calculate statistics
    assigned_count, assigned_percentage, unassigned_count, unassigned_percentage = calculate_stats(assigned_taxa_file, unassigned_fasta_file)

    taxa_level_plot_paths = {"genus": "", "species": ""}
    for level in taxa_level_plot_paths.keys():
        img_path = generate_bar_chart(assigned_taxa_file, level)
        taxa_level_plot_paths[level] = img_path
    
    # List the assigned taxonomies with abundance
    sorted_species_data, total_size = read_assigned_species(assigned_taxa_file)
    
    # Generate species table
    table_data = generate_species_table(sorted_species_data)

    # Prompt user to enter the desired location and name for saving the PDF report
    mounted_dir = assigned_taxa_file.split("vsearch_result/")[0]
    sample_name = assigned_taxa_file.split("vsearch_result/")[1].replace(".taxa.txt", ".report.pdf")
    pdf_parent_dir = os.path.join(mounted_dir, "post_analysis_results")
    pdf_full_path = os.path.join(pdf_parent_dir, sample_name)

    # Create a PDF report
    pdf = PDF()
    pdf.add_page()

    # Add content to PDF
    pdf.stat_summary(f"Analysis Report for {os.path.basename(assigned_taxa_file)}")
    pdf.cell(0, 10, f"Assigned ASVs: {assigned_count}, percentage: {assigned_percentage:.2f}%")
    pdf.ln()
    pdf.cell(0, 10, f"Unassigned ASVs: {unassigned_count}, percentage: {unassigned_percentage:.2f}%")
    pdf.ln()

    # Add bar plots as images to PDF
    pdf.chapter_body("Top 15 Genus vs Abundance")
    pdf.chapter_table("Below is the bar plot showing the top 15 genera present in the given sample based on abundance*.")
    pdf.image(taxa_level_plot_paths["genus"], x = 10, y = None, w = 190, h = 140)
    pdf.ln(100)

    pdf.chapter_body("Top 15 Species vs Abundance")
    pdf.chapter_table("Below is the bar plot showing the top 15 species present in the given sample based on abundance*.")
    pdf.image(taxa_level_plot_paths["species"], x = 10, y = None, w = 190, h = 160)
    pdf.ln(100)

    # Add species table to PDF
    pdf.chapter_body("Species Abundance Table")
    pdf.set_font("Arial", size=12)
    pdf.cell(100, 10, "Species", 1)
    pdf.cell(40, 10, "Abundance (count)", 1)
    pdf.cell(40, 10, "Abundance (%)", 1)
    pdf.ln()
    for species, abundance in sorted_species_data:
        percentage = (abundance / total_size) * 100
        pdf.cell(100, 10, species, 1)
        pdf.cell(40, 10, str(abundance), 1)
        pdf.cell(40, 10, f"{percentage:.2f}%", 1)
        pdf.ln()

        
    pdf.footer()
    
    # Save the PDF
    pdf.output(pdf_full_path)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("assigned_taxa_file", help="")
    parser.add_argument("unassigned_fasta_file", help="")
    args = parser.parse_args()
    
    assigned_taxa_file = args.assigned_taxa_file
    unassigned_fasta_file = args.unassigned_fasta_file
    
    generate_report(assigned_taxa_file, unassigned_fasta_file)














