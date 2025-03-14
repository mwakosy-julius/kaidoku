import numpy as np

def parse_fastq(file_path):
    sequences = []
    qualities = []
    
    with open(file_path, "r") as file:
        while True:
            header = file.readline().strip()
            if not header:
                break  
            seq = file.readline().strip()  
            file.readline()  
            qual = file.readline().strip()  
            
            sequences.append(seq)
            qualities.append([ord(char) - 33 for char in qual]) 
    
    return sequences, qualities

def calculate_gc_content(sequences):
    gc_contents = [(seq.count("G") + seq.count("C")) / len(seq) * 100 for seq in sequences]
    return gc_contents

def calculate_quality_distribution(qualities):
    avg_qualities = [np.mean(q) for q in qualities]
    return avg_qualities