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
for file in "$results_folder"/*.uniques.fa; do 
    # Detect ASVs
    sample_prefix="${file%.uniques.fa}"
    vsearch --cluster_unoise $file --centroids $sample_prefix.asvs.fa --relabel ASV --sizeout --log $sample_prefix.asvs.log.txt

    ((counter++))
done


# Completion message
echo "Done"
date


: '
# command run used for honey
source detect_ASVs.sh
'