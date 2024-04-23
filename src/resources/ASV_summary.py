def calculate_stats(assigned_taxa_file, unassigned_fasta_file):
    
    assigned_asvs = []
    with open(assigned_taxa_file, 'r') as file:
        for line in file:
            parts = line.strip().split('\t')
            asv = parts[0]
            assigned_asvs.append(asv)
            
    unassigned_asv_ids = []
    with open(unassigned_fasta_file, 'r') as file:
        lines = file.readlines()
        for i in lines:
            if i.startswith(">"):
                unassigned_asv_ids.append(i)
    
    
    total_asvs = len(assigned_asvs) + len(unassigned_asv_ids)
    assigned_percentage = (len(assigned_asvs) / total_asvs) * 100
    unassigned_percentage = (len(unassigned_asv_ids) / total_asvs) * 100
    return len(assigned_asvs), assigned_percentage, len(unassigned_asv_ids), unassigned_percentage

