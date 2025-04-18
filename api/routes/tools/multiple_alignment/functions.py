import time
import requests
from typing import Optional

def align_sequences(sequences: str, seq_type: str, email: str = "user@example.com") -> Optional[str]:
    """
    Align sequences using Clustal Omega API.
    
    Args:
        sequences: FASTA-formatted sequences.
        seq_type: Sequence type ('dna' or 'protein').
        email: Email for API (default: user@example.com).
    
    Returns:
        Alignment in Clustal format, or None if failed.
    
    Raises:
        ValueError: If inputs are invalid.
        RuntimeError: If API request fails.
    """
    if not sequences.strip():
        raise ValueError("Sequences cannot be empty")
    if seq_type not in ["dna", "protein"]:
        raise ValueError("Sequence type must be 'dna' or 'protein'")
    
    base_url = "https://www.ebi.ac.uk/Tools/services/rest/clustalo"
    try:
        # Submit job
        data = {"email": email, "sequence": sequences, "stype": seq_type}
        response = requests.post(f"{base_url}/run", data=data)
        response.raise_for_status()
        job_id = response.text

        # Poll status
        status_url = f"{base_url}/status/{job_id}"
        while requests.get(status_url).text == "RUNNING":
            time.sleep(5)

        # Get result
        result_url = f"{base_url}/result/{job_id}/aln-clustal_num"
        result = requests.get(result_url)
        result.raise_for_status()
        return result.text
    except requests.RequestException as e:
        raise RuntimeError(f"Clustal Omega API error: {str(e)}")
    except Exception as e:
        raise RuntimeError(f"Alignment failed: {str(e)}")