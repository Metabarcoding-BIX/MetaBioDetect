#!/bin/bash 
# Stop at runtime errors
set -e

base_folder=""

if [ -d "/app/uploads/trimmed_reads" ]; then
  # Trimmed folder exists, which means adapter trimming ran before
  base_folder="/app/uploads/trimmed_reads"
  echo "Trimmed folder exists"
else
  # Trimmed folder doesn't exist, which means adapter trimming was not chosen
  base_folder="/app/uploads"
  echo "Trimmed folder does not exist"
fi

mkdir -p /app/uploads/trimmed_reads
results_folder="/app/uploads/trimmed_reads"


# Extract user arguments
for arg in "$@"; do
    case "$arg" in
        # Trimming primers configs
        --a=*) forward_primer="${arg#*=}" ;;
        --A=*) reverse_primer="${arg#*=}" ;;
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

    # Primer trimming command
    # primer_trim_cmd="cutadapt -a $forward_primer -A $reverse_primer -o $results_folder/${R1/.fq.gz/_primer_trimmed.fq.gz} -p $results_folder/${R2/.fq.gz/_primer_trimmed.fq.gz} --minimum-length $minimum_length --quality-cutoff $quality_cutoff --overlap $overlap --error-rate $error_rate $results_folder/$R1 $results_folder/$R2 "
    primer_trim_cmd="cutadapt -a $forward_primer -A $reverse_primer -o $results_folder${R1/.fq.gz/_primer_trimmed.fq.gz} -p $results_folder${R2/.fq.gz/_primer_trimmed.fq.gz} --overlap $overlap --error-rate $error_rate $base_folder$R1 $base_folder$R2"
    
    # Add --minimum-length option if minimum_length is set
    if [ -n "$minimum_length" ]; then
      primer_trim_cmd+=" --minimum-length $minimum_length"
    fi
    
    # Add --quality-cutoff option if quality_cutoff is set
    if [ -n "$quality_cutoff" ]; then
      primer_trim_cmd+=" --quality-cutoff $quality_cutoff"
    fi
    
    # Add --max-n option if max_n is set
    if [ -n "$max_n" ]; then
      primer_trim_cmd+=" --max-n $max_n"
    fi

    # Add --discard-untrimmed option if discard_untrimmed is set
    if [ -n "$discard_untrimmed" ]; then
      primer_trim_cmd+=" --discard-untrimmed"
    fi

    # Execute primer trimming command
    $primer_trim_cmd 2>&1 | tee "$results_folder/$sample_prefix.primer_trim.log.txt"

done </app/uploads/filenames.txt


# Completion message
echo ""
echo "Done"
date


: '
# command run used for honey
source primer_trimming.sh --a="GGGCAATCCTGAGCCAA...GATAGGTGCAGAGACTCAATGG" --A="CCATTGAGTCTCTGCACCTATC...TTGGCTCAGGATTGCCC" --minimum-length=40 --quality-cutoff=15 --overlap=3 --error-rate=0.1
'