#!/bin/bash
# qsub script.sh

# PBS directives
#---------------

#PBS -N VSEARCH_PIPELINE
#PBS -l nodes=1:ncpus=12
#PBS -l walltime=01:00:00
#PBS -q three_hour
#PBS -m abe
#PBS -M shubham.patil.698@cranfield.ac.uk

#===============
#PBS -j oe
#PBS -v "CUDA_VISIBLE_DEVICES="
#PBS -W sandbox=PRIVATE
#PBS -k n
ln -s $PWD $PBS_O_WORKDIR/$PBS_JOBID
## Change to working directory
cd $PBS_O_WORKDIR
## Calculate number of CPUs and GPUs
export cpus=`cat $PBS_NODEFILE | wc -l`
## =============

# Stop at runtime errors
set -e

## Load production modules
module use /apps/modules/all
module load CONDA/TensorFlow-2.12-GPU-Python-3.9
## Load environment
cd /project/Zahra_Karimi/bioinformatics_group_project3
conda activate /project/Zahra_Karimi/bioinformatics_group_project3/.conda/envs/meta_env
##########################################################




############ Script start here:##############
base_folder="/mnt/beegfs/project/Zahra_Karimi/bioinformatics_group_project3/SHUBHAM/TRIMMING/"
results_folder="/mnt/beegfs/project/Zahra_Karimi/bioinformatics_group_project3/SHUBHAM/VSEARCH/V_RESULTS_TRNL/"
database_folder="/mnt/beegfs/project/Zahra_Karimi/bioinformatics_group_project3/SHUBHAM/VSEARCH/V_DATABASE/"

# Merge PairedEnd reads
vsearch --fastq_mergepairs $base_folder/honey_1_ZKDN230004379-1A_H3FJ2DSX7_L1_1_primer_trimmed.fq.gz --reverse $base_folder/honey_1_ZKDN230004379-1A_H3FJ2DSX7_L1_2_primer_trimmed.fq.gz --relabel merged --fastqout $results_folder/mergedh1.fastq --fastq_allowmergestagger
vsearch --fastq_mergepairs $base_folder/honey_2_ZKDN230004380-1A_H3FJ2DSX7_L1_1_primer_trimmed.fq.gz --reverse $base_folder/honey_2_ZKDN230004380-1A_H3FJ2DSX7_L1_2_primer_trimmed.fq.gz --relabel merged --fastqout $results_folder/mergedh2.fastq --fastq_allowmergestagger
vsearch --fastq_mergepairs $base_folder/honey_3_ZKDN230004381-1A_H3FJ2DSX7_L2_1_primer_trimmed.fq.gz --reverse $base_folder/honey_3_ZKDN230004381-1A_H3FJ2DSX7_L2_2_primer_trimmed.fq.gz --relabel merged --fastqout $results_folder/mergedh3.fastq --fastq_allowmergestagger
vsearch --fastq_mergepairs $base_folder/honey_4_ZKDN230004382-1A_H3FJ2DSX7_L2_1_primer_trimmed.fq.gz --reverse $base_folder/honey_4_ZKDN230004382-1A_H3FJ2DSX7_L2_2_primer_trimmed.fq.gz --relabel merged --fastqout $results_folder/mergedh4.fastq --fastq_allowmergestagger

##Quality Filtering
vsearch --fastq_filter $results_folder/mergedh1.fastq -fastq_maxee 1.0 --relabel filtered --fastaout $results_folder/filteredh1.fa
vsearch --fastq_filter $results_folder/mergedh2.fastq -fastq_maxee 1.0 --relabel filtered --fastaout $results_folder/filteredh2.fa
vsearch --fastq_filter $results_folder/mergedh3.fastq -fastq_maxee 1.0 --relabel filtered --fastaout $results_folder/filteredh3.fa
vsearch --fastq_filter $results_folder/mergedh4.fastq -fastq_maxee 1.0 --relabel filtered --fastaout $results_folder/filteredh4.fa

## Identifying unique sequences
vsearch --derep_fulllength $results_folder/filteredh1.fa --output $results_folder/uniquesh1.fa --sizeout
vsearch --derep_fulllength $results_folder/filteredh2.fa --output $results_folder/uniquesh2.fa --sizeout
vsearch --derep_fulllength $results_folder/filteredh3.fa --output $results_folder/uniquesh3.fa --sizeout
vsearch --derep_fulllength $results_folder/filteredh4.fa --output $results_folder/uniquesh4.fa --sizeout

##ASVs 
vsearch --cluster_unoise $results_folder/uniquesh1.fa --centroids $results_folder/asvsh1.fa --relabel ASV --sizeout
vsearch --cluster_unoise $results_folder/uniquesh2.fa --centroids $results_folder/asvsh2.fa --relabel ASV --sizeout
vsearch --cluster_unoise $results_folder/uniquesh3.fa --centroids $results_folder/asvsh3.fa --relabel ASV --sizeout
vsearch --cluster_unoise $results_folder/uniquesh4.fa --centroids $results_folder/asvsh4.fa --relabel ASV --sizeout

##Chimera Removal
vsearch --uchime3_denovo $results_folder/asvsh1.fa --nonchimeras $results_folder/asvsh1_nochime.fa --fasta_width 0 --relabel ASV --xsize --log $results_folder/unchime1_log.txt --sizeout
vsearch --uchime3_denovo $results_folder/asvsh2.fa --nonchimeras $results_folder/asvsh2_nochime.fa --fasta_width 0 --relabel ASV --xsize --log $results_folder/unchime2_log.txt --sizeout
vsearch --uchime3_denovo $results_folder/asvsh3.fa --nonchimeras $results_folder/asvsh3_nochime.fa --fasta_width 0 --relabel ASV --xsize --log $results_folder/unchime3_log.txt --sizeout
vsearch --uchime3_denovo $results_folder/asvsh4.fa --nonchimeras $results_folder/asvsh4_nochime.fa --fasta_width 0 --relabel ASV --xsize --log $results_folder/unchime4_log.txt --sizeout

## Taxonomy assignment with 97% similarity
vsearch --usearch_global $results_folder/asvsh1_nochime.fa --db $database_folder/trnL_GH.fasta --id 0.97 --top_hits_only --userfields query+target+qstrand+id --userout $results_folder/honey1_97.txt
vsearch --usearch_global $results_folder/asvsh2_nochime.fa --db $database_folder/trnL_GH.fasta --id 0.97 --top_hits_only --userfields query+target+qstrand+id --userout $results_folder/honey2_97.txt
vsearch --usearch_global $results_folder/asvsh3_nochime.fa --db $database_folder/trnL_GH.fasta --id 0.97 --top_hits_only --userfields query+target+qstrand+id --userout $results_folder/honey3_97.txt
vsearch --usearch_global $results_folder/asvsh4_nochime.fa --db $database_folder/trnL_GH.fasta --id 0.97 --top_hits_only --userfields query+target+qstrand+id --userout $results_folder/honey4_97.txt



############## Keep this ####################
conda deactivate
# Completion message
echo "Done"
date

## Tidy up the log directory
## =========================
rm $PBS_O_WORKDIR/$PBS_JOBID
