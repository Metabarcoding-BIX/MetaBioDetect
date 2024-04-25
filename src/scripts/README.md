# MetaBioDetect

In this folder, you can find the metabarcoding analysis scripts, taxonomy databases folder (db), and the Dockerfile, that is used to package the analysis scripts and dependencies in one place. Docker container was used to run the analysis in an isolated environment, ensuring consistency in software deployment across different computing infrastructure. Currently it's compatible with Debian-based Linux distributions, macOS, and Windows.

The metabarcoding analysis pipeline was built using cutadapt=4.8 for trimming and Vsearch (v2.27.1_linux_aarch64) for the main metabarcoding steps. Following is the pipeline:

1. Adapter trimming (`adapter_trimming.sh`)
2. Primer trimming (`primer_trimming.sh`)
3. Merging paired end reads (`merge_pair_end.sh`)
4. Quality filtering (`quality_filtering.sh`)
5. Identifying unique sequences (`identifying_unique_seq.sh`)
6. Detecting ASVs (`detect_ASVs.sh`)
7. Removing chimeric reads (`chimera_removal.sh`)
8. Taxonomy assignment (`taxonomy_assignment.sh`)

In the taxonomy assignment step, the databases that could be used are in **src/scripts/db** folder. The current databases were taken from PlantAligDB 27-07-2017 version (*A database of curated nucleotide sequence alignments for plants*). The Folder could be updated with new databases (read the developer use below).


## For developer use

For rebuilding the Docker image with updated scripts, databases, and dependencies, refer to the following steps:

1. To update or add new scripts make sure to include them in the same directory of the Dockerfile, so they get copied inside the container. For updating the dependencies refer to the Dockerfile and add the related commands for them. 

2. After having the updates, in terminal, navigate to the directory where Dockerfile resides and build the image by running:

`docker build -t meta_bio_detect .` 

3. Save the built image into tar file with the following command: 

`docker save -o MetaBioDetect_img.tar meta_bio_detect`

4. Lastly, move `MetaBioDetect_img.tar` into the **src/resources** directory, to be used within the deployed GUI app. Refer to the **src/README.md** for the next steps on how to deploy the app.