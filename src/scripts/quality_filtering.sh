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
        --fastq_maxee=*) fastq_maxee="${arg#*=}" ;;
    esac
done

# Initialize counter for suffixing samples output
counter=1
for file in "$results_folder"/*.merged.fastq; do 
    # Quality filtering command
    sample_prefix="${file%.merged.fastq}"
    vsearch --fastq_filter $file -fastq_maxee $fastq_maxee --relabel filtered --fastaout $sample_prefix.filtered.fa --log $sample_prefix.filtered.log.txt

    ((counter++))
done

# Completion message
echo "Done"
date


: '
# command run used for honey
source quality_filtering.sh --fastq_maxee=1.0
'