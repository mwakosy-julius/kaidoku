import requests
import time
import xml.etree.ElementTree as ET

def fetch_gene(text):
    try:
        # query = text.replace(" ", "+")
        
        config = {
            "headers": {
            }
        }
        
        esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term={text}&rettype=fasta&retmode=json&retmax=3"
        esearch_response = requests.get(esearch_url, headers=config.get("headers", {}))
        esearch_response.raise_for_status() 
        
        esearch_data = esearch_response.json()
        id_list = esearch_data.get("esearchresult", {}).get("idlist", [])

        # return id_list
        
        if not id_list:
            return {"error": "No results found for the query."}
        
        efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id={','.join(id_list)}&rettype=fasta&retmode=json"
        efetch_response = requests.get(efetch_url, headers=config.get("headers", {}))
        efetch_response.raise_for_status()
        
        fasta_data = efetch_response.text
        sequences = fasta_data.split(">")[1:]  
        formatted_sequences = [seq.split("\n", 1)[0] for seq in sequences]
        
        return {
            # "id_list": id_list,
            "sequences": fasta_data
        }
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def fetch_protein(text):
    try:
        # query = text.replace(" ", "+")
        
        config = {
            "headers": {
            }
        }
        
        esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=protein&term={text}&rettype=fasta&retmode=json&retmax=10"
        esearch_response = requests.get(esearch_url, headers=config.get("headers", {}))
        esearch_response.raise_for_status() 
        
        esearch_data = esearch_response.json()
        id_list = esearch_data.get("esearchresult", {}).get("idlist", [])

        # return id_list
        
        if not id_list:
            return {"error": "No results found for the query."}
        
        efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=protein&id={','.join(id_list)}&rettype=fasta&retmode=json"
        efetch_response = requests.get(efetch_url, headers=config.get("headers", {}))
        efetch_response.raise_for_status()
        
        fasta_data = efetch_response.text
        sequences = fasta_data.split(">")[1:]  
        formatted_sequences = [seq.split("\n", 1)[0] for seq in sequences]
        
        return {
            # "id_list": id_list,
            "sequences": fasta_data
        }
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def fetch_blast(text):
    url = "https://blast.ncbi.nlm.nih.gov/blast/Blast.cgi?CMD=Get&FORMAT_TYPE=Text&RID=$rid"
    try:
        response = requests.get(url)
        response.raise_for_status()  
        data = response.text
        return data 
    except requests.exceptions.RequestException as e:
        return {"error": "No results found for the query."}

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

def perform_blastp(text, program='blastp', database='nr', evalue=1e-5, max_results=5, organism=None):
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

# # Example Usage
# sequence = "ATGGTGCACCTGACTCCTGAGGAGAAGTCTGCCGTTACTGCCCTGTGGGGCAAGGTGAACGTGGATGAAGTTGGTGGTGAGGCCCTGGGCAG"
# results = perform_blast(sequence, program='blastn', database='nt', evalue=1e-5, max_results=5, organism="Homo sapiens")

# # Save or process the results
# with open("blast_results.xml", "w") as file:
#     file.write(results)