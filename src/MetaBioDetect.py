import tkinter as tk
from tkinter import *
from tkinter import filedialog, font
import pickle
import os
import docker
import subprocess
import matplotlib.pyplot as plt
from tkinter import messagebox  
import fpdf
import sys
# To import packages from it
app_resources_folder = os.path.join(os.path.dirname(__file__), 'resources')
sys.path.append(app_resources_folder)
from utils import CreateToolTip


mount_dir = ""

#creating main GUI shell
window = tk.Tk() #can also define size with .geometry without use of frame
frame = tk.Frame(master=window, width=1200, height=600)
window.title("MetaBioDetect")
frame.pack()


def calculate_pair_func(file):
    file_prefix = (file[0:file.index(".fq.gz")])
    if file_prefix.endswith('1'):
        complement = file_prefix[:-1] + "2.fq.gz"
    elif file_prefix.endswith('2'):
        complement = file_prefix[:-1] + "1.fq.gz"
    else:
        print("file should end with 1 or 2")
        #return an error 
    return complement


#function for loading files and storing filepath and names for pipeline
def load_files_func():
    pairs_list = []
    complements = set()
    #clearing text display everytime files are opened
    files_text_display.delete('1.0', END)
    loaded_files = filedialog.askopenfilenames()
    # Extract the parent folder to mount inside docker image
    global mount_dir
    mount_dir = os.path.dirname(loaded_files[0])
    print("-"*30)
    print("mount directory")
    print(mount_dir)
    
    mounted_dir_pickle_path = os.path.join(os.path.dirname(__file__), 'resources', 'mounted_dir.pickle')
    # Save mounted directory to pickle file 
    save_dict = {"mount_dir": mount_dir}
    with open(mounted_dir_pickle_path, 'wb') as handle:
        pickle.dump(save_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # Use the files path without parent directory for compatability with the image 
    loaded_files = [file.replace(mount_dir, "") for file in loaded_files if file.endswith(".fq.gz")]
    loaded_files = tuple(loaded_files)
    
    # Displaying loaded files in progress area
    files_text_display.insert(END, "Loaded Files:\n")
    files_text_display.insert(END, ("\n").join(loaded_files) + "\n")
    files_text_display.see(END)

    for i in loaded_files:
        complement = calculate_pair_func(i)
        if complement in complements or i in complements:
            if i < complement:
                pairs_list.append(i +','+ complement)
            elif complement < i:
                pairs_list.append(complement +','+ i)
        else:
            complements.add(complement)   
    
    # Write ordered input files within the directory to be mounted
    file_content = "\n".join(pairs_list) + "\n" # join records with newlines and add extra newline at the end, so last record get read in bash
    with open(f"{mount_dir}/filenames.txt", "w") as f:
        f.write(file_content)



def reverse_complement(seq):
    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A'}
    return ''.join(complement[base] for base in reversed(seq))

def seq_pairs(forward_read, reverse_read):
    forward_rc = reverse_complement(forward_read)
    reverse_rc = reverse_complement(reverse_read)
    return forward_read, reverse_rc, reverse_read, forward_rc



#function to open second window for visualisation 
def open_analysis_window_func():
    analysis_comp_script_path = os.path.join(os.path.dirname(__file__), 'resources', 'analysis_component.py')
    subprocess.run(["python", analysis_comp_script_path])



def catch_docker_error(docker_out):
    if docker_out.exit_code:
        error_msg = docker_out.output[1].decode('utf-8')
        raise Exception(END, f"Analysis Failed with the following exception: {error_msg}")
    else:
        print(docker_out.output[0].decode('utf-8'))

def adapter_trim_func(container):
    container.exec_run('chmod +x /app/adapter_trimming.sh')
    if adapt_discard_untrim == "Yes":
        adapter_trim_output = container.exec_run(f'/app/adapter_trimming.sh --a={adapt_for_read} --A={adapt_rev_read} --minimum-length={adapt_min_length} --quality-cutoff={adapt_qual_cutoff} --max-n={adapt_maxn} --overlap={adapt_overlap} --error-rate={adapt_error_rate} --discard-untrimmed=1',
                                        demux=True)
        catch_docker_error(adapter_trim_output)
    else:
        adapter_trim_output = container.exec_run(f'/app/adapter_trimming.sh --a={adapt_for_read} --A={adapt_rev_read} --minimum-length={adapt_min_length} --quality-cutoff={adapt_qual_cutoff} --max-n={adapt_maxn} --overlap={adapt_overlap} --error-rate={adapt_error_rate}',
                                        demux=True)
        catch_docker_error(adapter_trim_output)
        
        
def primer_trim_func(container):
    container.exec_run('chmod +x /app/primer_trimming.sh')
    if prime_discard_untrim == "Yes":
        primer_trim_output = container.exec_run(f'/app/primer_trimming.sh --a={prime_for_read} --A={prime_rev_read} --minimum-length={prime_min_length} --quality-cutoff={prime_qual_cutoff} --max-n={prime_maxn} --overlap={prime_overlap} --error-rate={prime_error_rate} --discard-untrimmed=1',
                                            demux=True)
        catch_docker_error(primer_trim_output)
    else:
        primer_trim_output = container.exec_run(f'/app/primer_trimming.sh --a={prime_for_read} --A={prime_rev_read} --minimum-length={prime_min_length} --quality-cutoff={prime_qual_cutoff} --max-n={prime_maxn} --overlap={prime_overlap} --error-rate={prime_error_rate}',
                                            demux=True)
        catch_docker_error(primer_trim_output)
    
def merging_paired_end_func(container):
    container.exec_run('chmod +x /app/merge_pair_end.sh', demux=True)
    vsearch_step1_output = container.exec_run('/app/merge_pair_end.sh', demux=True)
    catch_docker_error(vsearch_step1_output)
    
def quality_filtering_func(container):
    container.exec_run('chmod +x /app/quality_filtering.sh', demux=True)
    vsearch_step2_output = container.exec_run(f'/app/quality_filtering.sh --fastq_maxee={fastq_maxee}', demux=True)
    catch_docker_error(vsearch_step2_output)
    
def identifying_unique_seq_func(container):
    container.exec_run('chmod +x /app/identifying_unique_seq.sh', demux=True)
    vsearch_step3_output = container.exec_run('/app/identifying_unique_seq.sh', demux=True)
    catch_docker_error(vsearch_step3_output)
    
def detecting_asvs_func(container):
    container.exec_run('chmod +x /app/detect_ASVs.sh', demux=True)
    vsearch_step4_output = container.exec_run('/app/detect_ASVs.sh', demux=True)
    catch_docker_error(vsearch_step4_output)
    
def removing_chimera_func(container):
    container.exec_run('chmod +x /app/chimera_removal.sh', demux=True)
    vsearch_step5_output = container.exec_run('/app/chimera_removal.sh', demux=True)
    catch_docker_error(vsearch_step5_output)
    
def taxonomy_assignment_func(container):
    container.exec_run('chmod +x /app/taxonomy_assignment.sh', demux=True)
    vsearch_step6_output = container.exec_run(f'/app/taxonomy_assignment.sh --db={vser_db} --id={vsearch_id}', demux=True)
    catch_docker_error(vsearch_step6_output)
    
    

def pipeline_func():
    try:
        # Initialize docker client
        client = docker.from_env(timeout=1200)
        image_path = os.path.join(os.path.dirname(__file__), 'resources', 'MetaBioDetect_img.tar')


        # Load the image into docker
        with open(image_path, 'rb') as f:
            client.images.load(f.read())
        loaded_image = client.images.list()[0]
        
        # Run the docker image with the mounted directory 
        print(loaded_image.id)
        container = client.containers.run(loaded_image.id, detach=True, tty=True, volumes={mount_dir: {'bind': '/app/uploads', 'mode': 'rw'}}, command="/bin/bash")

        
        #if statement to say no files loaded in fun with no files
        files_text_display.insert(END,"Analysis Started ...\n\n")
        files_text_display.see(END)
        # Execute commands within the doecker image
        trim_dir = os.path.join(mount_dir, "trimmed_reads")
        vsearch_dir = os.path.join(mount_dir, "vsearch_result")
        # 1. Adapter trimming 
        if adapt_trimming:
            # Display progress (frontend)
            files_text_display.insert(END, "Adapter Trimming Started ...\n\n")
            window.after(5000, adapter_trim_func(container))
            files_text_display.see(END)
            adapter_trim_log_dir = os.listdir(os.path.join(mount_dir, "trimmed_reads"))
            adapter_trim_log = [os.path.join(trim_dir, file) for file in adapter_trim_log_dir if ".adapter_trim.log.txt" in file][0]
            with open(adapter_trim_log, "r") as fr:
                files_text_display.insert(END, fr.read())
                files_text_display.insert(END, "-"*80)
            files_text_display.see(END)
        
        # 2. Primer trimming
        if prime_trimming:
            # Display progress (frontend)
            files_text_display.insert(END, "\nPrimer Trimming Started ...\n\n")
            window.after(5000, primer_trim_func(container))
            files_text_display.see(END)
            primer_trim_log_dir = os.listdir(os.path.join(mount_dir, "trimmed_reads"))
            primer_trim_log = [os.path.join(trim_dir, file) for file in primer_trim_log_dir if ".primer_trim.log.txt" in file][0]
            with open(primer_trim_log, "r") as fr:
                files_text_display.insert(END, fr.read())
                files_text_display.insert(END, "-"*80)
            files_text_display.see(END)
        
        # 3. Vsearch
        # Display progress (frontend)
        files_text_display.insert(END, "\nMerging Paired-end Started ...\n\n")
        window.after(5000, merging_paired_end_func(container))
        files_text_display.see(END)
        merging_log_dir = os.listdir(os.path.join(mount_dir, "vsearch_result"))
        merging_log = [os.path.join(vsearch_dir, file) for file in merging_log_dir if ".merged.log.txt" in file][0]
        with open(merging_log, "r") as fr:
            files_text_display.insert(END, fr.read())
            files_text_display.insert(END, "-"*80)
        files_text_display.see(END)
        
        files_text_display.insert(END, "\nQuality Filtering Started ...\n\n")
        window.after(5000, quality_filtering_func(container))
        files_text_display.see(END)
        quality_filtering_log_dir = os.listdir(os.path.join(mount_dir, "vsearch_result"))
        quality_filtering_log = [os.path.join(vsearch_dir, file) for file in quality_filtering_log_dir if ".filtered.log.txt" in file][0]
        with open(quality_filtering_log, "r") as fr:
            files_text_display.insert(END, fr.read())
            files_text_display.insert(END, "-"*80)
        files_text_display.see(END)
        
        files_text_display.insert(END, "\nIdentifying Unique Sequences Started ...\n\n")
        window.after(5000, identifying_unique_seq_func(container))
        files_text_display.see(END)
        unique_seq_log_dir = os.listdir(os.path.join(mount_dir, "vsearch_result"))
        unique_seq_log = [os.path.join(vsearch_dir, file) for file in unique_seq_log_dir if ".uniques.log.txt" in file][0]
        with open(unique_seq_log, "r") as fr:
            files_text_display.insert(END, fr.read())
            files_text_display.insert(END, "-"*80)
        files_text_display.see(END)
        
        files_text_display.insert(END, "\nDetecting ASVs Started ...\n\n")
        window.after(5000, detecting_asvs_func(container))
        files_text_display.see(END)
        asv_log_dir = os.listdir(os.path.join(mount_dir, "vsearch_result"))
        asv_log = [os.path.join(vsearch_dir, file) for file in asv_log_dir if ".asvs.log.txt" in file][0]
        with open(asv_log, "r") as fr:
            files_text_display.insert(END, fr.read())
            files_text_display.insert(END, "-"*80)
        files_text_display.see(END)
        
        files_text_display.insert(END, "\nRemoving Chimera Started ...\n\n")
        window.after(5000, removing_chimera_func(container))
        files_text_display.see(END)
        chimera_log_dir = os.listdir(os.path.join(mount_dir, "vsearch_result"))
        chimera_log = [os.path.join(vsearch_dir, file) for file in chimera_log_dir if ".nochimera.log.txt" in file][0]
        with open(chimera_log, "r") as fr:
            files_text_display.insert(END, fr.read())
            files_text_display.insert(END, "-"*80)
        files_text_display.see(END)
        
        files_text_display.insert(END, "\nTaxonomy Assignment Started ...\n\n")
        window.after(5000, taxonomy_assignment_func(container))
        files_text_display.see(END)
        taxa_log_dir = os.listdir(os.path.join(mount_dir, "vsearch_result"))
        taxa_log = [os.path.join(vsearch_dir, file) for file in taxa_log_dir if ".taxa.log.txt" in file][0]
        with open(taxa_log, "r") as fr:
            files_text_display.insert(END, fr.read())
            files_text_display.insert(END, "-"*80)
        files_text_display.see(END)

        files_text_display.insert(END, "\nAnalysis Finished.")
        files_text_display.see(END)
        # Stop and remove the image
        container.stop()
        container.remove()
    except Exception as e:
        print("-"*30)
        print(e)
        print("-"*30)
        messagebox.showerror("Error", message="Analysis Crashed!!!\nPlease check your selected parameters and reload your input files.")



#setting empty variables for pipeline tick boxes
adapt_trimming_tick_var=tk.IntVar()
prime_trimming_tick_var=tk.IntVar()

#setting empty variables for parameters
fastq_maxee_var=tk.StringVar()
vser_db_var = tk.StringVar()
id_var=tk.StringVar()

adapt_for_read_var=tk.StringVar()
adapt_rev_read_var=tk.StringVar()
adapt_min_length_var=tk.StringVar()
adapt_qual_cutoff_var=tk.StringVar()
adapt_maxn_var=tk.StringVar()
adapt_overlap_var=tk.StringVar()
adapt_overlap_var.set("3")
adapt_error_rate_var=tk.StringVar()
adapt_error_rate_var.set("0.1")
adapt_discard_untrim_var=tk.StringVar()

prime_for_read_var=tk.StringVar()
prime_rev_read_var=tk.StringVar()
prime_min_length_var=tk.StringVar()
prime_qual_cutoff_var=tk.StringVar()
prime_maxn_var=tk.StringVar()
prime_overlap_var=tk.StringVar()
prime_overlap_var.set("3")
prime_error_rate_var=tk.StringVar()
prime_error_rate_var.set("0.1")
prime_discard_untrim_var=tk.StringVar()

param_window = ""


fastq_maxee = ""
vser_db = ""
vsearch_id = ""
adapt_for_read = ""
adapt_rev_read = ""
adapt_min_length = ""
adapt_qual_cutoff = ""
adapt_maxn = ""
adapt_overlap = ""
adapt_error_rate = ""
adapt_discard_untrim = ""
prime_for_read = ""
prime_rev_read = ""
prime_min_length = ""
prime_qual_cutoff = ""
prime_maxn = ""
prime_overlap = ""
prime_error_rate = ""
prime_discard_untrim = ""
adapt_trimming = ""
prime_trimming = ""

#function for user parameter input
def user_submit():
    global fastq_maxee, vser_db, vsearch_id, adapt_for_read, \
    adapt_rev_read, adapt_min_length, adapt_qual_cutoff, adapt_maxn, \
    adapt_overlap, adapt_error_rate, adapt_discard_untrim, prime_for_read, \
    prime_rev_read, prime_min_length, prime_qual_cutoff, prime_maxn, \
    prime_overlap, prime_error_rate, prime_discard_untrim, adapt_trimming, prime_trimming 
    
    fastq_maxee=fastq_maxee_var.get()
    vser_db=vser_db_var.get()
    vsearch_id=id_var.get()
    adapt_for_read=adapt_for_read_var.get()
    adapt_rev_read=adapt_rev_read_var.get()
    adapt_min_length=adapt_min_length_var.get()
    adapt_qual_cutoff=adapt_qual_cutoff_var.get()
    adapt_maxn=adapt_maxn_var.get()
    adapt_overlap=adapt_overlap_var.get()
    adapt_error_rate=adapt_error_rate_var.get()
    adapt_discard_untrim=adapt_discard_untrim_var.get()
    prime_for_read=prime_for_read_var.get()
    prime_rev_read=prime_rev_read_var.get()
    prime_min_length=prime_min_length_var.get()
    prime_qual_cutoff=prime_qual_cutoff_var.get()
    prime_maxn=prime_maxn_var.get()
    prime_overlap=prime_overlap_var.get()
    prime_error_rate=prime_error_rate_var.get()
    prime_discard_untrim=prime_discard_untrim_var.get()
    adapt_trimming=adapt_trimming_tick_var.get()
    prime_trimming=prime_trimming_tick_var.get()

    files_text_display.insert(END, '\n')
    files_text_display.insert(END,"Parameters set: ")
    files_text_display.insert(END, '\n')
    files_text_display.insert(END, '\n')
    if (adapt_trimming == 0):
        files_text_display.insert(END, "Adapt trimming not selected")
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, '\n')
    elif (adapt_trimming == 1):
        files_text_display.insert(END, "Adaptor trimming selected")
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Adaptor forward sequence: ")
        files_text_display.insert(END, adapt_for_read)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Adaptor reverse sequence: ")
        files_text_display.insert(END, adapt_rev_read)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Minimum length: ")
        files_text_display.insert(END, adapt_min_length)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Quality cutoff: ")
        files_text_display.insert(END, adapt_qual_cutoff)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Max-n: ")
        files_text_display.insert(END, adapt_maxn)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Overlap: ")
        files_text_display.insert(END, adapt_overlap)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Error-rate: ")
        files_text_display.insert(END, adapt_error_rate)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Discard-untrimmed: ")
        files_text_display.insert(END, adapt_discard_untrim)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, '\n')
    if (prime_trimming == 0):
        files_text_display.insert(END, "Primer trimming not selected")
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, '\n')
    elif (prime_trimming == 1):
        files_text_display.insert(END, "Primer trimming selected")
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Primer forward sequence: ")
        files_text_display.insert(END, prime_for_read)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Primer reverse sequence: ")
        files_text_display.insert(END, prime_rev_read)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Minimum length: ")
        files_text_display.insert(END, prime_min_length)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Quality cutoff: ")
        files_text_display.insert(END, prime_qual_cutoff)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Max-n: ")
        files_text_display.insert(END, prime_maxn)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Overlap: ")
        files_text_display.insert(END, prime_overlap)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Error-rate: ")
        files_text_display.insert(END, prime_error_rate)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, "Discard-untrimmed: ")
        files_text_display.insert(END, prime_discard_untrim)
        files_text_display.insert(END, '\n')
        files_text_display.insert(END, '\n')
    
    files_text_display.insert(END, "Quality filtering parameters")
    files_text_display.insert(END, '\n')
    files_text_display.insert(END, "FastQ maxee: ")
    files_text_display.insert(END, fastq_maxee)
    files_text_display.insert(END, '\n')
    files_text_display.insert(END, '\n')
    
    files_text_display.insert(END, "Taxonomic assignment parameters")
    files_text_display.insert(END, '\n')
    files_text_display.insert(END, "ID: ")
    files_text_display.insert(END, vsearch_id)
    files_text_display.insert(END, '\n')
    files_text_display.insert(END, "Database: ")
    files_text_display.insert(END, vser_db)
    files_text_display.insert(END, '\n')
    files_text_display.insert(END, '\n')
    files_text_display.see(END)
    
    
    # Modify the forward reverse sequence input to match cutadapt format (with complements)
    adapt_for_read, adapt_rev_read = returning_cutadapt_forward_reverse(adapt_for_read, adapt_rev_read)
    prime_for_read, prime_rev_read = returning_cutadapt_forward_reverse(prime_for_read, prime_rev_read)
    
    param_window.destroy()
    
    
    
def returning_cutadapt_forward_reverse(forward_read, reverse_read):
    # Generate the adapter pairs
    forward, reverse_rc, reverse, forward_rc = seq_pairs(forward_read, reverse_read)

    # Generate the primer pairs
    forward_read = f"{forward_read}...{reverse_rc}"
    reverse_read = f"{reverse_read}...{forward_rc}"
    
    return forward_read, reverse_read
    

def open_parameters_window_func():
    global param_window
    param_window = Toplevel(window)
    param_window.title("Select parameters window")
    param_frame = Frame(param_window)
    param_frame.pack(expand=True, fill="both")

    analy_steps_label = tk.Label(master=param_frame, text="Analysis steps:")
    analy_steps_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")

    #trimming adaptor parameters
    adapt_trimming_check_box = tk.Checkbutton(master=param_frame, text="1. Adapter Trimming", 
                                              variable=adapt_trimming_tick_var, onvalue=1, 
                                              offvalue=0, font=("Helvetica", 16, "bold"))
    adapt_trimming_check_box.grid(row=1, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(adapt_trimming_check_box, text = "(Mandatory step if adapters not removed )- Removal of adapter sequences,\nwhich are short, chemically synthesized, single-stranded, or double-stranded oligonucleotide\n used in the sequencing of DNA/RNA, from the raw sequence reads to ensure accurate downstream analysis.")

    adapt_for_read_label = tk.Label(master=param_frame, text="Forward reads: *", font=("Arial", 13, "normal"))
    adapt_for_read_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(adapt_for_read_label, text="(Mandatory) This option specifies the forward (3’ end ) adapter/primer sequence to be trimmed from the read.")
    adapt_for_read_entry = tk.Entry(master=param_frame, textvariable=adapt_for_read_var, font=('calibre', 10, 'normal'))
    adapt_for_read_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

    adapt_rev_read_label = tk.Label(master=param_frame, text="Reverse reads: *", font=("Arial", 13, "normal"))
    adapt_rev_read_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(adapt_rev_read_label, "(Mandatory) This option specifies the forward (3’ end ) adapter/primer sequence to be trimmed from the reverse read.")
    adapt_rev_read_entry = tk.Entry(master=param_frame, textvariable=adapt_rev_read_var, font=('calibre', 10, 'normal'))
    adapt_rev_read_entry.grid(row=3, column=1, padx=10, pady=5, sticky="w")

    min_length_label = tk.Label(master=param_frame, text="Min Length:", font=("Arial", 13, "normal"))
    min_length_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(min_length_label, text="This option sets the minimum length for reads to be kept after trimming.\n Reads shorter than this length after trimming will be discarded.")
    min_length_entry = tk.Entry(master=param_frame, textvariable = adapt_min_length_var, font=('calibre',10,'normal'))
    min_length_entry.grid(row=4, column=1, padx=10, pady=5, sticky="w")

    qual_cutoff_label = tk.Label(master=param_frame, text="Quality cutoff:", font=("Arial", 13, "normal"))
    qual_cutoff_label.grid(row=5, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(qual_cutoff_label, text="This option sets the minimum quality score required to keep a base during trimming.\n Bases with quality scores below this threshold will be trimmed.")
    qual_cutoff_entry = tk.Entry(master=param_frame, textvariable = adapt_qual_cutoff_var, font=('calibre',10,'normal'))
    qual_cutoff_entry.grid(row=5, column=1, padx=10, pady=5, sticky="w")

    maxn_label = tk.Label(master=param_frame, text="Max-n:", font=("Arial", 13, "normal"))
    maxn_label.grid(row=6, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(maxn_label, text="This option sets the maximum allowed fraction of N bases (ambiguous bases) in a read.\n Reads exceeding this fraction will be discarded.\n(value ranges from 0.0 to 1.0)")
    maxn_entry = tk.Entry(master=param_frame, textvariable = adapt_maxn_var, font=('calibre',10,'normal'))
    maxn_entry.grid(row=6, column=1, padx=10, pady=5, sticky="w")

    overlap_label = tk.Label(master=param_frame, text="Overlap:", font=("Arial", 13, "normal"))
    overlap_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(overlap_label, text="This option specifies the minimum overlap required between a read and the adapter/primer for adapter/primer removal.\n (Default value: 3)")
    overlap_entry = tk.Entry(master=param_frame, textvariable = adapt_overlap_var, font=('calibre',10,'normal'))
    overlap_entry.grid(row=7, column=1, padx=10, pady=5, sticky="w")

    error_rate_label = tk.Label(master=param_frame, text="Error rate:", font=("Arial", 13, "normal"))
    error_rate_label.grid(row=8, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(error_rate_label, text="This option sets the maximum allowed error rate during adapter/primer matching. (Default value: 0.1)")
    error_rate_entry = tk.Entry(master=param_frame, textvariable = adapt_error_rate_var, font=('calibre',10,'normal'))
    error_rate_entry.grid(row=8, column=1, padx=10, pady=5, sticky="w")

    dis_untrim_label = tk.Label(master=param_frame, text="Discard untrimmed:", font=("Arial", 13, "normal"))
    dis_untrim_label.grid(row=9, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(dis_untrim_label, text="This option will discard any read pair for which the specified adapter/primer sequences are not found and removed during the trimming process.")
    dis_untrim_dropdown = tk.OptionMenu(param_frame, adapt_discard_untrim_var, "Yes", "No")
    dis_untrim_dropdown.grid(row=9, column=1, padx=10, pady=5, sticky="w")
    
    #trimming primers parameters

    prime_trimming_check_box = tk.Checkbutton(master=param_frame, text="2. Primer Trimming", 
                                              variable=prime_trimming_tick_var, onvalue=1, 
                                              offvalue=0, font=("Helvetica", 16, "bold"))
    prime_trimming_check_box.grid(row=1, column=2, padx=10, pady=5, sticky="w")
    CreateToolTip(prime_trimming_check_box, text = "(Mandatory step if primers not removed )- Elimination of primer sequences,\n which are short DNA sequences used to amplify specific regions of interest,\n to prevent them from interfering with subsequent analysis steps.")

    prime_for_read_label = tk.Label(master=param_frame, text="Forward reads: *", font=("Arial", 13, "normal"))
    prime_for_read_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")
    prime_for_read_entry = tk.Entry(master=param_frame, textvariable = prime_for_read_var, font=('calibre',10,'normal'))
    prime_for_read_entry.grid(row=2, column=3, padx=10, pady=5, sticky="w")

    prime_rev_read_label = tk.Label(master=param_frame, text="Reverse reads: *", font=("Arial", 13, "normal"))
    prime_rev_read_label.grid(row=3, column=2, padx=10, pady=5, sticky="w")
    prime_rev_read_entry = tk.Entry(master=param_frame, textvariable = prime_rev_read_var, font=('calibre',10,'normal'))
    prime_rev_read_entry.grid(row=3, column=3, padx=10, pady=5, sticky="w")

    min_length_label2 = tk.Label(master=param_frame, text="Min Length:", font=("Arial", 13, "normal"))
    min_length_label2.grid(row=4, column=2, padx=10, pady=5, sticky="w")
    min_length_entry2 = tk.Entry(master=param_frame, textvariable = prime_min_length_var, font=('calibre',10,'normal'))
    min_length_entry2.grid(row=4, column=3, padx=10, pady=5, sticky="w")

    qual_cutoff_label2 = tk.Label(master=param_frame, text="Quality cutoff:", font=("Arial", 13, "normal"))
    qual_cutoff_label2.grid(row=5, column=2, padx=10, pady=5, sticky="w")
    qual_cutoff_entry2 = tk.Entry(master=param_frame, textvariable = prime_qual_cutoff_var, font=('calibre',10,'normal'))
    qual_cutoff_entry2.grid(row=5, column=3, padx=10, pady=5, sticky="w")

    maxn_label2 = tk.Label(master=param_frame, text="Max-n:", font=("Arial", 13, "normal"))
    maxn_label2.grid(row=6, column=2, padx=10, pady=5, sticky="w")
    maxn_entry2 = tk.Entry(master=param_frame, textvariable = prime_maxn_var, font=('calibre',10,'normal'))
    maxn_entry2.grid(row=6, column=3, padx=10, pady=5, sticky="w")

    overlap_label2 = tk.Label(master=param_frame, text="Overlap:", font=("Arial", 13, "normal"))
    overlap_label2.grid(row=7, column=2, padx=10, pady=5, sticky="w")
    overlap_entry2 = tk.Entry(master=param_frame, textvariable = prime_overlap_var, font=('calibre',10,'normal'))
    overlap_entry2.grid(row=7, column=3, padx=10, pady=5, sticky="w")

    error_rate_label2 = tk.Label(master=param_frame, text="Error rate:", font=("Arial", 13, "normal"))
    error_rate_label2.grid(row=8, column=2, padx=10, pady=5, sticky="w")
    error_rate_entry2 = tk.Entry(master=param_frame, textvariable = prime_error_rate_var, font=('calibre',10,'normal'))
    error_rate_entry2.grid(row=8, column=3, padx=10, pady=5, sticky="w")

    dis_untrim_label2 = tk.Label(master=param_frame, text="Discard untrimmed:", font=("Arial", 13, "normal"))
    dis_untrim_label2.grid(row=9, column=2, padx=10, pady=5, sticky="w")
    dis_untrim_dropdown2 = tk.OptionMenu(param_frame, prime_discard_untrim_var, "Yes", "No")
    dis_untrim_dropdown2.grid(row=9, column=3, padx=10, pady=5, sticky="w")
    
    #merging step
    merging_pe_label = tk.Label(master=param_frame, text="3. Merging paired end reads", font=("Helvetica", 16, "bold"))
    merging_pe_label.grid(row=10, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(merging_pe_label, text = "This step merges paired-end reads from forward and reverse reads into a single merged fasta file.")
    
    #quality filtering parameters
    qual_fil_label = tk.Label(master=param_frame, text="4. Quality filtering", font=("Helvetica", 16, "bold"))
    qual_fil_label.grid(row=11, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(qual_fil_label, text = "This step filters reads from merged files based on the expected errors (--fastq_maxee) specified by the user.")

    fast_label = tk.Label(master=param_frame, text="Fastq Maxee: *", font=("Arial", 13, "normal"))
    fast_label.grid(row=12, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(fast_label, text="(Mandatory) This option discard reads with an expected error rate greater than the specified by the user,\n and the remaining reads are written to filtered fasta file.\n(values ranges from 0.0 to 1.0)")
    fast_entry = tk.Entry(master=param_frame, textvariable = fastq_maxee_var, font=('calibre',10,'normal'))
    fast_entry.grid(row=12, column=1, padx=10, pady=5, sticky="w")

    #identifying unique sequences
    iden_uniq_label = tk.Label(master=param_frame, text="5. Identifying unique sequences", font=("Helvetica", 16, "bold"))
    iden_uniq_label.grid(row=13, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(iden_uniq_label, text = "This step identifies unique sequences in a filtered fasta file, removes duplicates, and writes the unique sequences to a unique fasta file.")

    #detecting ASVs
    detec_asvs_label = tk.Label(master=param_frame, text="6. Detect ASVs", font=("Helvetica", 16, "bold"))
    detec_asvs_label.grid(row=14, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(detec_asvs_label, text = "This step performs clustering of sequences using the UNOISE algorithm, which is designed for denoising amplicon sequence data and writes to asvs fasta file.")

    #removing chimeric reads
    rem_chim_label = tk.Label(master=param_frame, text="7. Remove chimeric reads", font=("Helvetica", 16, "bold"))
    rem_chim_label.grid(row=15, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(rem_chim_label, text = "This step detects chimeric sequences using the UCHIME3 de novo algorithm. Non-chimeric sequences are written to nonchimeras fasta files.")

    #taxonomy assignment
    tax_assig_label = tk.Label(master=param_frame, text="8. Taxanomic assignment", font=("Helvetica", 16, "bold"))
    tax_assig_label.grid(row=16, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(tax_assig_label, text = "This step assigns taxonomic classifications to the non-chimeric sequences\n using a reference database (user-defined) with a sequence identity threshold of --ID (user-defined).\n The output writes the results in text format.")

    id_label = tk.Label(master=param_frame, text="ID (% similarity): *", font=("Arial", 13, "normal"))
    id_label.grid(row=17, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(id_label, text="(Mandatory) Sequence identity threshold set to (usually 0.97 or 0.99) for assigning taxonomy.\n(values ranges from 0.0 to 1.0)")
    id_entry = tk.Entry(param_frame, textvariable = id_var, font=('calibre',10,'normal'))
    id_entry.grid(row=17, column=1, padx=10, pady=5, sticky="w")

    db_label = tk.Label(master=param_frame, text="Database: *", font=("Arial", 13, "normal"))
    db_label.grid(row=18, column=0, padx=10, pady=5, sticky="w")
    CreateToolTip(db_label, text="(Mandatory) Reference database file used for taxonomic assignment.")
    dis_untrim_dropdown = tk.OptionMenu(param_frame, vser_db_var, "trnL_GH.fasta", "trnL_CD.fasta", "RbcL.fasta", "psbA-trnH.fasta", "MatK.fasta", "atpF-atpH.fasta", "ITS.fasta")
    dis_untrim_dropdown.grid(row=18, column=1, padx=10, pady=5, sticky="w")

    # Submit button
    set_param_button = tk.Button(master=param_frame, text="Submit Parameters", width=15, height=1, command=user_submit)
    set_param_button.grid(row=19, column=3, padx=10, pady=10, sticky="e")

    param_window.mainloop()


    
#creating GUI labels and text boxes
meta_analy_label = tk.Label(master=frame, text="Metabarcoding Analysis", font=("Arial", 16, "bold"))
meta_analy_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

load_files_button = tk.Button(master=frame,text="Load Files", width=10, height=1, command=load_files_func)
load_files_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")


select_param_button = tk.Button(master=frame,text="Select Parameters", width=10, height=1, command=open_parameters_window_func)
select_param_button.grid(row=2, column=0, padx=10, pady=5, sticky="w")

files_text_display = tk.Text(master=frame, height=30, width=139)
files_text_display.grid(row=1, column=1, columnspan=2, rowspan=4, padx=10, pady=5, sticky="w")
files_text_display.insert(END,"Analysis progress area:\n")

run_pipe_button = tk.Button(master=frame,text="Start Analysis", width=10, height=1, command=pipeline_func) 
run_pipe_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

analy_out_button = tk.Button(master=frame,text="Analyse Output", width=10, height=1, command=open_analysis_window_func)
analy_out_button.grid(row=4, column=0, padx=10, pady=5, sticky="w")


window.mainloop()