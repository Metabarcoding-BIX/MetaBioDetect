import tkinter as tk
from tkinter import *
from tkinter import filedialog
import subprocess

#creating main GUI shell
window = tk.Tk() #can also define size with .geometry without use of frame
frame = tk.Frame(master=window, width=1200, height=500)
window.title("MetaBioDetect GUI")
frame.pack()

def calculate_pair_func(file):
    file_prefix = (file[0:file.index(".fq.gz")])
    if file_prefix.endswith('1'):
        complement = file_prefix[:-1] + "2.fq.gz"
    elif file_prefix.endswith('2'):
        complement = file_prefix[:-1] + "1.fq.gz"
    else:
        raise Exception ("Error, file should end in a 1 or 2")
    return complement

#function for loading files and storing filepath and names for pipeline
def load_files_func():
    pairs_list = []
    complements = set()
    #clearing text display everytime files are opened
    files_text_display.delete('1.0', END)
    loaded_files = filedialog.askopenfilenames()
    files_text_display.insert(END, loaded_files)
    list(loaded_files)
    for i in loaded_files:
        complement = calculate_pair_func(i)
        if complement in complements or i in complements:
        # print(i < complement, i > complement, i, complement)
            if i < complement:
                pairs_list.append(i +','+ complement)
            elif complement < i:
                pairs_list.append(complement +','+ i)
        else:
            complements.add(complement)
    #w to write over and no append to document
    txt_files = open("filenames.txt", "w")
    for i in pairs_list:
        txt_files.write(i + "\n")
    txt_files.close()

#function to open second window for visualisation 
def open_analysis_window_func():
    #creating second window shell
    new_window = Toplevel(window)
    new_window.title("Downstream analysis window")
    new_frame = Frame(new_window, width=1200, height=800)
    new_frame.pack()
    meta_data_label = Label(new_frame, text = "Metabarcoding Data Visualisation")
    meta_data_label.place(x=500, y=0)
    samp_vis_label = Label(new_frame, text = "Samples to visualize:")
    samp_vis_label.place(x=10, y=50)
    bar_chart_label = Label(new_frame, text = "Abundance Bar Chart")
    bar_chart_label.place(x=620, y=50)
    samp_text_display = Text(new_frame)
    samp_text_display.place(x=10, y=80)
    sum_rep_label = Label(new_frame, text = "Summary report:")
    sum_rep_label.place(x=10, y=420)
    pie_chart_label = Label(new_frame, text = "Abundance Pie Chart")
    pie_chart_label.place(x=620, y=420)
    report_text_display = tk.Text(new_frame)
    report_text_display.place(x=10, y=450)
    new_window.mainloop()

#defining fuction to run pipeline shell script 
#add trimming into the shell script 
def pipeline_func():
    #if statement to say no files loaded in fun with no files
    prog_text_display.insert(END,"Pipeline running")
    subprocess.call(['sh', './test.sh'])
    #prog_text_display.insert(END,"Trimming completed")

#setting empty variables for pipeline tick boxes
adapt_trimming_tick_var=tk.IntVar()
prime_trimming_tick_var=tk.IntVar()
merging_pe_tick_var=tk.IntVar()
qual_fil_tick_var=tk.IntVar()
iden_uniq_tick_var=tk.IntVar()
detec_asvs_tick_var=tk.IntVar()
rem_chim_tick_var=tk.IntVar()
tax_assig_tick_var=tk.IntVar()

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
adapt_error_rate_var=tk.StringVar()
adapt_discard_untrim_var=tk.StringVar()

prime_for_read_var=tk.StringVar()
prime_rev_read_var=tk.StringVar()
prime_min_length_var=tk.StringVar()
prime_qual_cutoff_var=tk.StringVar()
prime_maxn_var=tk.StringVar()
prime_overlap_var=tk.StringVar()
prime_error_rate_var=tk.StringVar()
prime_discard_untrim_var=tk.StringVar()

def close_window():
    window.destroy()

#function for user parameter input
def user_submit():
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
    merging_pe=merging_pe_tick_var.get()
    qual_filt=qual_fil_tick_var.get()
    iden_uniq=iden_uniq_tick_var.get()
    detec_asvs=detec_asvs_tick_var.get()
    rem_chim=rem_chim_tick_var.get()
    tax_assig=tax_assig_tick_var.get()

    prog_text_display.insert(END,"Parameters set: ")
    print(fastq_maxee)
    print(vser_db)
    print(vsearch_id)
    print(adapt_for_read)
    print(adapt_rev_read)
    print(adapt_min_length)
    print(adapt_qual_cutoff)
    print(adapt_maxn)
    print(adapt_overlap)
    print(adapt_error_rate)
    print(adapt_discard_untrim)
    print(prime_for_read)
    print(prime_rev_read)
    print(prime_min_length)
    print(prime_qual_cutoff)
    print(prime_maxn)
    print(prime_overlap)
    print(prime_error_rate)
    print(prime_discard_untrim)
    print(adapt_trimming)
    print(prime_trimming)
    print(merging_pe)
    print(qual_filt)
    print(iden_uniq)
    print(detec_asvs)
    print(rem_chim)
    print(tax_assig)
    #close_window()
    

def open_parameters_window_func():
    param_window = Toplevel(window)
    param_window.title("Select parameters window")
    param_frame = Frame(param_window, width=1200, height=850)
    param_frame.pack()
    analy_steps_label = tk.Label(master=param_frame, text="Analysis steps:")
    analy_steps_label.place(x=10, y=10)
    adapt_trimming_check_box = tk.Checkbutton(master=param_frame, text="Adapter Trimming", variable=adapt_trimming_tick_var, onvalue=1, offvalue=0)
    adapt_trimming_check_box.place(x=100, y=50)

    #trimming adaptor parameters
    adapt_for_read_label = tk.Label(master=param_frame, text="Forward reads:")
    adapt_for_read_label.place(x=150, y=90)
    adapt_for_read_entry = tk.Entry(master=param_frame, textvariable = adapt_for_read_var, font=('calibre',10,'normal'))
    adapt_for_read_entry.place(x=150, y=110)

    adapt_rev_read_label = tk.Label(master=param_frame, text="Reverse reads:")
    adapt_rev_read_label.place(x=400, y=90)
    adapt_rev_read_entry = tk.Entry(master=param_frame, textvariable = adapt_rev_read_var, font=('calibre',10,'normal'))
    adapt_rev_read_entry.place(x=400, y=110)

    min_length_label = tk.Label(master=param_frame, text="Min Length:")
    min_length_label.place(x=650, y=90)
    min_length_entry = tk.Entry(master=param_frame, textvariable = adapt_min_length_var, font=('calibre',10,'normal'))
    min_length_entry.place(x=650, y=110)

    qual_cutoff_label = tk.Label(master=param_frame, text="Quality cutoff:")
    qual_cutoff_label.place(x=900, y=90)
    qual_cutoff_entry = tk.Entry(master=param_frame, textvariable = adapt_qual_cutoff_var, font=('calibre',10,'normal'))
    qual_cutoff_entry.place(x=900, y=110)

    maxn_label = tk.Label(master=param_frame, text="Max-n:")
    maxn_label.place(x=150, y=150)
    maxn_entry = tk.Entry(master=param_frame, textvariable = adapt_maxn_var, font=('calibre',10,'normal'))
    maxn_entry.place(x=150, y=170)

    overlap_label = tk.Label(master=param_frame, text="Overlap:")
    overlap_label.place(x=400, y=150)
    overlap_entry = tk.Entry(master=param_frame, textvariable = adapt_overlap_var, font=('calibre',10,'normal'))
    overlap_entry.place(x=400, y=170)

    error_rate_label = tk.Label(master=param_frame, text="Error rate:")
    error_rate_label.place(x=650, y=150)
    error_rate_entry = tk.Entry(master=param_frame, textvariable = adapt_error_rate_var, font=('calibre',10,'normal'))
    error_rate_entry.place(x=650, y=170)    

    dis_untrim_label = tk.Label(master=param_frame, text="Discard untrimmed:")
    dis_untrim_label.place(x=900, y=150)
    dis_untrim_dropdown = tk.OptionMenu(param_frame, adapt_discard_untrim_var, "Yes", "No")
    dis_untrim_dropdown.place(x=900, y=170)

    #trimming primers parameters

    prime_trimming_check_box = tk.Checkbutton(master=param_frame, text="Primer Trimming", variable=prime_trimming_tick_var, onvalue=1, offvalue=0)
    prime_trimming_check_box.place(x=100, y=220)

    prime_for_read_label = tk.Label(master=param_frame, text="Forward reads:")
    prime_for_read_label.place(x=150, y=260)
    prime_for_read_entry = tk.Entry(master=param_frame, textvariable = prime_for_read_var, font=('calibre',10,'normal'))
    prime_for_read_entry.place(x=150, y=290)

    prime_rev_read_label = tk.Label(master=param_frame, text="Reverse reads:")
    prime_rev_read_label.place(x=400, y=260)
    prime_rev_read_entry = tk.Entry(master=param_frame, textvariable = prime_rev_read_var, font=('calibre',10,'normal'))
    prime_rev_read_entry.place(x=400, y=290)

    min_length_label2 = tk.Label(master=param_frame, text="Min Length:")
    min_length_label2.place(x=650, y=260)
    min_length_entry2 = tk.Entry(master=param_frame, textvariable = prime_min_length_var, font=('calibre',10,'normal'))
    min_length_entry2.place(x=650, y=290)

    qual_cutoff_label2 = tk.Label(master=param_frame, text="Quality cutoff:")
    qual_cutoff_label2.place(x=900, y=260)
    qual_cutoff_entry2 = tk.Entry(master=param_frame, textvariable = prime_qual_cutoff_var, font=('calibre',10,'normal'))
    qual_cutoff_entry2.place(x=900, y=290)

    maxn_label2 = tk.Label(master=param_frame, text="Max-n:")
    maxn_label2.place(x=150, y=330)
    maxn_entry2 = tk.Entry(master=param_frame, textvariable = prime_maxn_var, font=('calibre',10,'normal'))
    maxn_entry2.place(x=150, y=350)

    overlap_label2 = tk.Label(master=param_frame, text="Overlap:")
    overlap_label2.place(x=400, y=330)
    overlap_entry2 = tk.Entry(master=param_frame, textvariable = prime_overlap_var, font=('calibre',10,'normal'))
    overlap_entry2.place(x=400, y=350)

    error_rate_label2 = tk.Label(master=param_frame, text="Error rate:")
    error_rate_label2.place(x=650, y=330)
    error_rate_entry2 = tk.Entry(master=param_frame, textvariable = prime_error_rate_var, font=('calibre',10,'normal'))
    error_rate_entry2.place(x=650, y=350)

    dis_untrim_label2 = tk.Label(master=param_frame, text="Discard untrimmed:")
    dis_untrim_label2.place(x=900, y=330)
    dis_untrim_dropdown2 = tk.OptionMenu(param_frame, prime_discard_untrim_var, "Yes", "No")
    dis_untrim_dropdown2.place(x=900, y=350)

    #merging step
    merging_pe_check_box = tk.Checkbutton(master=param_frame, text="Merging paied end reads", variable=merging_pe_tick_var, onvalue=1, offvalue=0)
    merging_pe_check_box.place(x=100, y=400)

    #quality filtering parameters
    qual_fil_check_box = tk.Checkbutton(master=param_frame, text="Quality filtering", variable=qual_fil_tick_var, onvalue=1, offvalue=0)
    qual_fil_check_box.place(x=100, y=450)

    fast_label = tk.Label(master=param_frame, text="Fastq Maxee:")
    fast_label.place(x=150, y=490)
    fast_entry = tk.Entry(master=param_frame, textvariable = fastq_maxee_var, font=('calibre',10,'normal'))
    fast_entry.place(x=150, y=510)  

    #identifying unique sequences
    iden_uniq_check_box = tk.Checkbutton(master=param_frame, text="Identifying unique sequences", variable=iden_uniq_tick_var, onvalue=1, offvalue=0)
    iden_uniq_check_box.place(x=100, y=560)

    #detecting ASVs
    detec_asvs_check_box = tk.Checkbutton(master=param_frame, text="Detect ASVs", variable=detec_asvs_tick_var, onvalue=1, offvalue=0)
    detec_asvs_check_box.place(x=100, y=610)

    #removing chimeric reads
    rem_chim_check_box = tk.Checkbutton(master=param_frame, text="Remove chimeric reads", variable=rem_chim_tick_var, onvalue=1, offvalue=0)
    rem_chim_check_box.place(x=100, y=660)

    #taxonomy assignment
    tax_assig_check_box = tk.Checkbutton(master=param_frame, text="Taxanomic assignment", variable=tax_assig_tick_var, onvalue=1, offvalue=0)
    tax_assig_check_box.place(x=100, y=710)

    id_label = tk.Label(master=param_frame, text="ID:")
    id_label.place(x=150, y=750)
    id_entry = tk.Entry(param_frame, textvariable = id_var, font=('calibre',10,'normal'))
    id_entry.place(x=150, y=770)

    db_label = tk.Label(master=param_frame, text="Database:")
    db_label.place(x=400, y=750)
    dis_untrim_dropdown = tk.OptionMenu(param_frame, vser_db_var, "trnL_GH", "trnL_CD", "RbcL", "psbA-trnH", "MatK", "atpF-atpH", "ITS")
    dis_untrim_dropdown.place(x=400, y=770)

    #submitting parameters
    set_param_button = tk.Button(master=param_frame,text="Submit Parameters", width=10, height=1, command=user_submit)
    set_param_button.place(x=530, y=800)

    param_window.mainloop()

#creating GUI labels and text boxes
meta_analy_label = tk.Label(master=frame, text="Metabarcoding Analysis")
meta_analy_label.place(x=520, y=7)

load_files_button = tk.Button(master=frame,text="Load Files", width=10, height=1, command=load_files_func)
load_files_button.place(x=540, y=35)

loaded_files_label = tk.Label(master=frame, text="Loaded files:")
loaded_files_label.place(x=10, y=80)

prog_label = tk.Label(master=frame, text="Progress:")
prog_label.place(x=610, y=80)

files_text_display = tk.Text(master=frame, height=20, width=82)
files_text_display.place(x=10, y=100)

prog_text_display = tk.Text(master=frame, height=20, width=82)
prog_text_display.place(x=610, y=100)

run_pipe_button = tk.Button(master=frame,text="Start Analysis", width=10, height=1, command=pipeline_func)
run_pipe_button.place(x=535, y=380)

analy_out_button = tk.Button(master=frame,text="Analyse Output", width=10, height=1, command=open_analysis_window_func)
analy_out_button.place(x=830, y=380)

select_param_button = tk.Button(master=frame,text="Select Parameters", width=10, height=1, command=open_parameters_window_func)
select_param_button.place(x=250, y=380)


window.mainloop()