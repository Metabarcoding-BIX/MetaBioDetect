#!/bin/bash 
# Stop at runtime errors
set -e


############ Script start here:##############
base_folder="/app/uploads/trimmed_reads"
mkdir -p /app/uploads/vsearch_result
results_folder="/app/uploads/vsearch_result"
database_folder="/app/db"


# Initialize counter for suffixing samples output
counter=1
for file in "$results_folder"/*.filtered.fa; do 
    # Identifying unique sequences
    sample_prefix="${file%.filtered.fa}"
    vsearch --derep_fulllength $file --output $sample_prefix.uniques.fa --sizeout --log $sample_prefix.uniques.log.txt 

    ((counter++))
done


# Completion message
echo "Done"
date


: '
# command run used for honey
source identifying_unique_seq.sh
'