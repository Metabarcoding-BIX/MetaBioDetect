#!/bin/bash 
# Stop at runtime errors
set -e


############ Script start here:##############
base_folder="/app/uploads/trimmed_reads"
mkdir -p /app/uploads/vsearch_result
results_folder="/app/uploads/vsearch_result"
database_folder="/app/db"


# Extract user arguments
for arg in "$@"; do
    case "$arg" in
        # Quality filtering configs
        --db=*) database="${arg#*=}" ;;
        --id=*) id="${arg#*=}" ;;
    esac
done

# Initialize counter for suffixing samples output
counter=1
for file in "$results_folder"/*.asvs_nochimera.fa; do 
    # Taxonomy assignment 
    sample_prefix="${file%.asvs_nochimera.fa}"
    vsearch --usearch_global $file --db $database_folder/$database --id $id --top_hits_only --userfields query+target+qstrand+id --userout $sample_prefix.taxa.txt --notmatched $sample_prefix.unassigned.fa --log $sample_prefix.taxa.log.txt
    
    ((counter++))
done


# Completion message
echo "Done"
date


: '
# command run used for honey
source taxonomy_assignment.sh --db="trnL_GH.fasta" --id=0.97
'