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
for file in "$results_folder"/*.asvs.fa; do 
    # Chimera Removal
    sample_prefix="${file%.asvs.fa}"
    vsearch --uchime3_denovo $file --nonchimeras $sample_prefix.asvs_nochimera.fa --fasta_width 0 --relabel ASV --xsize --log $sample_prefix.nochimera.log.txt --sizeout

    ((counter++))
done


# Completion message
echo "Done"
date


: '
# command run used for honey
source chimera_removal.sh
'