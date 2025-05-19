import requests

def fetch_gene(query):
    try:
        # query = query.replace(" ", "+")
        
        config = {
            "headers": {
            }
        }
        
        esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term={query}&rettype=fasta&retmode=json&retmax=10"
        esearch_response = requests.get(esearch_url, headers=config.get("headers", {}))
        esearch_response.raise_for_status() 
        
        esearch_data = esearch_response.json()
        id_list = esearch_data.get("esearchresult", {}).get("idlist", [])
        
        if not id_list:
            return {"error": "No results found for the query."}
        
        efetch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nuccore&id={','.join(id_list)}&rettype=fasta&retmode=json"
        efetch_response = requests.get(efetch_url, headers=config.get("headers", {}))
        efetch_response.raise_for_status()
        
        fasta_data = efetch_response.text
        sequences = fasta_data.split(">")[1:]  
        formatted_sequences = [seq.split("\n", 1)[0] for seq in sequences]
        
        return {
            "sequences": fasta_data
        }
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def fetch_protein(query):
    try:
        # query = query.replace(" ", "+")
        
        config = {
            "headers": {
            }
        }
        
        esearch_url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=protein&term={query}&rettype=fasta&retmode=json&retmax=10"
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
