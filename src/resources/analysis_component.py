import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import pickle
import subprocess
import sys
# To import packages from it
app_resources_folder = os.path.join(os.path.dirname(__file__), 'resources')
sys.path.append(app_resources_folder)
from ASV_summary import calculate_stats


def display_content(*args):
    action = selected_action.get()
    sample = selected_sample.get()
    plot_type = selected_plot_type.get()
    taxa_level = selected_taxa_level.get()

    if action == "Plotting":
        if plot_type != "Plot Type" and sample != "Samples Taxonomies" and taxa_level != "Taxonomy Level":
            # Perform plotting based on plot type
            if plot_type == "bar plot":
                plot_bar(sample, taxa_level)
            elif plot_type == "pie plot":
                plot_pie(sample, taxa_level)
        else:
            pass
    elif action == "PDF Report":
        if sample != "Samples Taxonomies":
            generate_pdf(sample)
        else:
            pass

def plot_bar(sample, taxa_level):
    taxa_level = taxa_level.lower()
    bar_script_path = os.path.join(os.path.dirname(__file__), "bar_plotting.py")
    # Generate bar chart that will be saved in post_analysis_results folder inside mounted directory
    subprocess.run(["python", bar_script_path, taxa_files[sample], taxa_level])
    # Display bar chart
    img_path = os.path.join(mounted_dir, "post_analysis_results", sample.replace(".taxa.txt", f"_{taxa_level}.bar.png"))
    display_image(img_path, sample)

def plot_pie(sample, taxa_level):
    taxa_level = taxa_level.lower()
    pie_script_path = os.path.join(os.path.dirname(__file__), "pie_plotting.py")
    # Generate pie chart that will be saved in post_analysis_results folder inside mounted directory
    subprocess.run(["python", pie_script_path, taxa_files[sample], taxa_level])
    # Display pie chart
    img_path = os.path.join(mounted_dir, "post_analysis_results", sample.replace(".taxa.txt", f"_{taxa_level}.pie.png"))
    display_image(img_path, sample)

def generate_pdf(sample):
    pdf_script_path = os.path.join(os.path.dirname(__file__), "pdf_report.py")
    # Generate PDF report 
    print("Generating PDF report for", sample)
    assigned_taxa_file = taxa_files[sample]
    unassigned_fasta_file = taxa_files[sample].replace(".taxa.txt", ".unassigned.fa")
    pdf_path = os.path.join(mounted_dir, "post_analysis_results")
    subprocess.run(["python", pdf_script_path, assigned_taxa_file, unassigned_fasta_file])
    # Show a message for the successful completion of PDF generation 
    messagebox.showinfo("Success", "PDF report downloaded successfully for {} in {}".format(sample, pdf_path))

def display_image(image_path, sample):
    if image_path:
        image = Image.open(image_path)
        # Set dimensions for image based on window size
        window_height = window.winfo_height()
        img_width, img_height = image.size
        new_height = min(window_height // 2, img_height)
        new_width = int(new_height / img_height * img_width)
        # Convert resized image to a Tkinter PhotoImage object
        img = ImageTk.PhotoImage(image)
        
        # Clear canvas
        canvas.delete("all")
        
        # Calculate position to center image in canvas
        canvas_width = canvas.winfo_width()
        x = (canvas_width - new_width) // 2
        # Display image on canvas
        canvas.create_image(x, 0, anchor=tk.NW, image=img)
        # Store reference to image to prevent garbage collection before it is displayed on the canvas
        canvas.img = img
        
        # ASVs track statistical summary
        assigned_taxa_file = taxa_files[sample]
        unassigned_fasta_file = taxa_files[sample].replace(".taxa.txt", ".unassigned.fa")
        assigned_count, assigned_percentage, unassigned_count, unassigned_percentage = calculate_stats(assigned_taxa_file, unassigned_fasta_file)
        text_label.config(text=f"Assigned ASVs: count={assigned_count}, percentage={round(assigned_percentage, 2)}\n\nUnassigned ASVs: count={unassigned_count}, percentage={round(unassigned_percentage, 2)}") 
    else:
        # Clear the canvas and text label if the selected option does not have an image path
        canvas.delete("all")
        text_label.config(text="")
        

def on_frame_configure(event):
    canvas.config(scrollregion=canvas.bbox("all"))


window = tk.Tk()
window.geometry("1200x1000")  # Window size
window.title("Downstream analysis window")

# Frame for dropdowns
dropdown_frame = tk.Frame(window)
dropdown_frame.pack(fill=tk.X)

# Dropdown for actions
action_options = ["Action", "Plotting", "PDF Report"]  # Removed "Table Summary"
selected_action = tk.StringVar()
selected_action.set(action_options[0])  # Default action
action_dropdown = tk.OptionMenu(dropdown_frame, selected_action, *action_options, command=display_content)
action_dropdown.pack(side=tk.LEFT, padx=5, pady=10)

# Dropdown for sample files fetched from a directory
mounted_dir_pickle_path = os.path.join(os.path.dirname(__file__), 'mounted_dir.pickle')
with open(mounted_dir_pickle_path, 'rb') as handle:
    mounted_dir = pickle.load(handle)["mount_dir"]

print("-"*30)
print("Mount dir:")
print(mounted_dir)
print("-"*30)

taxa_path = os.path.join(mounted_dir, "vsearch_result")
taxa_files = {file: os.path.join(taxa_path, file) for file in os.listdir(taxa_path) if ".taxa.txt" in file}
samples_list = ["Samples Taxonomies"] + list(taxa_files.keys())
selected_sample = tk.StringVar()
selected_sample.set(samples_list[0])  # Default sample
sample_dropdown = tk.OptionMenu(dropdown_frame, selected_sample, *samples_list, command=display_content)
sample_dropdown.pack(side=tk.LEFT, padx=5, pady=10)

# Dropdown for taxonomy level
taxa_level_options = ["Taxonomy Level", "Genus", "Species"]
selected_taxa_level = tk.StringVar()
selected_taxa_level.set(taxa_level_options[0])  # Default taxonomy type
taxa_level_dropdown = tk.OptionMenu(dropdown_frame, selected_taxa_level, *taxa_level_options, command=display_content)
taxa_level_dropdown.pack(side=tk.LEFT, padx=5, pady=10)

# Dropdown for plot type
plot_type_options = ["Plot Type", "bar plot", "pie plot"]
selected_plot_type = tk.StringVar()
selected_plot_type.set(plot_type_options[0])  # Default plot type
plot_type_dropdown = tk.OptionMenu(dropdown_frame, selected_plot_type, *plot_type_options, command=display_content)
plot_type_dropdown.pack(side=tk.LEFT, padx=5, pady=10)

canvas = tk.Canvas(window)
canvas.pack(fill=tk.BOTH, expand=True)
window.bind("<Configure>", on_frame_configure)

# Label to display ASVs track statistical summary underneath the image
text_label = tk.Label(window, text="", font=("Helvetica", 14), wraplength=800)
text_label.pack(pady=10)

window.mainloop()
