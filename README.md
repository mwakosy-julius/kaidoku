# Kaidoku: Bioinformatics Toolkit API

Kaidoku is a comprehensive bioinformatics API that provides various tools for analyzing, manipulating, and visualizing biological data. This project offers RESTful endpoints for DNA/RNA sequence analysis, alignment, phylogenetics, and more.

## Installation

### Prerequisites

- Python 3.7+
- pip or pipenv

### Using pip

```bash
# Clone the repository
git clone https://github.com/mwakosy-julius/kaidoku.git
cd kaidoku

# Install dependencies
pip install -r requirements.txt
```

### Using pipenv

```bash
# Clone the repository
git clone https://github.com/mwakosy-julius/kaidoku.git
cd kaidoku

# Install dependencies
pipenv install
```

## Usage

### Running the API Server

Start the API server with:

```bash
python main.py
```

The API will be available at `http://localhost:8000` by default.

### API Endpoints

The following endpoints are available:

- `/auth` - Authentication and user management
- `/blast` - Sequence similarity searching
- `/codon-usage` - Codon usage analysis
- `/consensus-maker` - Consensus sequence generation
- `/data-compression` - Biological data compression
- `/dna-assembler` - DNA sequence assembly

Additional tools (in development/refactoring):

- `/consensus-maker` - Consensus sequence generation
- `/data-compression` - Biological data compression
- `/dna-assembler` - DNA sequence assembly
- `/gc-content` - GC content analysis
- `/metagenomics` - Metagenomic analysis
- `/motif-finder` - Sequence motif discovery
- `/multiple-alignment` - Multiple sequence alignments
- `/musicdna` - DNA-to-music conversion
- `/pairwise-alignment` - Pairwise sequence alignments
- `/phylogenetic-trees` - Phylogenetic tree analysis
- `/primer-design` - PCR primer design
- `/quality-control` - Sequence data QC
- `/variant-calling` - Genetic variant identification

### Authentication

The API uses JWT token-based authentication. To access protected endpoints:

1. Register or login to obtain a token
2. Include the token in the `Authorization` header for subsequent requests

### Example API Usage

```python
import requests
import json

# Step 1: Authenticate
auth_response = requests.post(
    "http://localhost:8000/auth/token",
    data={"username": "user@example.com", "password": "password"}
)
token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Step 2: Use an endpoint (e.g., DNA Assembly)
sequences = ["ATGC", "GCTA", "TACG"]
response = requests.post(
    "http://localhost:8000/dna-assembler/assemble",
    headers=headers,
    json={"sequences": sequences}
)
result = response.json()
print(f"Assembled DNA: {result['assembled_sequence']}")
```

## Project Structure

The project follows a FastAPI-based architecture:

```
main.py               # FastAPI application entry point
app/
  ├── core/           # Core functionality (security, etc.)
  ├── db/             # Database models and connection
  ├── models/         # Pydantic models for request/response
  ├── routes/         # API route handlers
  └── tools/          # Bioinformatics tool implementations
      ├── blast/
      ├── codon_usage/
      ├── consensus_maker/
      ├── data_compression/
      ├── dna_assembler/
      └── ...
```

## Development

### Refactoring Notes

Some tool modules are being refactored from Django to FastAPI structure:

1. Create `router.py` and `functions.py` in each tool directory
2. Move business logic from Django views to functions
3. Create FastAPI routers with appropriate endpoints
4. Update authentication to use FastAPI dependency injection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- List any libraries or tools that inspired this project
- Credits to contributors
- Any relevant papers or methodologies
