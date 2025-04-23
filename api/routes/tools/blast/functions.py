import requests
import time
import xml.etree.ElementTree as ET

def perform_blastn(text, program='blastn', database='nt', evalue=1e-5, max_results=10, organism=None):
    """
    Perform a BLAST query using the NCBI BLAST API and return formatted results.
    
    Parameters:
        text (str): The nucleotide or protein sequence to query.  
        program (str): BLAST program (e.g., 'blastn', 'blastp').
        database (str): BLAST database to search (e.g., 'nt', 'nr').
        evalue (float): Expect value cutoff for matches.
        max_results (int): Maximum number of results to retrieve.
        organism (str): Limit results to a specific organism (e.g., "Homo sapiens").
    
    Returns:
        list: List of dictionaries containing organism names, hit IDs, and percentage matches.
    """
    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    
    payload = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': text,
        'EXPECT': evalue,
        'HITLIST_SIZE': max_results,
        'FORMAT_TYPE': 'XML',
    }
    if organism:
        payload['ENTREZ_QUERY'] = f'"{organism}"[organism]'
    
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
    root = ET.fromstring(response.text)
    
    for hit in root.findall(".//Hit"):
        organism_name = hit.find(".//Hit_def").text
        hit_id = hit.find(".//Hit_id").text

        hsp = hit.find(".//Hsp")
        if hsp is not None:
            identity = int(hsp.find("Hsp_identity").text)
            align_length = int(hsp.find("Hsp_align-len").text)
            percentage_match = (identity / align_length) * 100

            results.append({
                "organism_name": organism_name,
                "hit_id": hit_id,
                "percentage_match": round(percentage_match, 2)
            })
    
    return results

def perform_blastp(text, program='blastp', database='nr', evalue=1e-5, max_results=10, organism=None):
    """
    Perform a BLAST query using the NCBI BLAST API for protein sequences.
    
    Parameters:
        text (str): The protein sequence to query.
        program (str): BLAST program (default 'blastp').
        database (str): BLAST database to search (default 'nr').
        evalue (float): Expect value cutoff for matches.
        max_results (int): Maximum number of results to retrieve.
        organism (str): Limit results to a specific organism (optional).
    
    Returns:
        list: List of dictionaries containing organism names, hit IDs, and percentage matches.
    """
    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    
    payload = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': text,
        'EXPECT': evalue,
        'HITLIST_SIZE': max_results,
        'FORMAT_TYPE': 'XML',
    }
    if organism:
        payload['ENTREZ_QUERY'] = f'"{organism}"[organism]'
    
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
    root = ET.fromstring(response.text)
    
    for hit in root.findall(".//Hit"):
        organism_name = hit.find(".//Hit_def").text
        hit_id = hit.find(".//Hit_id").text

        hsp = hit.find(".//Hsp")
        if hsp is not None:
            identity = int(hsp.find("Hsp_identity").text)
            align_length = int(hsp.find("Hsp_align-len").text)
            percentage_match = (identity / align_length) * 100

            results.append({
                "organism_name": organism_name,
                "hit_id": hit_id,
                "percentage_match": round(percentage_match, 2)
            })
    
    return results

def perform_blastx(text, program='blastx', database='nr', evalue=1e-5, max_results=10, organism=None):
    """
    Perform a BLAST query using the NCBI BLAST API for translated nucleotide sequences.
    Parameters:
        text (str): The nucleotide sequence to query.
        program (str): BLAST program (default 'blastx').
        database (str): BLAST database to search (default 'nr').
        evalue (float): Expect value cutoff for matches.
        max_results (int): Maximum number of results to retrieve.
        organism (str): Limit results to a specific organism (optional).
    Returns:
        list: List of dictionaries containing organism names, hit IDs, and percentage matches.
    """
    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    
    payload = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': text,
        'EXPECT': evalue,
        'HITLIST_SIZE': max_results,
        'FORMAT_TYPE': 'XML',
    }
    if organism:
        payload['ENTREZ_QUERY'] = f'"{organism}"[organism]'
    
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
    root = ET.fromstring(response.text)
    
    for hit in root.findall(".//Hit"):
        organism_name = hit.find(".//Hit_def").text
        hit_id = hit.find(".//Hit_id").text

        hsp = hit.find(".//Hsp")
        if hsp is not None:
            identity = int(hsp.find("Hsp_identity").text)
            align_length = int(hsp.find("Hsp_align-len").text)
            percentage_match = (identity / align_length) * 100

            results.append({
                "organism_name": organism_name,
                "hit_id": hit_id,
                "percentage_match": round(percentage_match, 2)
            })
    return results