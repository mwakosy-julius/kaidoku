import requests
import time
import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from cachetools import TTLCache
from fastapi import HTTPException

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache for BLAST results (TTL: 1 hour)
cache = TTLCache(maxsize=100, ttl=3600)

# Sequence validation patterns
DNA_PATTERN = re.compile(r'^[ATCGNRYSWKMBDHVatcgnryswkmbdhv]+$')
PROTEIN_PATTERN = re.compile(r'^[ACDEFGHIKLMNPQRSTVWYacdefghiklmnpqrstvwy]+$')

def validate_sequence(sequence: str, program: str) -> None:
    """Validate sequence for BLAST program."""
    if program == 'blastn':
        if not DNA_PATTERN.match(sequence):
            raise ValueError("Invalid nucleotide sequence: must contain A, T, C, G, N, or IUPAC bases")
    elif program == 'blastp':
        if not PROTEIN_PATTERN.match(sequence):
            raise ValueError("Invalid protein sequence: must contain standard amino acids")
    else:
        raise ValueError(f"Unsupported BLAST program: {program}")

def parse_fasta(fasta: str) -> str:
    """Parse FASTA input and return the first valid sequence."""
    sequences = []
    current_seq = []
    current_header = None
    lines = fasta.strip().splitlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('>'):
            if current_seq:
                seq = ''.join(current_seq).upper()
                sequences.append((current_header, seq))
                current_seq = []
            current_header = line
        else:
            current_seq.append(line)
    
    if current_seq:
        seq = ''.join(current_seq).upper()
        sequences.append((current_header, seq))
    
    if not sequences:
        raise ValueError("No sequences found in FASTA input")
    
    for header, seq in sequences:
        if seq:
            return seq
    
    raise ValueError("No valid sequences found in FASTA input")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((requests.RequestException, ValueError))
)
def blast_sequence(
    sequence: str,
    program: str = 'blastn',
    database: str = 'nt',
    evalue: float = 1e-5,
    max_results: int = 10,
    organism: Optional[str] = None
) -> List[Dict]:
    """
    Perform BLAST query for gene (nucleotide) or protein sequences using NCBI BLAST API.
    
    Args:
        sequence: Raw or FASTA sequence (nucleotide for blastn, protein for blastp).
        program: BLAST program ('blastn' for genes, 'blastp' for proteins).
        database: BLAST database (e.g., 'nt' for blastn, 'nr' for blastp).
        evalue: Expect value cutoff for matches.
        max_results: Maximum number of results to retrieve.
        organism: Optional organism filter (e.g., 'Homo sapiens').
    
    Returns:
        List of dictionaries with BLAST results (organism, accession, percentage_identity,
        query_coverage, evalue, bit_score, gaps).
    
    Raises:
        ValueError: For invalid sequence or parameters.
        HTTPException: For API failures.
    """
    # Handle FASTA input
    if sequence.strip().startswith('>'):
        sequence = parse_fasta(sequence)
    
    # Validate sequence
    validate_sequence(sequence, program)
    
    # Check cache
    cache_key = f"{program}:{database}:{sequence}:{evalue}:{max_results}:{organism}"
    if cache_key in cache:
        logger.info("Returning cached BLAST results")
        return cache[cache_key]
    
    blast_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
    session = requests.Session()
    
    # Submit query
    payload = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': sequence,
        'EXPECT': evalue,
        'HITLIST_SIZE': max_results,
        'FORMAT_TYPE': 'XML',
    }
    if organism:
        payload['ENTREZ_QUERY'] = f'"{organism}"[organism]'
    
    logger.info("Submitting BLAST query...")
    try:
        response = session.post(blast_url, data=payload, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error submitting BLAST query: {str(e)}")
    
    # Parse RID and RTOE
    result = response.text
    rid_match = re.search(r'RID = (\S+)', result)
    rtoe_match = re.search(r'RTOE = (\d+)', result)
    if not rid_match or not rtoe_match:
        raise ValueError("Could not retrieve RID or RTOE from response")
    
    rid = rid_match.group(1)
    rtoe = int(rtoe_match.group(1))
    logger.info(f"RID: {rid}, RTOE: {rtoe} seconds")
    
    # Poll for results
    payload = {
        'CMD': 'Get',
        'RID': rid,
        'FORMAT_TYPE': 'XML',
    }
    max_attempts = 30
    poll_interval = max(rtoe, 5)
    
    for attempt in range(max_attempts):
        logger.info(f"Checking BLAST statu (attempt {attempt + 1}/{max_attempts})...")
        logger.debug(f"Polling URL: {blast_url}, Parameters: {payload}")
        response = session.get(blast_url, params=payload, timeout=30)
        response.raise_for_status()
        
        root = ET.fromstring(response.text)
        status = root.find(".//Status")
        if status is not None and status.text == "READY":
            break
        if attempt == max_attempts - 1:
            raise HTTPException(status_code=500, detail="BLAST job timed out")
        time.sleep(poll_interval)
    
    # Parse results
    results = []
    for hit in root.findall(".//Hit"):
        hit_def = hit.find(".//Hit_def").text or "Unknown"
        hit_id = hit.find(".//Hit_id").text or "Unknown"
        accession = hit.find(".//Hit_accession").text or "Unknown"
        
        # Clean organism name
        organism_match = re.search(r'^(.*?)(?:\s+\w+\s+\w+|\s*\[.*?\]|\s*$)', hit_def)
        organism_clean = organism_match.group(1) if organism_match else hit_def
        
        hsp = hit.find(".//Hsp")
        if hsp is None:
            continue
        
        identity = int(hsp.find("Hsp_identity").text)
        align_len = int(hsp.find("Hsp_align-len").text)
        query_len = int(root.find(".//Iteration_query-len").text)
        evalue_hit = float(hsp.find("Hsp_evalue").text)
        bit_score = float(hsp.find("Hsp_bit-score").text)
        gaps = int(hsp.find("Hsp_gaps").text)
        query_from = int(hsp.find("Hsp_query-from").text)
        query_to = int(hsp.find("Hsp_query-to").text)
        
        percentage_identity = (identity / align_len) * 100
        query_coverage = ((query_to - query_from + 1) / query_len) * 100
        
        results.append({
            "organism": organism_clean,
            "accession": accession,
            "hit_id": hit_id,
            "percentage_identity": round(percentage_identity, 2),
            "query_coverage": round(query_coverage, 2),
            "evalue": evalue_hit,
            "bit_score": round(bit_score, 2),
            "gaps": gaps
        })
    
    # Cache and sort results
    cache[cache_key] = results
    logger.info(f"Retrieved {len(results)} BLAST hits")
    
    return sorted(results, key=lambda x: x['bit_score'], reverse=True)