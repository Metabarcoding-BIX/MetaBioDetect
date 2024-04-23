#!/bin/bash 
# Stop at runtime errors
set -e

base_folder=""

############ Script start here:##############
if [ -d "/app/uploads/trimmed_reads" ]; then
  # Trimmed folder exists, which means adapter/primer ran before
  base_folder="/app/uploads/trimmed_reads"
  echo "Trimmed folder exists"
else
  # Trimmed folder doesn't exist, which means adapter/primer trimming was not chosen
  base_folder="/app/uploads"
  echo "Trimmed folder does not exist"
fi


mkdir -p /app/uploads/vsearch_result
results_folder="/app/uploads/vsearch_result"
database_folder="/app/db"


# Loop through each sample in filenames.txt
while read sample; do
  echo "$sample"
  IFS=',' read -a myarray <<< "$sample"
  # Get the filenames for the fastq files with forward (R1) and reverse (R2) reads:
  R1=${myarray[0]}
  R1=${R1//$'\r'} 
  R2=${myarray[1]}
  R2=${R2//$'\r'}
  echo "$R1"
  echo "$R2"
  sample_prefix="${R1%1.fq.gz}"

    # Merging paired-end command
    if [[ $base_folder == "/app/uploads/trimmed_reads" ]]; then
      merge_pairend_cmd="vsearch --fastq_mergepairs $base_folder${R1/.fq.gz/_primer_trimmed.fq.gz} --reverse $base_folder${R2/.fq.gz/_primer_trimmed.fq.gz} --relabel merged --fastqout $results_folder/$sample_prefix.merged.fastq --fastq_allowmergestagger --log $results_folder/$sample_prefix.merged.log.txt"
    else
      merge_pairend_cmd="vsearch --fastq_mergepairs $base_folder$R1 --reverse $base_folder$R2 --relabel merged --fastqout $results_folder/$sample_prefix.merged.fastq --fastq_allowmergestagger --log $results_folder/$sample_prefix.merged.log.txt"
    fi

    # Execute command
    $merge_pairend_cmd 

done </app/uploads/filenames.txt

# Completion message
echo "Done"
date


: '
# command run used for honey
source merge_pair_end.sh
'