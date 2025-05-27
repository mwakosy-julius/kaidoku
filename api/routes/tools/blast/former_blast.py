import requests
import re
import xml.etree.ElementTree as ET
import time

def format_sequence(sequence):
    sequence = sequence.upper()
    if sequence[0] == ">":
        sequence = sequence.splitlines()[1:]
        sequence = "".join(sequence).strip()
    else:
        sequence = "".join(sequence.splitlines()).strip()
    return sequence

def perform_blastn(sequence, program='blastn', database='nt', evalue=1e-5, max_results=10, organism=None):

    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    
    payload = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': sequence,
        'EXPECT': evalue,
        'HITLIST_SIZE': max_results,
        'FORMAT_TYPE': 'XML',
    }
    # if organism:
    #     payload['ENTREZ_QUERY'] = f'"{organism}"[organism]'
    
    print("Submitting BLAST query...")
    response = requests.post(blast_url, data=payload)
    if response.status_code != 200:
        raise Exception(f"Error submitting BLAST query: {response.status_code}")
    
    result = response.text
    rid_index = result.find("RID = ")
    rtoe_index = result.find("RTOE = ")
    if rid_index == -1 or rtoe_index == -1:
        raise Exception("Could not retrieve RID or RTOE from the response.")
    
    rid = result[rid_index + 6:result.find("\n", rid_index)].strip()
    rtoe = int(result[rtoe_index + 7:result.find("\n", rtoe_index)].strip())
    print(f"RID: {rid}, RTOE: {rtoe} seconds")
    
    time.sleep(rtoe)
    
    payload = {
        'CMD': 'Get',
        'RID': rid,
        'FORMAT_TYPE': 'XML',
    }
    print("Retrieving results...")
    response = requests.get(blast_url, params=payload)
    if response.status_code != 200:
        raise Exception(f"Error retrieving BLAST results: {response.status_code}")
    
    results = []
    print(response.text,"text\n\n")
    root = ET.fromstring(response.text)
    print(root)
    
    for hit in root.findall(".//Hit"):
        organism = hit.find(".//Hit_def").text
        hit_id = hit.find(".//Hit_id").text

        hsp = hit.find(".//Hsp")
        if hsp is not None:
            identity = int(hsp.find("Hsp_identity").text)
            align_length = int(hsp.find("Hsp_align-len").text)
            percentage_match = (identity / align_length) * 100

            results.append({
                "organism": organism,
                "hit_id": hit_id,
                "percentage_match": round(percentage_match, 2)
            })
    print("Results retrieved successfully.")
    print(f"Total hits: {len(results)}")
    print(results)
    return results

def perform_blastp(sequence, program='blastp', database='nr', evalue=1e-5, max_results=10, organism=None):

    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    
    payload = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': sequence,
        'EXPECT': evalue,
        'HITLIST_SIZE': max_results,
        'FORMAT_TYPE': 'XML',
    }
    # if organism:
    #     payload['ENTREZ_QUERY'] = f'"{organism}"[organism]'
    
    print("Submitting BLAST query...")
    response = requests.post(blast_url, data=payload)
    if response.status_code != 200:
        raise Exception(f"Error submitting BLAST query: {response.status_code}")
    
    result = response.text
    rid_index = result.find("RID = ")
    rtoe_index = result.find("RTOE = ")
    if rid_index == -1 or rtoe_index == -1:
        raise Exception("Could not retrieve RID or RTOE from the response.")
    
    rid = result[rid_index + 6:result.find("\n", rid_index)].strip()
    rtoe = int(result[rtoe_index + 7:result.find("\n", rtoe_index)].strip())
    print(f"RID: {rid}, RTOE: {rtoe} seconds")
    
    time.sleep(rtoe)
    
    payload = {
        'CMD': 'Get',
        'RID': rid,
        'FORMAT_TYPE': 'XML',
    }
    print("Retrieving results...")
    response = requests.get(blast_url, params=payload)
    if response.status_code != 200:
        raise Exception(f"Error retrieving BLAST results: {response.status_code}")
    
    results = []
    print(response.text,"text\n\n")
    root = ET.fromstring(response.text)
    print(root)
    
    for hit in root.findall(".//Hit"):
        organism = hit.find(".//Hit_def").text
        hit_id = hit.find(".//Hit_id").text

        hsp = hit.find(".//Hsp")
        if hsp is not None:
            identity = int(hsp.find("Hsp_identity").text)
            align_length = int(hsp.find("Hsp_align-len").text)
            percentage_match = (identity / align_length) * 100

            results.append({
                "organism": organism,
                "hit_id": hit_id,
                "percentage_match": round(percentage_match, 2)
            })
    print("Results retrieved successfully.")
    print(f"Total hits: {len(results)}")
    print(results)
    return results