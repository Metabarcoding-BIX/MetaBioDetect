#!/bin/bash 
# Stop at runtime errors
set -e

base_folder="/app/uploads"
mkdir -p /app/uploads/trimmed_reads
results_folder="/app/uploads/trimmed_reads"

# Extract user arguments
for arg in "$@"; do
    case "$arg" in
        # Trimming adapters configs
        --a=*) forward_adapter="${arg#*=}" ;;
        --A=*) reverse_adapter="${arg#*=}" ;;
        --minimum-length=*) minimum_length="${arg#*=}" ;;
        --quality-cutoff=*) quality_cutoff="${arg#*=}" ;;
        --max-n=*) max_n="${arg#*=}" ;;
        --overlap=*) overlap="${arg#*=}" ;;
        --error-rate=*) error_rate="${arg#*=}" ;;
        --discard-untrimmed=*) discard_untrimmed="${arg#*=}" ;;
    esac
done

# Loop through each sample in filenames.txt
while read sample; do
  echo "$sample"
  IFS=',' read -a myarray <<< "$sample"
  # Get the filenames for the fastq files with forward (R1) and reverse (R2) reads:
  R1=${myarray[0]}
  R1=${R1//$'\r'} 
  R2=${myarray[1]}
  R2=${R2//$'\r'}
  echo "forward: $R1"
  echo "reverse: $R2"
  sample_prefix="${R1%1.fq.gz}"

    # Adapter trimming command
    # adapter_trim_cmd="cutadapt -a $forward_adapter -A $reverse_adapter -o $results_folder/$R1 -p $results_folder/$R2 --minimum-length $minimum_length --quality-cutoff $quality_cutoff --overlap $overlap --error-rate $error_rate $base_folder/$R1 $base_folder/$R2 "
    adapter_trim_cmd="cutadapt -a $forward_adapter -A $reverse_adapter -o $results_folder$R1 -p $results_folder$R2 --overlap $overlap --error-rate $error_rate $base_folder$R1 $base_folder$R2"
    

    # Add --minimum-length option if minimum_length is set
    if [ -n "$minimum_length" ]; then
      adapter_trim_cmd+=" --minimum-length $minimum_length"
    fi

    # Add --quality-cutoff option if quality_cutoff is set
    if [ -n "$quality_cutoff" ]; then
      adapter_trim_cmd+=" --quality-cutoff $quality_cutoff"
    fi

    # Add --max-n option if max_n is set
    if [ -n "$max_n" ]; then
      adapter_trim_cmd+=" --max-n $max_n"
    fi

    # Add --discard-untrimmed option if discard_untrimmed is set
    if [ -n "$discard_untrimmed" ]; then
      adapter_trim_cmd+=" --discard-untrimmed"
    fi

    # Execute adapter trimming command
    $adapter_trim_cmd 2>&1 | tee "$results_folder/$sample_prefix.adapter_trim.log.txt"

done </app/uploads/filenames.txt


# Completion message
echo ""
echo "Done"
date


: '
# command run used for honey
source adapter_trimming.sh --a="AGATCGGAAGAGCGTCGTGTAGGGAAAGAGTGTAGATCTCGGTGGTCGCCGTATCATT...CAAGCAGAAGACGGCATACGAGATAGTCATCCGTGACTGGAGTTCAGACGTGTGCTCTTCCGATC" --A="GATCGGAAGAGCACACGTCTGAACTCCAGTCACGGATGACTATCTCGTATGCCGTCTTCTGCTTG...AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT" --minimum-length=50 --quality-cutoff=10 --max-n=0.05 --overlap=5 --error-rate=0.3
'