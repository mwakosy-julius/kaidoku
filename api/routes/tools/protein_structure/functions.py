import random
from typing import Dict


def format_sequence(sequence):
    sequence = sequence.upper()
    if sequence[0] == ">":
        sequence = sequence.splitlines()[1:]
        sequence = "".join(sequence).strip()
    else:
        sequence = "".join(sequence.splitlines()).strip()
    return sequence


def validate_sequence(sequence: str) -> bool:
    """Validate that the sequence contains only standard amino acids."""
    valid_amino_acids = set("ACDEFGHIKLMNPQRSTVWY")
    return all(c.upper() in valid_amino_acids for c in sequence.strip())


def is_hydrophilic_or_hydrophobic(sequence: str, threshold: float = 0.0) -> str:
    # Kyte-Doolittle hydrophobicity scale
    hydrophobicity_scale = {
        "A": 1.8,  # Alanine
        "C": 2.5,  # Cysteine
        "D": -3.5,  # Aspartic acid
        "E": -3.5,  # Glutamic acid
        "F": 2.8,  # Phenylalanine
        "G": -0.4,  # Glycine
        "H": -3.2,  # Histidine
        "I": 4.5,  # Isoleucine
        "K": -3.9,  # Lysine
        "L": 3.8,  # Leucine
        "M": 1.9,  # Methionine
        "N": -3.5,  # Asparagine
        "P": -1.6,  # Proline
        "Q": -3.5,  # Glutamine
        "R": -4.5,  # Arginine
        "S": -0.8,  # Serine
        "T": -0.7,  # Threonine
        "V": 4.2,  # Valine
        "W": -0.9,  # Tryptophan
        "Y": -1.3,  # Tyrosine
    }

    # Validate sequence
    sequence = sequence.upper()
    if not sequence or not all(aa in hydrophobicity_scale for aa in sequence):
        return "Invalid sequence"

    # Calculate average hydrophobicity
    total_score = sum(hydrophobicity_scale[aa] for aa in sequence)
    average_score = total_score / len(sequence)

    # Determine hydrophobicity
    return "Hydrophobic" if average_score > threshold else "Hydrophilic"


def calculate_protein_properties(sequence):
    # Molecular weights of amino acids (in Daltons, average isotopic mass)
    aa_weights = {
        "A": 71.08,
        "R": 156.19,
        "N": 114.11,
        "D": 115.09,
        "C": 103.14,
        "E": 129.12,
        "Q": 128.13,
        "G": 57.05,
        "H": 137.14,
        "I": 113.16,
        "L": 113.16,
        "K": 128.17,
        "M": 131.19,
        "F": 147.18,
        "P": 97.12,
        "S": 87.08,
        "T": 101.11,
        "W": 186.21,
        "Y": 163.18,
        "V": 99.13,
    }

    # pKa values for ionizable groups
    # Format: {'residue': (pKa if positive, pKa if negative, charge when protonated)}
    pka_values = {
        "N_term": (9.69, None, 1),  # N-terminus
        "C_term": (None, 2.34, -1),  # C-terminus
        "C": (None, 8.33, -1),  # Cysteine
        "D": (None, 3.65, -1),  # Aspartic acid
        "E": (None, 4.25, -1),  # Glutamic acid
        "H": (6.00, None, 1),  # Histidine
        "K": (10.53, None, 1),  # Lysine
        "R": (12.48, None, 1),  # Arginine
        "Y": (None, 10.07, -1),  # Tyrosine
    }

    # Validate sequence
    sequence = sequence.upper().strip()
    if not sequence or not all(aa in aa_weights for aa in sequence):
        return None, None

    # Calculate molecular weight
    # Sum of amino acid weights minus water (18.02 Da) per peptide bond
    molecular_weight = sum(aa_weights[aa] for aa in sequence)
    molecular_weight -= 18.02 * (len(sequence) - 1)  # Water loss for n-1 peptide bonds
    molecular_weight += 18.02  # Add water for N- and C-terminus (H2O)

    # Calculate isoelectric point
    def net_charge(pH):
        charge = 0.0

        # N-terminus contribution
        if pka_values["N_term"][0]:
            charge += pka_values["N_term"][2] / (
                1 + 10 ** (pH - pka_values["N_term"][0])
            )

        # C-terminus contribution
        if pka_values["C_term"][1]:
            charge += pka_values["C_term"][2] / (
                1 + 10 ** (pka_values["C_term"][1] - pH)
            )

        # Side chain contributions
        for aa in sequence:
            if aa in pka_values:
                pKa_pos, pKa_neg, base_charge = pka_values[aa]
                if pKa_pos:  # Positive charge when protonated
                    charge += base_charge / (1 + 10 ** (pH - pKa_pos))
                elif pKa_neg:  # Negative charge when deprotonated
                    charge += base_charge / (1 + 10 ** (pKa_neg - pH))

        return charge

    # Binary search to find pH where net charge is closest to zero
    pH_min, pH_max = 0.0, 14.0
    tolerance = 0.01
    max_iterations = 100

    for _ in range(max_iterations):
        pH_mid = (pH_min + pH_max) / 2
        charge = net_charge(pH_mid)

        if abs(charge) < tolerance:
            break
        elif charge > 0:
            pH_min = pH_mid
        else:
            pH_max = pH_mid

    isoelectric_point = round(pH_mid, 2)

    return round(molecular_weight, 2), isoelectric_point


def predict_structure(sequence: str) -> Dict:
    """
    Simulate protein structure prediction.
    Returns a mock PDB string or error.
    In production, integrate with AlphaFold or ESMFold.
    """
    if not sequence:
        return {"error": "Sequence is required"}

    sequence = format_sequence(sequence)

    if not validate_sequence(sequence):
        return {
            "error": "Invalid amino acid sequence. Use A,C,D,E,F,G,H,I,K,L,M,N,P,Q,R,S,T,V,W,Y"
        }

    # Mock PDB data (simplified for demo)
    # In production, call AlphaFold/ESMFold API or local model

    mock_pdb = """
HEADER    PLANT PROTEIN                           02-MAR-00   1EJG
TITLE     CRAMBIN AT ULTRA-HIGH RESOLUTION: VALENCE ELECTRON DENSITY.
COMPND    MOL_ID: 1;
COMPND   2 MOLECULE: CRAMBIN (PRO22,SER22/LEU25,ILE25);
COMPND   3 CHAIN: A;
COMPND   4 FRAGMENT: CRAMBIN
SOURCE    MOL_ID: 1;
SOURCE   2 ORGANISM_SCIENTIFIC: CRAMBE HISPANICA SUBSP. ABYSSINICA;
SOURCE   3 ORGANISM_TAXID: 3721;
SOURCE   4 STRAIN: SUBSP. ABYSSINICA
KEYWDS    VALENCE ELECTRON DENSITY, MULTI-SUBSTATE, MULTIPOLE REFINEMENT, PLANT
KEYWDS   2 PROTEIN
EXPDTA    X-RAY DIFFRACTION
AUTHOR    C.JELSCH,M.M.TEETER,V.LAMZIN,V.PICHON-LESME,B.BLESSING,C.LECOMTE
REVDAT   8   30-OCT-24 1EJG    1       REMARK SEQADV
REVDAT   7   04-OCT-17 1EJG    1       REMARK
REVDAT   6   05-FEB-14 1EJG    1       ATOM   CONECT
REVDAT   5   13-JUL-11 1EJG    1       VERSN
REVDAT   4   24-FEB-09 1EJG    1       VERSN
REVDAT   3   01-APR-03 1EJG    1       JRNL
REVDAT   2   10-MAY-00 1EJG    1       COMPND ATOM
REVDAT   1   05-APR-00 1EJG    0
JRNL        AUTH   C.JELSCH,M.M.TEETER,V.LAMZIN,V.PICHON-PESME,R.H.BLESSING,
JRNL        AUTH 2 C.LECOMTE
JRNL        TITL   ACCURATE PROTEIN CRYSTALLOGRAPHY AT ULTRA-HIGH RESOLUTION:
JRNL        TITL 2 VALENCE ELECTRON DISTRIBUTION IN CRAMBIN.
JRNL        REF    PROC.NATL.ACAD.SCI.USA        V.  97  3171 2000
JRNL        REFN                   ISSN 0027-8424
JRNL        PMID   10737790
JRNL        DOI    10.1073/PNAS.97.7.3171
REMARK   2
REMARK   2 RESOLUTION.    0.54 ANGSTROMS.
REMARK   3
REMARK   3 REFINEMENT.
REMARK   3   PROGRAM     : MOLLY
REMARK   3   AUTHORS     : NULL
REMARK   3
REMARK   3  DATA USED IN REFINEMENT.
REMARK   3   RESOLUTION RANGE HIGH (ANGSTROMS) : 0.54
REMARK   3   RESOLUTION RANGE LOW  (ANGSTROMS) : 22.37
REMARK   3   DATA CUTOFF            (SIGMA(F)) : 0.000
REMARK   3   DATA CUTOFF HIGH         (ABS(F)) : NULL
REMARK   3   DATA CUTOFF LOW          (ABS(F)) : NULL
REMARK   3   COMPLETENESS (WORKING+TEST)   (%) : 97.6
REMARK   3   NUMBER OF REFLECTIONS             : 100989
REMARK   3
REMARK   3  FIT TO DATA USED IN REFINEMENT.
REMARK   3   CROSS-VALIDATION METHOD          : NULL
REMARK   3   FREE R VALUE TEST SET SELECTION  : 1 REFLECTION OUT OF 20
REMARK   3   R VALUE            (WORKING SET) : 0.090
REMARK   3   FREE R VALUE                     : 0.094
REMARK   3   FREE R VALUE TEST SET SIZE   (%) : 5.000
REMARK   3   FREE R VALUE TEST SET COUNT      : 11220
REMARK   3   ESTIMATED ERROR OF FREE R VALUE  : NULL
REMARK   3
REMARK   3  FIT IN THE HIGHEST RESOLUTION BIN.
REMARK   3   TOTAL NUMBER OF BINS USED           : NULL
REMARK   3   BIN RESOLUTION RANGE HIGH       (A) : 0.54
REMARK   3   BIN RESOLUTION RANGE LOW        (A) : 0.57
REMARK   3   BIN COMPLETENESS (WORKING+TEST) (%) : NULL
REMARK   3   REFLECTIONS IN BIN    (WORKING SET) : 17547
REMARK   3   BIN R VALUE           (WORKING SET) : 0.1970
REMARK   3   BIN FREE R VALUE                    : 0.2050
REMARK   3   BIN FREE R VALUE TEST SET SIZE  (%) : 5.00
REMARK   3   BIN FREE R VALUE TEST SET COUNT     : NULL
REMARK   3   ESTIMATED ERROR OF BIN FREE R VALUE : NULL
REMARK   3
REMARK   3  NUMBER OF NON-HYDROGEN ATOMS USED IN REFINEMENT.
REMARK   3   PROTEIN ATOMS            : 340
REMARK   3   NUCLEIC ACID ATOMS       : 0
REMARK   3   HETEROGEN ATOMS          : 0
REMARK   3   SOLVENT ATOMS            : 0
REMARK   3
REMARK   3  B VALUES.
REMARK   3   FROM WILSON PLOT           (A**2) : 2.80
REMARK   3   MEAN B VALUE      (OVERALL, A**2) : NULL
REMARK   3   OVERALL ANISOTROPIC B VALUE.
REMARK   3    B11 (A**2) : NULL
REMARK   3    B22 (A**2) : NULL
REMARK   3    B33 (A**2) : NULL
REMARK   3    B12 (A**2) : NULL
REMARK   3    B13 (A**2) : NULL
REMARK   3    B23 (A**2) : NULL
REMARK   3
REMARK   3  ESTIMATED COORDINATE ERROR.
REMARK   3   ESD FROM LUZZATI PLOT        (A) : NULL
REMARK   3   ESD FROM SIGMAA              (A) : NULL
REMARK   3   LOW RESOLUTION CUTOFF        (A) : NULL
REMARK   3
REMARK   3  CROSS-VALIDATED ESTIMATED COORDINATE ERROR.
REMARK   3   ESD FROM C-V LUZZATI PLOT    (A) : NULL
REMARK   3   ESD FROM C-V SIGMAA          (A) : NULL
REMARK   3
REMARK   3  RMS DEVIATIONS FROM IDEAL VALUES.
REMARK   3   BOND LENGTHS                 (A) : 0.023
REMARK   3   BOND ANGLES            (DEGREES) : 2.700
REMARK   3   DIHEDRAL ANGLES        (DEGREES) : NULL
REMARK   3   IMPROPER ANGLES        (DEGREES) : NULL
REMARK   3
REMARK   3  ISOTROPIC THERMAL MODEL : NULL
REMARK   3
REMARK   3  ISOTROPIC THERMAL FACTOR RESTRAINTS.    RMS    SIGMA
REMARK   3   MAIN-CHAIN BOND              (A**2) : NULL  ; NULL
REMARK   3   MAIN-CHAIN ANGLE             (A**2) : NULL  ; NULL
REMARK   3   SIDE-CHAIN BOND              (A**2) : NULL  ; NULL
REMARK   3   SIDE-CHAIN ANGLE             (A**2) : NULL  ; NULL
REMARK   3
REMARK   3  NCS MODEL : NULL
REMARK   3
REMARK   3  NCS RESTRAINTS.                         RMS   SIGMA/WEIGHT
REMARK   3   GROUP  1  POSITIONAL            (A) : NULL  ; NULL
REMARK   3   GROUP  1  B-FACTOR           (A**2) : NULL  ; NULL
REMARK   3
REMARK   3  PARAMETER FILE  1  : SHELXL97 DICTIONARY
REMARK   3  PARAMETER FILE  2  : NULL
REMARK   3  TOPOLOGY FILE  1   : NULL
REMARK   3  TOPOLOGY FILE  2   : NULL
REMARK   3
REMARK   3  OTHER REFINEMENT REMARKS: SHELX97 FOLLOWED BY MOLLY (N.K.HANSEN &
REMARK   3  P.COPPENS ACTA CRYSTALLOGR. A34, 909-921) REFINEMENT OF ELECTRON
REMARK   3  DENSITY.
REMARK   4
REMARK   4 1EJG COMPLIES WITH FORMAT V. 3.30, 13-JUL-11
REMARK 100
REMARK 100 THIS ENTRY HAS BEEN PROCESSED BY RCSB ON 06-MAR-00.
REMARK 100 THE DEPOSITION ID IS D_1000010638.
REMARK 200
REMARK 200 EXPERIMENTAL DETAILS
REMARK 200  EXPERIMENT TYPE                : X-RAY DIFFRACTION
REMARK 200  DATE OF DATA COLLECTION        : 31-MAY-97
REMARK 200  TEMPERATURE           (KELVIN) : 100.0
REMARK 200  PH                             : 7
REMARK 200  NUMBER OF CRYSTALS USED        : 1
REMARK 200
REMARK 200  SYNCHROTRON              (Y/N) : Y
REMARK 200  RADIATION SOURCE               : EMBL/DESY, HAMBURG
REMARK 200  BEAMLINE                       : BW7A
REMARK 200  X-RAY GENERATOR MODEL          : NULL
REMARK 200  MONOCHROMATIC OR LAUE    (M/L) : M
REMARK 200  WAVELENGTH OR RANGE        (A) : 0.54
REMARK 200  MONOCHROMATOR                  : NULL
REMARK 200  OPTICS                         : NULL
REMARK 200
REMARK 200  DETECTOR TYPE                  : IMAGE PLATE
REMARK 200  DETECTOR MANUFACTURER          : MARRESEARCH
REMARK 200  INTENSITY-INTEGRATION SOFTWARE : DREAR
REMARK 200  DATA SCALING SOFTWARE          : DREAR
REMARK 200
REMARK 200  NUMBER OF UNIQUE REFLECTIONS   : 79868
REMARK 200  RESOLUTION RANGE HIGH      (A) : 0.540
REMARK 200  RESOLUTION RANGE LOW       (A) : 50.000
REMARK 200  REJECTION CRITERIA  (SIGMA(I)) : 3.000
REMARK 200
REMARK 200 OVERALL.
REMARK 200  COMPLETENESS FOR RANGE     (%) : 97.6
REMARK 200  DATA REDUNDANCY                : 4.500
REMARK 200  R MERGE                    (I) : 0.05500
REMARK 200  R SYM                      (I) : NULL
REMARK 200  <I/SIGMA(I)> FOR THE DATA SET  : 8.2000
REMARK 200
REMARK 200 IN THE HIGHEST RESOLUTION SHELL.
REMARK 200  HIGHEST RESOLUTION SHELL, RANGE HIGH (A) : 0.54
REMARK 200  HIGHEST RESOLUTION SHELL, RANGE LOW  (A) : 0.55
REMARK 200  COMPLETENESS FOR SHELL     (%) : 100.0
REMARK 200  DATA REDUNDANCY IN SHELL       : 3.80
REMARK 200  R MERGE FOR SHELL          (I) : 0.14760
REMARK 200  R SYM FOR SHELL            (I) : NULL
REMARK 200  <I/SIGMA(I)> FOR SHELL         : NULL
REMARK 200
REMARK 200 DIFFRACTION PROTOCOL: SINGLE WAVELENGTH
REMARK 200 METHOD USED TO DETERMINE THE STRUCTURE: NULL
REMARK 200 SOFTWARE USED: ALREADY SOLVED
REMARK 200 STARTING MODEL: NULL
REMARK 200
REMARK 200 REMARK: NULL
REMARK 280
REMARK 280 CRYSTAL
REMARK 280 SOLVENT CONTENT, VS   (%): 30.00
REMARK 280 MATTHEWS COEFFICIENT, VM (ANGSTROMS**3/DA): 1.40
REMARK 280
REMARK 280 CRYSTALLIZATION CONDITIONS: THE PROTEIN (40 MG/ML IN 80% ETHANOL)
REMARK 280  IS EQUILIBRATED AGAINST 60% ETHANOL. NOT BUFFERED., PH 7, VAPOR
REMARK 280  DIFFUSION, SITTING DROP, TEMPERATURE 293K
REMARK 290
REMARK 290 CRYSTALLOGRAPHIC SYMMETRY
REMARK 290 SYMMETRY OPERATORS FOR SPACE GROUP: P 1 21 1
REMARK 290
REMARK 290      SYMOP   SYMMETRY
REMARK 290     NNNMMM   OPERATOR
REMARK 290       1555   X,Y,Z
REMARK 290       2555   -X,Y+1/2,-Z
REMARK 290
REMARK 290     WHERE NNN -> OPERATOR NUMBER
REMARK 290           MMM -> TRANSLATION VECTOR
REMARK 290
REMARK 290 CRYSTALLOGRAPHIC SYMMETRY TRANSFORMATIONS
REMARK 290 THE FOLLOWING TRANSFORMATIONS OPERATE ON THE ATOM/HETATM
REMARK 290 RECORDS IN THIS ENTRY TO PRODUCE CRYSTALLOGRAPHICALLY
REMARK 290 RELATED MOLECULES.
REMARK 290   SMTRY1   1  1.000000  0.000000  0.000000        0.00000
REMARK 290   SMTRY2   1  0.000000  1.000000  0.000000        0.00000
REMARK 290   SMTRY3   1  0.000000  0.000000  1.000000        0.00000
REMARK 290   SMTRY1   2 -1.000000  0.000000  0.000000        0.00000
REMARK 290   SMTRY2   2  0.000000  1.000000  0.000000        9.24900
REMARK 290   SMTRY3   2  0.000000  0.000000 -1.000000        0.00000
REMARK 290
REMARK 290 REMARK: NULL
REMARK 300
REMARK 300 BIOMOLECULE: 1
REMARK 300 SEE REMARK 350 FOR THE AUTHOR PROVIDED AND/OR PROGRAM
REMARK 300 GENERATED ASSEMBLY INFORMATION FOR THE STRUCTURE IN
REMARK 300 THIS ENTRY. THE REMARK MAY ALSO PROVIDE INFORMATION ON
REMARK 300 BURIED SURFACE AREA.
REMARK 350
REMARK 350 COORDINATES FOR A COMPLETE MULTIMER REPRESENTING THE KNOWN
REMARK 350 BIOLOGICALLY SIGNIFICANT OLIGOMERIZATION STATE OF THE
REMARK 350 MOLECULE CAN BE GENERATED BY APPLYING BIOMT TRANSFORMATIONS
REMARK 350 GIVEN BELOW.  BOTH NON-CRYSTALLOGRAPHIC AND
REMARK 350 CRYSTALLOGRAPHIC OPERATIONS ARE GIVEN.
REMARK 350
REMARK 350 BIOMOLECULE: 1
REMARK 350 AUTHOR DETERMINED BIOLOGICAL UNIT: MONOMERIC
REMARK 350 APPLY THE FOLLOWING TO CHAINS: A
REMARK 350   BIOMT1   1  1.000000  0.000000  0.000000        0.00000
REMARK 350   BIOMT2   1  0.000000  1.000000  0.000000        0.00000
REMARK 350   BIOMT3   1  0.000000  0.000000  1.000000        0.00000
REMARK 470
REMARK 470 MISSING ATOM
REMARK 470 THE FOLLOWING RESIDUES HAVE MISSING ATOMS (M=MODEL NUMBER;
REMARK 470 RES=RESIDUE NAME; C=CHAIN IDENTIFIER; SSEQ=SEQUENCE NUMBER;
REMARK 470 I=INSERTION CODE):
REMARK 470   M RES CSSEQI  ATOMS
REMARK 470     PRO A  22    N
REMARK 500
REMARK 500 GEOMETRY AND STEREOCHEMISTRY
REMARK 500 SUBTOPIC: CLOSE CONTACTS IN SAME ASYMMETRIC UNIT
REMARK 500
REMARK 500 THE FOLLOWING ATOMS ARE IN CLOSE CONTACT.
REMARK 500
REMARK 500  ATM1  RES C  SSEQI   ATM2  RES C  SSEQI           DISTANCE
REMARK 500   N    PRO A    22     CA   SER A    22              1.39
REMARK 500   N    PRO A    22     CA   SER A    22              1.60
REMARK 500
REMARK 500 REMARK: NULL
REMARK 500
REMARK 500 GEOMETRY AND STEREOCHEMISTRY
REMARK 500 SUBTOPIC: COVALENT BOND ANGLES
REMARK 500
REMARK 500 THE STEREOCHEMICAL PARAMETERS OF THE FOLLOWING RESIDUES
REMARK 500 HAVE VALUES WHICH DEVIATE FROM EXPECTED VALUES BY MORE
REMARK 500 THAN 6*RMSD (M=MODEL NUMBER; RES=RESIDUE NAME; C=CHAIN
REMARK 500 IDENTIFIER; SSEQ=SEQUENCE NUMBER; I=INSERTION CODE).
REMARK 500
REMARK 500 STANDARD TABLE:
REMARK 500 FORMAT: (10X,I3,1X,A3,1X,A1,I4,A1,3(1X,A4,2X),12X,F5.1)
REMARK 500
REMARK 500 EXPECTED VALUES PROTEIN: ENGH AND HUBER, 1999
REMARK 500 EXPECTED VALUES NUCLEIC ACID: CLOWNEY ET AL 1996
REMARK 500
REMARK 500  M RES CSSEQI ATM1   ATM2   ATM3
REMARK 500    THR A   1   CA  -  CB  -  OG1 ANGL. DEV. =  13.1 DEGREES
REMARK 500    ARG A  10   NE  -  CZ  -  NH1 ANGL. DEV. =   6.3 DEGREES
REMARK 500    SER A  22   CA  -  C   -  O   ANGL. DEV. =  14.1 DEGREES
REMARK 500    SER A  22   O   -  C   -  N   ANGL. DEV. = -13.1 DEGREES
REMARK 500    TYR A  29   CB  -  CG  -  CD2 ANGL. DEV. =  -8.4 DEGREES
REMARK 500    TYR A  29   CB  -  CG  -  CD1 ANGL. DEV. =   7.9 DEGREES
REMARK 500    TYR A  29   CG  -  CD1 -  CE1 ANGL. DEV. =   5.7 DEGREES
REMARK 500    THR A  39   CA  -  CB  -  CG2 ANGL. DEV. =  -9.8 DEGREES
REMARK 500    ASP A  43   CA  -  CB  -  CG  ANGL. DEV. =  13.5 DEGREES
REMARK 500
REMARK 500 REMARK: NULL
REMARK 500
REMARK 500 GEOMETRY AND STEREOCHEMISTRY
REMARK 500 SUBTOPIC: MAIN CHAIN PLANARITY
REMARK 500
REMARK 500 THE FOLLOWING RESIDUES HAVE A PSEUDO PLANARITY
REMARK 500 TORSION ANGLE, C(I) - CA(I) - N(I+1) - O(I), GREATER
REMARK 500 10.0 DEGREES. (M=MODEL NUMBER; RES=RESIDUE NAME;
REMARK 500 C=CHAIN IDENTIFIER; SSEQ=SEQUENCE NUMBER;
REMARK 500 I=INSERTION CODE).
REMARK 500
REMARK 500  M RES CSSEQI        ANGLE
REMARK 500    SER A  22        -10.62
REMARK 500
REMARK 500 REMARK: NULL
REMARK 900
REMARK 900 RELATED ENTRIES
REMARK 900 RELATED ID: 1CBN   RELATED DB: PDB
REMARK 900 CRAMBIN AT 130K AND 0.83 A. TWO SEQUENCE FORMS.
REMARK 900 RELATED ID: 1CRN   RELATED DB: PDB
REMARK 900 CRAMBIN AT 1.5 A AND ROOM TEMPERATURE. TWO SEQUENCE FORMS.
REMARK 900 RELATED ID: 1AB1   RELATED DB: PDB
REMARK 900 CRAMBIN AT 150 K IN THE PURE SER22/ILE25 SEQUENCE FORMS.
REMARK 900 RELATED ID: 1CNR   RELATED DB: PDB
REMARK 900 CRAMBIN AT 150K AND 1.05 A RESOLUTION. PURE PRO22/LEU25 FORM OF
REMARK 900 CRAMBIN.
DBREF  1EJG A    1    46  UNP    P01542   CRAM_CRAAB       1     46
SEQADV 1EJG SER A   22  UNP  P01542    PRO    22 MICROHETEROGENEITY
SEQADV 1EJG ILE A   25  UNP  P01542    LEU    25 MICROHETEROGENEITY
SEQRES   1 A   46  THR THR CYS CYS PRO SER ILE VAL ALA ARG SER ASN PHE
SEQRES   2 A   46  ASN VAL CYS ARG LEU PRO GLY THR PRO GLU ALA LEU CYS
SEQRES   3 A   46  ALA THR TYR THR GLY CYS ILE ILE ILE PRO GLY ALA THR
SEQRES   4 A   46  CYS PRO GLY ASP TYR ALA ASN
HELIX    1   1 SER A    6  LEU A   18  1                                  13
HELIX    2   2 PRO A   22  GLY A   31  1                                  10
SHEET    1   A 2 THR A   2  CYS A   3  0
SHEET    2   A 2 ILE A  33  ILE A  34 -1  O  ILE A  33   N  CYS A   3
SSBOND   1 CYS A    3    CYS A   40                          1555   1555  2.03
SSBOND   2 CYS A    4    CYS A   32                          1555   1555  2.05
SSBOND   3 CYS A   16    CYS A   26                          1555   1555  2.04
CRYST1   40.824   18.498   22.371  90.00  90.47  90.00 P 1 21 1      2
ORIGX1      1.000000  0.000000  0.000000        0.00000
ORIGX2      0.000000  1.000000  0.000000        0.00000
ORIGX3      0.000000  0.000000  1.000000        0.00000
SCALE1      0.024495  0.000000  0.000201        0.00000
SCALE2      0.000000  0.054060  0.000000        0.00000
SCALE3      0.000000  0.000000  0.044702        0.00000
ATOM      1  N  ATHR A   1      16.885  14.078   3.427  0.82  4.48           N
ANISOU    1  N  ATHR A   1      434    531    735    201    133    -28       N
ATOM      2  N  BTHR A   1      17.553  14.234   4.214  0.18  5.51           N
ATOM      3  CA ATHR A   1      16.938  12.834   4.234  0.82  3.12           C
ANISOU    3  CA ATHR A   1      305    437    441     39    103    -65       C
ATOM      4  CA BTHR A   1      16.985  12.901   4.228  0.18 16.71           C
ATOM      5  C   THR A   1      15.642  12.760   4.985  1.00  3.28           C
ANISOU    5  C   THR A   1      338    431    477    -32    137    -43       C
ATOM      6  O   THR A   1      15.150  13.818   5.439  1.00  5.91           O
ANISOU    6  O   THR A   1      476    455   1311   -213    289    -42       O
ATOM      7  CB ATHR A   1      18.103  12.875   5.202  0.82  4.05           C
ANISOU    7  CB ATHR A   1      249    662    627     23     60   -110       C
ATOM      8  CB BTHR A   1      17.983  11.950   4.917  0.18  8.95           C
ATOM      9  OG1ATHR A   1      19.256  13.004   4.401  0.82  5.75           O
ANISOU    9  OG1ATHR A   1      294   1049    842    134    158   -125       O
ATOM     10  OG1BTHR A   1      17.792  10.543   4.939  0.18  9.94           O
ATOM     11  CG2ATHR A   1      18.173  11.582   6.055  0.82  5.30           C
ANISOU   11  CG2ATHR A   1      343    850    818    215    -11    -32       C
ATOM     12  CG2BTHR A   1      18.117  12.174   6.499  0.18  6.78           C
ATOM     13  H1 ATHR A   1      17.705  14.139   2.840  0.82  6.68           H
ATOM     14  H1 BTHR A   1      18.510  14.188   3.898  0.18  7.89           H
ATOM     15  H2 ATHR A   1      16.879  14.894   4.049  0.82  6.68           H
ATOM     16  H2 BTHR A   1      17.525  14.622   5.144  0.18  7.89           H
ATOM     17  H3 ATHR A   1      16.057  14.105   2.859  0.82  6.68           H
ATOM     18  H3 BTHR A   1      17.021  14.820   3.588  0.18  7.89           H
ATOM     19  HA ATHR A   1      17.013  11.969   3.577  0.82  3.83           H
ATOM     20  HA BTHR A   1      16.841  12.569   3.191  0.18  6.31           H
ATOM     21  HB ATHR A   1      17.995  13.758   5.848  0.82  4.83           H
ATOM     22  HB BTHR A   1      18.972  12.139   4.475  0.18  6.31           H
ATOM     23  HG1ATHR A   1      19.852  13.644   4.803  0.82  8.74           H
ATOM     24  HG1BTHR A   1      17.772  10.206   4.033  0.18  7.89           H
ATOM     25 HG21ATHR A   1      19.024  11.659   6.737  0.82  7.89           H
ATOM     26 HG21BTHR A   1      17.805  11.261   7.025  0.18  7.89           H
ATOM     27 HG22ATHR A   1      18.290  10.718   5.396  0.82  7.89           H
ATOM     28 HG22BTHR A   1      17.475  13.012   6.806  0.18  7.89           H
ATOM     29 HG23ATHR A   1      17.241  11.481   6.636  0.82  7.89           H
ATOM     30 HG23BTHR A   1      19.162  12.403   6.749  0.18  7.89           H
ATOM     31  N   THR A   2      15.069  11.586   5.134  1.00  2.84           N
ANISOU   31  N   THR A   2      325    445    309    -46    132    -59       N
ATOM     32  CA ATHR A   2      13.856  11.498   5.932  0.67  2.54           C
ANISOU   32  CA ATHR A   2      266    380    316     18     89    -29       C
ATOM     33  CA BTHR A   2      13.843  11.266   5.843  0.33  2.68           C
ANISOU   33  CA BTHR A   2      243    500    273    -18     30    -90       C
ATOM     34  C   THR A   2      14.172  10.757   7.221  1.00  2.52           C
ANISOU   34  C   THR A   2      244    442    270     -3     84    -20       C
ATOM     35  O   THR A   2      15.006   9.857   7.315  1.00  3.12           O
ANISOU   35  O   THR A   2      321    531    334    -22    120     69       O
ATOM     36  CB ATHR A   2      12.785  10.742   5.129  0.67  4.28           C
ANISOU   36  CB ATHR A   2      380    828    416    222    -76   -280       C
ATOM     37  CB BTHR A   2      13.014  10.211   5.070  0.33  6.00           C
ANISOU   37  CB BTHR A   2      455   1292    533   -381     15   -400       C
ATOM     38  OG1ATHR A   2      13.312   9.437   4.770  0.67  5.18           O
ANISOU   38  OG1ATHR A   2     1082    608    278     52    -81   -546       O
ATOM     39  OG1BTHR A   2      12.661  10.876   3.761  0.33  7.04           O
ANISOU   39  OG1BTHR A   2      776   1532    368   -344    167   -537       O
ATOM     40  CG2ATHR A   2      12.315  11.612   3.973  0.67  5.81           C
ANISOU   40  CG2ATHR A   2      696   1012    497    311   -225   -310       C
ATOM     41  CG2BTHR A   2      11.751   9.803   5.800  0.33 11.66           C
ANISOU   41  CG2BTHR A   2      770   2618   1042    468     28   -955       C
ATOM     42  H   THR A   2      15.465  10.769   4.694  1.00  3.42           H
ATOM     43  HA ATHR A   2      13.508  12.532   6.154  0.67  3.05           H
ATOM     44  HA BTHR A   2      13.237  12.147   5.938  0.33  3.42           H
ATOM     45  HB ATHR A   2      11.925  10.594   5.819  0.67  5.10           H
ATOM     46  HB BTHR A   2      13.558   9.302   4.866  0.33  7.43           H
ATOM     47  HG1ATHR A   2      14.200   9.345   5.125  0.67  7.86           H
ATOM     48  HG1BTHR A   2      13.454  11.073   3.278  0.33 11.01           H
ATOM     49 HG21ATHR A   2      11.570  11.067   3.373  0.67  8.54           H
ATOM     50 HG21BTHR A   2      11.118   9.118   5.255  0.33 16.13           H
ATOM     51 HG22ATHR A   2      13.159  11.901   3.347  0.67  8.54           H
ATOM     52 HG22BTHR A   2      11.082  10.771   5.953  0.33 16.13           H
ATOM     53 HG23ATHR A   2      11.828  12.539   4.368  0.67  8.54           H
ATOM     54 HG23BTHR A   2      11.949   9.454   6.810  0.33 16.13           H
ATOM     55  N   CYS A   3      13.438  11.192   8.264  1.00  2.26           N
ANISOU   55  N   CYS A   3      254    330    274     18     95    -33       N
ATOM     56  CA  CYS A   3      13.607  10.675   9.600  1.00  2.06           C
ANISOU   56  CA  CYS A   3      223    287    270      2     80    -69       C
ATOM     57  C   CYS A   3      12.210  10.413  10.164  1.00  1.94           C
ANISOU   57  C   CYS A   3      214    221    301     -6     89    -42       C
ATOM     58  O   CYS A   3      11.324  11.246   9.996  1.00  2.78           O
ANISOU   58  O   CYS A   3      284    240    529     99    166      4       O
ATOM     59  CB  CYS A   3      14.300  11.703  10.523  1.00  2.35           C
ANISOU   59  CB  CYS A   3      271    295    327    -12     52    -77       C
ATOM     60  SG  CYS A   3      15.846  12.374   9.880  1.00  3.32           S
ANISOU   60  SG  CYS A   3      336    478    449    125      9   -211       S
ATOM     61  H   CYS A   3      12.743  11.906   8.104  1.00  2.71           H
ATOM     62  HA  CYS A   3      14.185   9.741   9.573  1.00  2.47           H
ATOM     63  HB2 CYS A   3      13.605  12.535  10.703  1.00  2.81           H
ATOM     64  HB3 CYS A   3      14.502  11.224  11.491  1.00  2.81           H
ATOM     65  N   CYS A   4      12.015   9.277  10.850  1.00  1.74           N
ANISOU   65  N   CYS A   4      187    240    231     -8     66    -40       N
ATOM     66  CA  CYS A   4      10.681   8.944  11.326  1.00  1.60           C
ANISOU   66  CA  CYS A   4      172    211    225     -2     52    -36       C
ATOM     67  C   CYS A   4      10.683   8.745  12.838  1.00  1.63           C
ANISOU   67  C   CYS A   4      168    226    222     -6     45    -26       C
ATOM     68  O   CYS A   4      11.651   8.272  13.418  1.00  2.08           O
ANISOU   68  O   CYS A   4      184    337    267      5     31     14       O
ATOM     69  CB  CYS A   4      10.155   7.684  10.617  1.00  1.78           C
ANISOU   69  CB  CYS A   4      237    216    222     -6     35    -45       C
ATOM     70  SG  CYS A   4       9.833   7.934   8.843  1.00  2.03           S
ANISOU   70  SG  CYS A   4      303    238    229    -52     41    -26       S
ATOM     71  H   CYS A   4      12.789   8.657  11.035  1.00  2.08           H
ATOM     72  HA  CYS A   4      10.009   9.781  11.088  1.00  1.93           H
ATOM     73  HB2 CYS A   4      10.891   6.876  10.734  1.00  2.14           H
ATOM     74  HB3 CYS A   4       9.225   7.362  11.105  1.00  2.14           H
ATOM     75  N   PRO A   5       9.546   9.093  13.475  1.00  1.64           N
ANISOU   75  N   PRO A   5      178    227    218    -10     50    -22       N
ATOM     76  CA  PRO A   5       9.500   9.079  14.937  1.00  1.85           C
ANISOU   76  CA  PRO A   5      216    270    214    -47     45    -74       C
ATOM     77  C   PRO A   5       9.373   7.688  15.546  1.00  2.01           C
ANISOU   77  C   PRO A   5      264    304    195     -5     30    -52       C
ATOM     78  O   PRO A   5       9.640   7.542  16.748  1.00  3.15           O
ANISOU   78  O   PRO A   5      544    447    203     11    -23   -132       O
ATOM     79  CB  PRO A   5       8.267   9.939  15.267  1.00  2.28           C
ANISOU   79  CB  PRO A   5      307    306    252    -66    114    -31       C
ATOM     80  CG  PRO A   5       7.364   9.742  14.044  1.00  2.26           C
ANISOU   80  CG  PRO A   5      199    335    322    -14     96     13       C
ATOM     81  CD  PRO A   5       8.360   9.748  12.898  1.00  1.83           C
ANISOU   81  CD  PRO A   5      184    251    258     -6     56      2       C
ATOM     82  HA  PRO A   5      10.401   9.568  15.334  1.00  2.21           H
ATOM     83  HB2 PRO A   5       7.773   9.587  16.184  1.00  2.72           H
ATOM     84  HB3 PRO A   5       8.542  10.995  15.390  1.00  2.72           H
ATOM     85  HG2 PRO A   5       6.823   8.787  14.098  1.00  2.70           H
ATOM     86  HG3 PRO A   5       6.640  10.563  13.947  1.00  2.70           H
ATOM     87  HD2 PRO A   5       7.976   9.183  12.037  1.00  2.19           H
ATOM     88  HD3 PRO A   5       8.590  10.774  12.580  1.00  2.19           H
ATOM     89  N   SER A   6       8.926   6.705  14.756  1.00  1.84           N
ANISOU   89  N   SER A   6      232    268    198     15     19    -46       N
ATOM     90  CA  SER A   6       8.755   5.347  15.231  1.00  1.70           C
ANISOU   90  CA  SER A   6      207    255    183     21     26     15       C
ATOM     91  C   SER A   6       8.832   4.429  14.008  1.00  1.84           C
ANISOU   91  C   SER A   6      215    281    200      3     41     37       C
ATOM     92  O   SER A   6       8.757   4.867  12.860  1.00  2.14           O
ANISOU   92  O   SER A   6      284    326    200     19     54     23       O
ATOM     93  CB  SER A   6       7.409   5.161  15.930  1.00  1.78           C
ANISOU   93  CB  SER A   6      248    219    206     13     67      5       C
ATOM     94  OG  SER A   6       6.371   5.265  14.953  1.00  2.15           O
ANISOU   94  OG  SER A   6      201    330    283     60     59      2       O
ATOM     95  H   SER A   6       8.700   6.916  13.796  1.00  2.20           H
ATOM     96  HA  SER A   6       9.567   5.098  15.928  1.00  2.03           H
ATOM     97  HB2 SER A   6       7.371   4.176  16.415  1.00  2.13           H
ATOM     98  HB3 SER A   6       7.277   5.932  16.702  1.00  2.13           H
ATOM     99  HG  SER A   6       5.560   4.870  15.300  1.00  3.21           H
ATOM    100  N   ILE A   7       8.936   3.129  14.302  1.00  2.20           N
ANISOU  100  N   ILE A   7      350    283    202    -11     40    105       N
ATOM    101  CA AILE A   7       8.829   2.039  13.300  0.55  2.58           C
ANISOU  101  CA AILE A   7      516    264    200     -6    151     84       C
ATOM    102  CA BILE A   7       9.104   2.209  13.197  0.45  2.14           C
ANISOU  102  CA BILE A   7      381    195    233      9    131     47       C
ATOM    103  C  AILE A   7       7.559   2.141  12.460  0.55  2.53           C
ANISOU  103  C  AILE A   7      595    230    137     20    117    131       C
ATOM    104  C  BILE A   7       7.839   2.105  12.369  0.45  2.15           C
ANISOU  104  C  BILE A   7      396    209    211   -103    150    -38       C
ATOM    105  O  AILE A   7       7.573   2.124  11.205  0.55  2.78           O
ANISOU  105  O  AILE A   7      602    310    145     24    113    111       O
ATOM    106  O  BILE A   7       7.990   2.102  11.154  0.45  2.53           O
ANISOU  106  O  BILE A   7      359    395    206   -115    130   -115       O
ATOM    107  CB AILE A   7       8.928   0.644  13.932  0.55  3.24           C
ANISOU  107  CB AILE A   7      571    217    440     -4    180    112       C
ATOM    108  CB BILE A   7       9.491   0.865  13.815  0.45  2.71           C
ANISOU  108  CB BILE A   7      506    148    373    -28     88     72       C
ATOM    109  CG1AILE A   7      10.309   0.385  14.573  0.55  5.58           C
ANISOU  109  CG1AILE A   7      545    414   1161     51    125    259       C
ATOM    110  CG1BILE A   7      10.981   0.969  14.362  0.45  3.52           C
ANISOU  110  CG1BILE A   7      451    354    532    134    107    211       C
ATOM    111  CG2AILE A   7       8.510  -0.464  12.908  0.55  4.24           C
ANISOU  111  CG2AILE A   7      843    247    518    -70    159    109       C
ATOM    112  CG2BILE A   7       9.389  -0.211  12.797  0.45  4.65           C
ANISOU  112  CG2BILE A   7      943    293    527   -181    -35    169       C
ATOM    113  CD1AILE A   7      11.430   0.295  13.473  0.55  7.60           C
ANISOU  113  CD1AILE A   7      582    653   1651   -377    357    116       C
ATOM    114  CD1BILE A   7      11.345  -0.312  15.110  0.45  4.98           C
ANISOU  114  CD1BILE A   7      834    563    496    251    159    405       C
ATOM    115  H   ILE A   7       9.078   2.878  15.269  1.00  2.65           H
ATOM    116  HA AILE A   7       9.714   2.123  12.623  0.55  3.11           H
ATOM    117  HA BILE A   7       9.909   2.595  12.552  0.45  2.54           H
ATOM    118  HB AILE A   7       8.200   0.598  14.759  0.55  3.92           H
ATOM    119  HB BILE A   7       8.815   0.671  14.655  0.45  3.28           H
ATOM    120 HG12AILE A   7      10.550   1.170  15.240  0.55  6.88           H
ATOM    121 HG12BILE A   7      11.630   1.137  13.512  0.45  4.23           H
ATOM    122 HG13AILE A   7      10.274  -0.579  15.106  0.55  6.88           H
ATOM    123 HG13BILE A   7      11.028   1.816  15.040  0.45  4.23           H
ATOM    124 HG21AILE A   7       7.863   0.004  12.146  0.55  6.50           H
ATOM    125 HG21BILE A   7       9.566  -1.189  13.311  0.45  7.18           H
ATOM    126 HG22AILE A   7       7.955  -1.251  13.426  0.55  6.50           H
ATOM    127 HG22BILE A   7      10.130  -0.079  12.019  0.45  7.18           H
ATOM    128 HG23AILE A   7       9.402  -0.873  12.434  0.55  6.50           H
ATOM    129 HG23BILE A   7       8.377  -0.228  12.371  0.45  7.18           H
ATOM    130 HD11AILE A   7      12.389   0.055  13.960  0.55 11.57           H
ATOM    131 HD11BILE A   7      12.440  -0.265  15.300  0.45  7.62           H
ATOM    132 HD12AILE A   7      11.499   1.217  12.922  0.55 11.57           H
ATOM    133 HD12BILE A   7      11.152  -1.180  14.450  0.45  7.62           H
ATOM    134 HD13AILE A   7      11.196  -0.544  12.761  0.55 11.57           H
ATOM    135 HD13BILE A   7      10.803  -0.391  16.024  0.45  7.62           H
ATOM    136  N  AVAL A   8       6.382   2.222  13.070  0.55  1.92           N
ANISOU  136  N  AVAL A   8      421    149    160     33    -23    -35       N
ATOM    137  N  BVAL A   8       6.695   2.072  13.037  0.45  1.88           N
ATOM    138  CA AVAL A   8       5.099   2.259  12.380  0.55  2.32           C
ANISOU  138  CA AVAL A   8      397    258    224     16    -22   -120       C
ATOM    139  CA BVAL A   8       5.471   2.048  12.164  0.45  1.94           C
ATOM    140  C   VAL A   8       5.208   3.386  11.373  1.00  2.63           C
ANISOU  140  C   VAL A   8      380    402    213     71    -42   -209       C
ATOM    141  O   VAL A   8       4.712   3.302  10.238  1.00  2.67           O
ANISOU  141  O   VAL A   8      378    434    200     39    -31   -178       O
ATOM    142  CB AVAL A   8       3.944   2.394  13.375  0.55  3.36           C
ANISOU  142  CB AVAL A   8      376    635    262    186      4   -244       C
ATOM    143  CB BVAL A   8       4.263   1.630  13.035  0.45  3.05           C
ATOM    144  CG1AVAL A   8       2.629   2.981  12.701  0.55  4.22           C
ANISOU  144  CG1AVAL A   8      326    856    420    159     34   -159       C
ATOM    145  CG1BVAL A   8       3.580   2.930  13.664  0.45  3.89           C
ATOM    146  CG2AVAL A   8       3.635   1.036  13.955  0.55  4.82           C
ANISOU  146  CG2AVAL A   8      771    684    376    230    -61   -385       C
ATOM    147  CG2BVAL A   8       3.136   1.077  12.028  0.45  4.17           C
ATOM    148  H  AVAL A   8       6.374   2.231  14.084  0.55  2.27           H
ATOM    149  H  BVAL A   8       6.648   2.059  14.045  0.45  5.91           H
ATOM    150  HA AVAL A   8       4.948   1.364  11.845  0.55  2.65           H
ATOM    151  HA BVAL A   8       5.622   1.256  11.418  0.45  5.91           H
ATOM    152  HB AVAL A   8       4.204   3.077  14.197  0.55  4.16           H
ATOM    153  HB BVAL A   8       4.536   0.891  13.800  0.45  5.91           H
ATOM    154 HG11AVAL A   8       2.862   3.979  12.286  0.55  6.22           H
ATOM    155 HG11BVAL A   8       2.659   2.642  14.189  0.45  7.38           H
ATOM    156 HG12AVAL A   8       1.845   3.103  13.478  0.55  6.22           H
ATOM    157 HG12BVAL A   8       3.337   3.640  12.861  0.45  7.38           H
ATOM    158 HG13AVAL A   8       2.286   2.318  11.926  0.55  6.22           H
ATOM    159 HG13BVAL A   8       4.275   3.401  14.373  0.45  7.38           H
ATOM    160 HG21AVAL A   8       4.536   0.671  14.467  0.55  7.38           H
ATOM    161 HG21BVAL A   8       2.262   0.744  12.605  0.45  7.38           H
ATOM    162 HG22AVAL A   8       3.367   0.343  13.145  0.55  7.38           H
ATOM    163 HG22BVAL A   8       3.540   0.231  11.455  0.45  7.38           H
ATOM    164 HG23AVAL A   8       2.805   1.098  14.673  0.55  7.38           H
ATOM    165 HG23BVAL A   8       2.836   1.878  11.338  0.45  7.38           H
ATOM    166  N   ALA A   9       5.668   4.556  11.848  1.00  2.19           N
ANISOU  166  N   ALA A   9      303    382    147     23     -5   -114       N
ATOM    167  CA  ALA A   9       5.637   5.732  10.997  1.00  1.92           C
ANISOU  167  CA  ALA A   9      219    314    195     -8     14     -7       C
ATOM    168  C   ALA A   9       6.496   5.510   9.742  1.00  1.64           C
ANISOU  168  C   ALA A   9      233    220    169     -6      8    -17       C
ATOM    169  O   ALA A   9       6.087   5.887   8.640  1.00  1.98           O
ANISOU  169  O   ALA A   9      284    267    198     19     -8     33       O
ATOM    170  CB  ALA A   9       6.088   6.968  11.772  1.00  2.30           C
ANISOU  170  CB  ALA A   9      305    295    273    -42     18     13       C
ATOM    171  H   ALA A   9       6.031   4.617  12.787  1.00  2.64           H
ATOM    172  HA  ALA A   9       4.599   5.892  10.675  1.00  2.30           H
ATOM    173  HB1 ALA A   9       5.450   7.098  12.658  1.00  3.45           H
ATOM    174  HB2 ALA A   9       6.005   7.855  11.128  1.00  3.45           H
ATOM    175  HB3 ALA A   9       7.132   6.841  12.089  1.00  3.45           H
ATOM    176  N   ARG A  10       7.685   4.898   9.905  1.00  1.59           N
ANISOU  176  N   ARG A  10      228    214    160     -6     -3    -23       N
ATOM    177  CA  ARG A  10       8.505   4.573   8.737  1.00  1.56           C
ANISOU  177  CA  ARG A  10      203    197    192     -2      2    -28       C
ATOM    178  C   ARG A  10       7.811   3.576   7.811  1.00  1.58           C
ANISOU  178  C   ARG A  10      218    210    170      0     -9    -18       C
ATOM    179  O   ARG A  10       7.840   3.742   6.580  1.00  1.79           O
ANISOU  179  O   ARG A  10      258    262    158      0      0    -15       O
ATOM    180  CB  ARG A  10       9.857   4.014   9.199  1.00  1.82           C
ANISOU  180  CB  ARG A  10      213    273    203    -14    -21    -17       C
ATOM    181  CG  ARG A  10      10.767   3.570   8.047  1.00  2.09           C
ANISOU  181  CG  ARG A  10      265    275    252    -40     14     -7       C
ATOM    182  CD  ARG A  10      11.272   4.693   7.139  1.00  2.37           C
ANISOU  182  CD  ARG A  10      302    349    246    -45     64    -50       C
ATOM    183  NE AARG A  10      12.137   5.620   7.824  0.67  2.14           N
ANISOU  183  NE AARG A  10      312    293    206      6     49    -48       N
ATOM    184  NE BARG A  10      12.206   5.472   8.032  0.33  2.43           N
ANISOU  184  NE BARG A  10      353    303    266    -13     64   -104       N
ATOM    185  CZ AARG A  10      12.683   6.719   7.295  0.67  2.69           C
ANISOU  185  CZ AARG A  10      452    275    294    -68    157   -106       C
ATOM    186  CZ BARG A  10      12.925   6.393   7.470  0.33  5.04           C
ANISOU  186  CZ BARG A  10      983    436    494     -9    255   -368       C
ATOM    187  NH1AARG A  10      12.436   7.053   6.053  0.67  3.34           N
ANISOU  187  NH1AARG A  10      594    333    340     10    131   -106       N
ATOM    188  NH1BARG A  10      12.990   6.670   6.157  0.33  5.59           N
ANISOU  188  NH1BARG A  10      955    719    447    -84    213   -444       N
ATOM    189  NH2AARG A  10      13.443   7.503   8.090  0.67  3.48           N
ANISOU  189  NH2AARG A  10      599    360    364   -116    149   -204       N
ATOM    190  NH2BARG A  10      13.755   7.127   8.237  0.33  8.43           N
ANISOU  190  NH2BARG A  10     1708    931    562   -265    514  -1062       N
ATOM    191  H   ARG A  10       8.009   4.663  10.831  1.00  1.90           H
ATOM    192  HA  ARG A  10       8.688   5.499   8.174  1.00  1.87           H
ATOM    193  HB2 ARG A  10      10.377   4.784   9.785  1.00  2.18           H
ATOM    194  HB3 ARG A  10       9.677   3.155   9.860  1.00  2.18           H
ATOM    195  HG2 ARG A  10      11.636   3.050   8.472  1.00  2.50           H
ATOM    196  HG3 ARG A  10      10.217   2.846   7.430  1.00  2.50           H
ATOM    197  HD2 ARG A  10      11.818   4.251   6.293  1.00  2.82           H
ATOM    198  HD3 ARG A  10      10.410   5.240   6.732  1.00  2.82           H
ATOM    199  HE AARG A  10      12.350   5.422   8.790  0.67  2.56           H
ATOM    200  HE BARG A  10      12.268   5.285   9.022  0.33  2.87           H
ATOM    201 HH11AARG A  10      11.830   6.478   5.487  0.67  4.04           H
ATOM    202 HH11BARG A  10      12.442   6.135   5.501  0.33  6.91           H
ATOM    203 HH12AARG A  10      12.853   7.884   5.661  0.67  4.04           H
ATOM    204 HH12BARG A  10      13.587   7.414   5.828  0.33  6.91           H
ATOM    205 HH21AARG A  10      13.831   8.362   7.729  0.67  4.22           H
ATOM    206 HH21BARG A  10      13.808   6.956   9.229  0.33 10.67           H
ATOM    207 HH22AARG A  10      13.622   7.230   9.044  0.67  4.22           H
ATOM    208 HH22BARG A  10      14.322   7.849   7.818  0.33 10.67           H
ATOM    209  N   SER A  11       7.211   2.522   8.369  1.00  1.73           N
ANISOU  209  N   SER A  11      258    217    181     -5    -33    -53       N
ATOM    210  CA  SER A  11       6.538   1.562   7.510  1.00  1.77           C
ANISOU  210  CA  SER A  11      253    193    224    -16    -48    -32       C
ATOM    211  C   SER A  11       5.415   2.243   6.711  1.00  1.70           C
ANISOU  211  C   SER A  11      255    194    194     -5    -40    -35       C
ATOM    212  O   SER A  11       5.227   1.995   5.517  1.00  2.01           O
ANISOU  212  O   SER A  11      318    248    196    -40    -58      0       O
ATOM    213  CB  SER A  11       5.967   0.416   8.335  1.00  2.24           C
ANISOU  213  CB  SER A  11      299    206    343     51    -87    -47       C
ATOM    214  OG  SER A  11       7.043  -0.267   8.962  1.00  3.47           O
ANISOU  214  OG  SER A  11      384    310    621    199   -148    -11       O
ATOM    215  H   SER A  11       7.224   2.395   9.370  1.00  2.07           H
ATOM    216  HA  SER A  11       7.271   1.152   6.802  1.00  2.12           H
ATOM    217  HB2 SER A  11       5.276   0.807   9.095  1.00  2.69           H
ATOM    218  HB3 SER A  11       5.411  -0.275   7.685  1.00  2.69           H
ATOM    219  HG  SER A  11       6.697  -1.005   9.482  1.00  5.17           H
ATOM    220  N   ASN A  12       4.661   3.116   7.382  1.00  1.73           N
ANISOU  220  N   ASN A  12      256    227    172     22     -7    -24       N
ATOM    221  CA AASN A  12       3.595   3.898   6.756  0.37  1.76           C
ANISOU  221  CA AASN A  12      218    269    181     26      6    -23       C
ATOM    222  CA BASN A  12       3.587   3.804   6.673  0.63  1.83           C
ANISOU  222  CA BASN A  12      234    246    215     37     33      9       C
ATOM    223  C   ASN A  12       4.154   4.793   5.647  1.00  1.79           C
ANISOU  223  C   ASN A  12      283    231    164     19     22     12       C
ATOM    224  O   ASN A  12       3.549   4.958   4.581  1.00  2.30           O
ANISOU  224  O   ASN A  12      371    336    164     41    -13    -33       O
ATOM    225  CB AASN A  12       2.831   4.764   7.756  0.37  1.88           C
ANISOU  225  CB AASN A  12      239    240    234     57     73    -25       C
ATOM    226  CB BASN A  12       2.681   4.487   7.692  0.63  2.39           C
ANISOU  226  CB BASN A  12      317    363    228     38     91     39       C
ATOM    227  CG AASN A  12       1.901   3.956   8.670  0.37  2.03           C
ANISOU  227  CG AASN A  12      252    248    271     77     79    -28       C
ATOM    228  CG BASN A  12       1.884   3.461   8.515  0.63  2.82           C
ANISOU  228  CG BASN A  12      336    444    292     74    126     21       C
ATOM    229  OD1AASN A  12       1.513   2.854   8.302  0.37  3.92           O
ANISOU  229  OD1AASN A  12      600    328    560    -55    307   -200       O
ATOM    230  OD1BASN A  12       1.651   2.334   8.091  0.63  3.87           O
ANISOU  230  OD1BASN A  12      507    455    507     78    167   -112       O
ATOM    231  ND2AASN A  12       1.534   4.536   9.789  0.37  2.49           N
ANISOU  231  ND2AASN A  12      306    377    262     35     79    -57       N
ATOM    232  ND2BASN A  12       1.461   3.901   9.686  0.63  4.09           N
ANISOU  232  ND2BASN A  12      563    622    369     31    267     16       N
ATOM    233  H   ASN A  12       4.835   3.242   8.368  1.00  2.07           H
ATOM    234  HA AASN A  12       2.882   3.196   6.300  0.37  2.13           H
ATOM    235  HA BASN A  12       2.994   3.052   6.135  0.63  2.21           H
ATOM    236  HB2AASN A  12       3.553   5.313   8.377  0.37  2.34           H
ATOM    237  HB2BASN A  12       3.292   5.101   8.368  0.63  2.92           H
ATOM    238  HB3AASN A  12       2.234   5.503   7.204  0.37  2.34           H
ATOM    239  HB3BASN A  12       1.982   5.154   7.167  0.63  2.92           H
ATOM    240 HD21AASN A  12       0.890   4.070  10.410  0.37  3.02           H
ATOM    241 HD21BASN A  12       0.915   3.299  10.284  0.63  4.90           H
ATOM    242 HD22AASN A  12       1.897   5.447  10.027  0.37  3.02           H
ATOM    243 HD22BASN A  12       1.683   4.839   9.983  0.63  4.90           H
ATOM    244  N   PHE A  13       5.288   5.434   5.950  1.00  1.78           N
ANISOU  244  N   PHE A  13      300    221    154     20     21     -5       N
ATOM    245  CA  PHE A  13       5.940   6.322   4.994  1.00  1.70           C
ANISOU  245  CA  PHE A  13      283    198    164     10      8    -19       C
ATOM    246  C   PHE A  13       6.312   5.548   3.719  1.00  1.55           C
ANISOU  246  C   PHE A  13      239    216    131     19      2    -26       C
ATOM    247  O   PHE A  13       6.092   6.018   2.611  1.00  1.78           O
ANISOU  247  O   PHE A  13      286    238    153     34     -6    -35       O
ATOM    248  CB  PHE A  13       7.176   6.946   5.672  1.00  2.08           C
ANISOU  248  CB  PHE A  13      361    234    194      6    -41    -67       C
ATOM    249  CG APHE A  13       7.941   7.888   4.755  0.40  2.00           C
ANISOU  249  CG APHE A  13      302    247    210     25   -120   -117       C
ATOM    250  CG BPHE A  13       7.848   8.003   4.844  0.60  2.19           C
ANISOU  250  CG BPHE A  13      300    252    279     19     47    -23       C
ATOM    251  CD1APHE A  13       8.984   7.309   3.949  0.40  3.11           C
ANISOU  251  CD1APHE A  13      430    387    362    -63     32   -164       C
ATOM    252  CD1BPHE A  13       8.844   7.684   3.917  0.60  2.62           C
ANISOU  252  CD1BPHE A  13      375    278    341   -104     95    -68       C
ATOM    253  CD2APHE A  13       7.610   9.268   4.690  0.40  2.48           C
ANISOU  253  CD2APHE A  13      417    260    264     66   -130    -86       C
ATOM    254  CD2BPHE A  13       7.486   9.333   5.057  0.60  2.28           C
ANISOU  254  CD2BPHE A  13      304    255    307     27    -19     -4       C
ATOM    255  CE1APHE A  13       9.674   8.201   3.099  0.40  4.71           C
ANISOU  255  CE1APHE A  13      661    931    196    -57     23   -506       C
ATOM    256  CE1BPHE A  13       9.430   8.686   3.153  0.60  3.77           C
ANISOU  256  CE1BPHE A  13      517    556    360    -64    146   -260       C
ATOM    257  CE2APHE A  13       8.310  10.117   3.816  0.40  4.07           C
ANISOU  257  CE2APHE A  13      716    487    340    198   -188   -289       C
ATOM    258  CE2BPHE A  13       8.071  10.331   4.281  0.60  2.95           C
ANISOU  258  CE2BPHE A  13      364    288    466    134   -116    -67       C
ATOM    259  CZ APHE A  13       9.375   9.576   3.044  0.40  4.83           C
ANISOU  259  CZ APHE A  13      493    993    348    279   -102   -442       C
ATOM    260  CZ BPHE A  13       9.036   9.997   3.302  0.60  3.50           C
ANISOU  260  CZ BPHE A  13      411    532    384    203    -57   -187       C
ATOM    261  H   PHE A  13       5.701   5.301   6.861  1.00  2.13           H
ATOM    262  HA  PHE A  13       5.240   7.126   4.726  1.00  2.05           H
ATOM    263  HB2 PHE A  13       6.853   7.500   6.565  1.00  2.49           H
ATOM    264  HB3 PHE A  13       7.848   6.142   6.001  1.00  2.49           H
ATOM    265  HD1APHE A  13       9.228   6.238   3.992  0.40  3.59           H
ATOM    266  HD1BPHE A  13       9.164   6.640   3.792  0.60  3.14           H
ATOM    267  HD2APHE A  13       6.806   9.671   5.323  0.40  2.94           H
ATOM    268  HD2BPHE A  13       6.748   9.591   5.830  0.60  2.74           H
ATOM    269  HE1APHE A  13      10.474   7.807   2.456  0.40  5.62           H
ATOM    270  HE1BPHE A  13      10.214   8.431   2.425  0.60  4.57           H
ATOM    271  HE2APHE A  13       8.040  11.178   3.731  0.40  4.92           H
ATOM    272  HE2BPHE A  13       7.781  11.381   4.429  0.60  3.59           H
ATOM    273  HZ APHE A  13       9.970  10.238   2.399  0.40  5.90           H
ATOM    274  HZ BPHE A  13       9.469  10.780   2.663  0.60  4.21           H
ATOM    275  N   ASN A  14       6.892   4.356   3.906  1.00  1.62           N
ANISOU  275  N   ASN A  14      238    222    154      3     -7    -12       N
ATOM    276  CA  ASN A  14       7.323   3.600   2.746  1.00  1.56           C
ANISOU  276  CA  ASN A  14      202    236    152      3     -3    -19       C
ATOM    277  C   ASN A  14       6.137   3.150   1.887  1.00  1.55           C
ANISOU  277  C   ASN A  14      186    233    168     -2      1    -23       C
ATOM    278  O   ASN A  14       6.248   3.117   0.663  1.00  2.17           O
ANISOU  278  O   ASN A  14      227    411    187     -9     16    -83       O
ATOM    279  CB  ASN A  14       8.188   2.417   3.167  1.00  1.96           C
ANISOU  279  CB  ASN A  14      228    261    254    -19    -42      8       C
ATOM    280  CG  ASN A  14       9.563   2.858   3.654  1.00  2.40           C
ANISOU  280  CG  ASN A  14      230    344    337    -21    -73      5       C
ATOM    281  OD1 ASN A  14      10.051   3.925   3.246  1.00  3.33           O
ANISOU  281  OD1 ASN A  14      280    436    546     38   -108   -101       O
ATOM    282  ND2 ASN A  14      10.180   2.025   4.475  1.00  3.15           N
ANISOU  282  ND2 ASN A  14      308    442    445      1   -145     63       N
ATOM    283  H   ASN A  14       7.026   3.990   4.837  1.00  1.94           H
ATOM    284  HA  ASN A  14       7.946   4.263   2.131  1.00  1.87           H
ATOM    285  HB2 ASN A  14       7.680   1.866   3.971  1.00  2.35           H
ATOM    286  HB3 ASN A  14       8.308   1.735   2.314  1.00  2.35           H
ATOM    287 HD21 ASN A  14      11.107   2.241   4.810  1.00  3.78           H
ATOM    288 HD22 ASN A  14       9.724   1.174   4.767  1.00  3.78           H
ATOM    289  N   VAL A  15       4.992   2.817   2.503  1.00  1.46           N
ANISOU  289  N   VAL A  15      193    202    157     10      2    -23       N
ATOM    290  CA  VAL A  15       3.809   2.515   1.695  1.00  1.45           C
ANISOU  290  CA  VAL A  15      204    181    163     19     -4    -35       C
ATOM    291  C   VAL A  15       3.309   3.772   0.970  1.00  1.47           C
ANISOU  291  C   VAL A  15      210    181    168     28      6    -34       C
ATOM    292  O   VAL A  15       2.967   3.733  -0.207  1.00  1.77           O
ANISOU  292  O   VAL A  15      264    218    189     23    -28    -42       O
ATOM    293  CB  VAL A  15       2.718   1.853   2.546  1.00  1.79           C
ANISOU  293  CB  VAL A  15      214    217    249     79     14    -37       C
ATOM    294  CG1 VAL A  15       1.390   1.798   1.795  1.00  2.75           C
ANISOU  294  CG1 VAL A  15      219    348    477    176    -55    -89       C
ATOM    295  CG2 VAL A  15       3.171   0.458   2.966  1.00  2.43           C
ANISOU  295  CG2 VAL A  15      310    229    381    126    -37    -45       C
ATOM    296  H   VAL A  15       4.948   2.775   3.510  1.00  1.74           H
ATOM    297  HA  VAL A  15       4.112   1.790   0.927  1.00  1.73           H
ATOM    298  HB  VAL A  15       2.576   2.457   3.453  1.00  2.15           H
ATOM    299 HG11 VAL A  15       1.086   2.816   1.514  1.00  4.07           H
ATOM    300 HG12 VAL A  15       0.621   1.353   2.443  1.00  4.07           H
ATOM    301 HG13 VAL A  15       1.506   1.187   0.890  1.00  4.07           H
ATOM    302 HG21 VAL A  15       4.124   0.530   3.509  1.00  3.65           H
ATOM    303 HG22 VAL A  15       3.304  -0.169   2.073  1.00  3.65           H
ATOM    304 HG23 VAL A  15       2.411   0.007   3.619  1.00  3.65           H
ATOM    305  N   CYS A  16       3.265   4.910   1.697  1.00  1.55           N
ANISOU  305  N   CYS A  16      224    181    184     27      6    -12       N
ATOM    306  CA  CYS A  16       2.853   6.168   1.085  1.00  1.54           C
ANISOU  306  CA  CYS A  16      194    192    199     21      7      0       C
ATOM    307  C   CYS A  16       3.680   6.497  -0.171  1.00  1.45           C
ANISOU  307  C   CYS A  16      190    182    178     26    -12     -4       C
ATOM    308  O   CYS A  16       3.159   7.037  -1.146  1.00  1.80           O
ANISOU  308  O   CYS A  16      243    242    198     56    -33      7       O
ATOM    309  CB  CYS A  16       2.981   7.257   2.155  1.00  1.93           C
ANISOU  309  CB  CYS A  16      284    205    245     -7     16     -2       C
ATOM    310  SG  CYS A  16       2.571   8.931   1.593  1.00  2.20           S
ANISOU  310  SG  CYS A  16      275    199    360    -33    -49     28       S
ATOM    311  H   CYS A  16       3.519   4.890   2.673  1.00  1.87           H
ATOM    312  HA  CYS A  16       1.796   6.085   0.795  1.00  1.85           H
ATOM    313  HB2 CYS A  16       2.321   7.000   2.996  1.00  2.33           H
ATOM    314  HB3 CYS A  16       4.013   7.258   2.533  1.00  2.33           H
ATOM    315  N   ARG A  17       4.980   6.166  -0.135  1.00  1.46           N
ANISOU  315  N   ARG A  17      186    194    172     36     -5    -11       N
ATOM    316  CA  ARG A  17       5.850   6.474  -1.244  1.00  1.51           C
ANISOU  316  CA  ARG A  17      188    180    205     23      7    -35       C
ATOM    317  C   ARG A  17       5.641   5.554  -2.455  1.00  1.61           C
ANISOU  317  C   ARG A  17      207    222    182     18      9    -48       C
ATOM    318  O   ARG A  17       6.033   5.932  -3.563  1.00  2.20           O
ANISOU  318  O   ARG A  17      313    315    204      0     60   -132       O
ATOM    319  CB  ARG A  17       7.317   6.413  -0.802  1.00  1.71           C
ANISOU  319  CB  ARG A  17      191    215    241     24      1    -29       C
ATOM    320  CG  ARG A  17       7.692   7.571   0.124  1.00  1.91           C
ANISOU  320  CG  ARG A  17      229    260    238     17    -10    -75       C
ATOM    321  CD  ARG A  17       7.903   8.893  -0.615  1.00  2.03           C
ANISOU  321  CD  ARG A  17      211    211    348     -1     66    -44       C
ATOM    322  NE  ARG A  17       9.156   8.833  -1.364  1.00  2.13           N
ANISOU  322  NE  ARG A  17      191    268    350     54     54    -13       N
ATOM    323  CZ  ARG A  17       9.472   9.600  -2.396  1.00  1.95           C
ANISOU  323  CZ  ARG A  17      222    259    257     -7     47    -35       C
ATOM    324  NH1 ARG A  17       8.585  10.416  -2.966  1.00  2.59           N
ANISOU  324  NH1 ARG A  17      284    377    323     89     75     20       N
ATOM    325  NH2 ARG A  17      10.713   9.561  -2.889  1.00  2.55           N
ANISOU  325  NH2 ARG A  17      253    383    330     10     98    -13       N
ATOM    326  H   ARG A  17       5.352   5.696   0.676  1.00  1.75           H
ATOM    327  HA  ARG A  17       5.637   7.504  -1.563  1.00  1.81           H
ATOM    328  HB2 ARG A  17       7.498   5.462  -0.282  1.00  2.04           H
ATOM    329  HB3 ARG A  17       7.963   6.439  -1.691  1.00  2.04           H
ATOM    330  HG2 ARG A  17       6.896   7.703   0.870  1.00  2.29           H
ATOM    331  HG3 ARG A  17       8.615   7.312   0.662  1.00  2.29           H
ATOM    332  HD2 ARG A  17       7.065   9.072  -1.303  1.00  2.43           H
ATOM    333  HD3 ARG A  17       7.939   9.721   0.107  1.00  2.43           H
ATOM    334  HE  ARG A  17       9.838   8.150  -1.070  1.00  2.55           H
ATOM    335 HH11 ARG A  17       7.642  10.462  -2.611  1.00  3.10           H
ATOM    336 HH12 ARG A  17       8.858  10.988  -3.751  1.00  3.10           H
ATOM    337 HH21 ARG A  17      11.402   8.951  -2.474  1.00  3.07           H
ATOM    338 HH22 ARG A  17      10.962  10.142  -3.675  1.00  3.07           H
ATOM    339  N   LEU A  18       5.053   4.360  -2.271  1.00  1.65           N
ANISOU  339  N   LEU A  18      236    199    192     15      9    -33       N
ATOM    340  CA  LEU A  18       4.954   3.418  -3.387  1.00  1.68           C
ANISOU  340  CA  LEU A  18      252    179    208      7      4    -13       C
ATOM    341  C   LEU A  18       4.321   4.013  -4.638  1.00  1.55           C
ANISOU  341  C   LEU A  18      227    171    189      2     26    -27       C
ATOM    342  O   LEU A  18       4.849   3.780  -5.744  1.00  1.81           O
ANISOU  342  O   LEU A  18      266    209    213     -3     50      1       O
ATOM    343  CB  LEU A  18       4.203   2.149  -2.980  1.00  2.10           C
ANISOU  343  CB  LEU A  18      328    197    272     52    -18    -44       C
ATOM    344  CG  LEU A  18       4.942   1.212  -2.020  1.00  2.28           C
ANISOU  344  CG  LEU A  18      391    228    244     53    -25    -24       C
ATOM    345  CD1 LEU A  18       3.987   0.098  -1.586  1.00  3.65           C
ANISOU  345  CD1 LEU A  18      586    317    483    185    -73   -133       C
ATOM    346  CD2 LEU A  18       6.197   0.625  -2.641  1.00  3.47           C
ANISOU  346  CD2 LEU A  18      481    328    509     97     29    128       C
ATOM    347  H   LEU A  18       4.681   4.113  -1.366  1.00  2.00           H
ATOM    348  HA  LEU A  18       5.978   3.119  -3.651  1.00  2.01           H
ATOM    349  HB2 LEU A  18       3.254   2.444  -2.511  1.00  2.53           H
ATOM    350  HB3 LEU A  18       3.958   1.585  -3.891  1.00  2.53           H
ATOM    351  HG  LEU A  18       5.232   1.787  -1.129  1.00  2.72           H
ATOM    352 HD11 LEU A  18       3.070   0.542  -1.173  1.00  5.44           H
ATOM    353 HD12 LEU A  18       4.472  -0.522  -0.819  1.00  5.44           H
ATOM    354 HD13 LEU A  18       3.733  -0.526  -2.454  1.00  5.44           H
ATOM    355 HD21 LEU A  18       6.879   1.438  -2.928  1.00  5.25           H
ATOM    356 HD22 LEU A  18       5.926   0.042  -3.533  1.00  5.25           H
ATOM    357 HD23 LEU A  18       6.695  -0.030  -1.913  1.00  5.25           H
ATOM    358  N   PRO A  19       3.209   4.754  -4.571  1.00  1.63           N
ANISOU  358  N   PRO A  19      218    219    181     -2     21    -17       N
ATOM    359  CA  PRO A  19       2.660   5.337  -5.804  1.00  1.75           C
ANISOU  359  CA  PRO A  19      233    217    214      0    -13    -11       C
ATOM    360  C   PRO A  19       3.434   6.548  -6.317  1.00  2.08           C
ANISOU  360  C   PRO A  19      273    263    254     57      8    -16       C
ATOM    361  O   PRO A  19       3.086   7.062  -7.379  1.00  3.61           O
ANISOU  361  O   PRO A  19      463    536    373    246    -81   -117       O
ATOM    362  CB  PRO A  19       1.226   5.736  -5.413  1.00  2.27           C
ANISOU  362  CB  PRO A  19      216    355    292     -1    -24      0       C
ATOM    363  CG APRO A  19       1.283   5.912  -3.890  0.85  2.25           C
ANISOU  363  CG APRO A  19      236    320    296    -23     27     20       C
ATOM    364  CG BPRO A  19       0.975   5.129  -4.119  0.15  2.42           C
ATOM    365  CD  PRO A  19       2.249   4.859  -3.446  1.00  2.24           C
ANISOU  365  CD  PRO A  19      255    401    192     -2     41     50       C
ATOM    366  HA  PRO A  19       2.625   4.567  -6.588  1.00  2.08           H
ATOM    367  HB2APRO A  19       0.932   6.673  -5.906  0.85  2.72           H
ATOM    368  HB2BPRO A  19       1.110   6.800  -5.370  0.15  2.69           H
ATOM    369  HB3APRO A  19       0.511   4.948  -5.690  0.85  2.72           H
ATOM    370  HB3BPRO A  19       0.580   5.380  -6.120  0.15  2.69           H
ATOM    371  HG2APRO A  19       1.644   6.915  -3.622  0.85  2.69           H
ATOM    372  HG2BPRO A  19       0.366   5.805  -3.504  0.15  2.69           H
ATOM    373  HG3APRO A  19       0.294   5.755  -3.437  0.85  2.69           H
ATOM    374  HG3BPRO A  19       0.419   4.190  -4.251  0.15  2.69           H
ATOM    375  HD2APRO A  19       2.760   5.160  -2.521  0.85  2.68           H
ATOM    376  HD2BPRO A  19       2.521   5.681  -2.769  0.15  2.68           H
ATOM    377  HD3APRO A  19       1.737   3.902  -3.277  0.85  2.68           H
ATOM    378  HD3BPRO A  19       2.205   3.922  -2.874  0.15  2.68           H
ATOM    379  N   GLY A  20       4.420   7.027  -5.559  1.00  1.87           N
ANISOU  379  N   GLY A  20      264    178    266    -17     67    -25       N
ATOM    380  CA  GLY A  20       5.223   8.167  -5.960  1.00  2.48           C
ANISOU  380  CA  GLY A  20      345    186    408    -34    195    -40       C
ATOM    381  C   GLY A  20       4.902   9.466  -5.248  1.00  1.98           C
ANISOU  381  C   GLY A  20      242    170    338     -9     99    -29       C
ATOM    382  O   GLY A  20       5.443  10.505  -5.620  1.00  3.00           O
ANISOU  382  O   GLY A  20      519    204    415    -12    232    -94       O
ATOM    383  H   GLY A  20       4.614   6.582  -4.675  1.00  2.24           H
ATOM    384  HA2 GLY A  20       6.281   7.926  -5.785  1.00  2.95           H
ATOM    385  HA3 GLY A  20       5.093   8.321  -7.041  1.00  2.95           H
ATOM    386  N   THR A  21       4.056   9.404  -4.216  1.00  1.67           N
ANISOU  386  N   THR A  21      228    168    235    -19     40    -32       N
ATOM    387  CA  THR A  21       3.664  10.576  -3.461  1.00  1.43           C
ANISOU  387  CA  THR A  21      177    164    200     -2     -2     -6       C
ATOM    388  C   THR A  21       4.915  11.347  -3.001  1.00  1.58           C
ANISOU  388  C   THR A  21      176    184    240      0     -2    -21       C
ATOM    389  O   THR A  21       5.844  10.729  -2.478  1.00  2.25           O
ANISOU  389  O   THR A  21      193    270    389     73    -61    -34       O
ATOM    390  CB  THR A  21       2.932  10.113  -2.178  1.00  1.52           C
ANISOU  390  CB  THR A  21      163    180    234     11      0     -6       C
ATOM    391  OG1 THR A  21       1.964   9.124  -2.552  1.00  1.89           O
ANISOU  391  OG1 THR A  21      210    214    293     43    -32    -50       O
ATOM    392  CG2 THR A  21       2.280  11.274  -1.459  1.00  2.12           C
ANISOU  392  CG2 THR A  21      241    246    318    -29     68     19       C
ATOM    393  H   THR A  21       3.676   8.507  -3.952  1.00  2.00           H
ATOM    394  HA  THR A  21       3.014  11.225  -4.064  1.00  1.71           H
ATOM    395  HB  THR A  21       3.666   9.650  -1.503  1.00  1.83           H
ATOM    396  HG1 THR A  21       2.092   8.329  -2.016  1.00  2.85           H
ATOM    397 HG21 THR A  21       1.606  11.800  -2.148  1.00  3.17           H
ATOM    398 HG22 THR A  21       3.056  11.968  -1.105  1.00  3.17           H
ATOM    399 HG23 THR A  21       1.706  10.898  -0.600  1.00  3.17           H
ATOM    400  N   PRO A  22       4.915  12.683  -3.102  1.00  1.83           N
ANISOU  400  N   PRO A  22      220    185    289    -20     -2    -33       N
ATOM    401  CA APRO A  22       6.042  13.429  -2.601  0.57  1.82           C
ANISOU  401  CA APRO A  22      339    145    204    -56     75   -144       C
ATOM    402  C  APRO A  22       6.387  13.122  -1.160  0.57  1.66           C
ANISOU  402  C  APRO A  22      230    195    204    -82     85   -119       C
ATOM    403  O  APRO A  22       5.480  13.006  -0.345  0.57  2.09           O
ANISOU  403  O  APRO A  22      224    322    246    -51     60    -58       O
ATOM    404  CB APRO A  22       5.655  14.896  -2.744  0.57  2.86           C
ANISOU  404  CB APRO A  22      591    108    387    -50     -5   -173       C
ATOM    405  CG APRO A  22       4.661  14.854  -4.058  0.57  2.66           C
ANISOU  405  CG APRO A  22      420    174    417     69     20    -27       C
ATOM    406  CD APRO A  22       3.957  13.505  -3.910  0.57  2.27           C
ANISOU  406  CD APRO A  22      317    174    370     60     -1     -4       C
ATOM    407  HA APRO A  22       6.915  13.244  -3.241  0.57  1.93           H
ATOM    408  HB2APRO A  22       5.112  15.266  -1.863  0.57  3.34           H
ATOM    409  HB3APRO A  22       6.516  15.539  -2.944  0.57  3.34           H
ATOM    410  HG2APRO A  22       3.919  15.683  -4.043  0.57  3.20           H
ATOM    411  HG3APRO A  22       5.214  14.903  -5.002  0.57  3.20           H
ATOM    412  HD2APRO A  22       2.984  13.625  -3.389  0.57  2.69           H
ATOM    413  HD3APRO A  22       3.752  13.060  -4.903  0.57  2.69           H
ATOM    414  CA BSER A  22       6.034  13.399  -2.687  0.21  1.55           C
ATOM    415  CA CSER A  22       6.112  13.653  -2.656  0.22  2.31           C
ATOM    416  C  BSER A  22       6.367  13.062  -1.223  0.21  2.92           C
ATOM    417  C  CSER A  22       6.354  13.275  -1.187  0.22  1.92           C
ATOM    418  O  BSER A  22       5.412  13.050  -0.345  0.21  1.87           O
ATOM    419  O  CSER A  22       5.636  12.705  -0.270  0.22  1.77           O
ATOM    420  CB BSER A  22       5.409  14.835  -2.876  0.21  2.60           C
ATOM    421  CB CSER A  22       5.605  15.097  -2.687  0.22  3.56           C
ATOM    422  OG BSER A  22       4.760  15.243  -1.635  0.21  2.11           O
ATOM    423  OG CSER A  22       6.750  15.771  -2.280  0.22  6.38           O
ATOM    424  HA BSER A  22       6.897  13.240  -3.349  0.21  4.26           H
ATOM    425  HA CSER A  22       7.013  13.518  -3.271  0.22  4.26           H
ATOM    426  N   GLU A  23       7.651  13.190  -0.860  1.00  1.86           N
ANISOU  426  N   GLU A  23      256    245    205    -32     61    -70       N
ATOM    427  CA  GLU A  23       8.108  13.002   0.513  1.00  1.81           C
ANISOU  427  CA  GLU A  23      246    213    227    -17     62    -30       C
ATOM    428  C   GLU A  23       7.394  13.968   1.459  1.00  1.66           C
ANISOU  428  C   GLU A  23      214    206    209     -5     46    -21       C
ATOM    429  O   GLU A  23       7.064  13.585   2.589  1.00  1.97           O
ANISOU  429  O   GLU A  23      274    260    212     25     62     12       O
ATOM    430  CB  GLU A  23       9.620  13.168   0.681  1.00  2.12           C
ANISOU  430  CB  GLU A  23      243    280    281    -40     55      1       C
ATOM    431  CG AGLU A  23      10.459  12.148  -0.048  0.58  2.73           C
ANISOU  431  CG AGLU A  23      372    317    349     12    163     64       C
ATOM    432  CG BGLU A  23      10.414  11.969   0.088  0.42  1.79           C
ANISOU  432  CG BGLU A  23      262    182    235     22     34    -17       C
ATOM    433  CD AGLU A  23      11.942  12.208   0.242  0.58  4.60           C
ANISOU  433  CD AGLU A  23      404   1001    343   -141     78     99       C
ATOM    434  CD BGLU A  23      11.911  12.048   0.452  0.42  2.33           C
ANISOU  434  CD BGLU A  23      240    305    341     52     40    113       C
ATOM    435  OE1AGLU A  23      12.418  13.330   0.541  0.58  7.57           O
ANISOU  435  OE1AGLU A  23      395   1235   1244   -482    236    -77       O
ATOM    436  OE1BGLU A  23      12.430  13.113   0.795  0.42  2.70           O
ANISOU  436  OE1BGLU A  23      191    409    425     74    -50     24       O
ATOM    437  OE2AGLU A  23      12.629  11.211   0.128  0.58  7.42           O
ANISOU  437  OE2AGLU A  23      455   1209   1155    128    244    304       O
ATOM    438  OE2BGLU A  23      12.514  10.945   0.316  0.42  4.43           O
ANISOU  438  OE2BGLU A  23      553    501    629   -196   -205    354       O
ATOM    439  H   GLU A  23       8.361  13.404  -1.574  1.00  2.23           H
ATOM    440  HA  GLU A  23       7.842  11.977   0.808  1.00  2.17           H
ATOM    441  HB2 GLU A  23       9.902  14.169   0.326  1.00  2.55           H
ATOM    442  HB3 GLU A  23       9.860  13.116   1.752  1.00  2.55           H
ATOM    443  HG2AGLU A  23      10.094  11.146   0.214  0.58  3.27           H
ATOM    444  HG2BGLU A  23       9.996  11.029   0.473  0.42  2.13           H
ATOM    445  HG3AGLU A  23      10.310  12.283  -1.128  0.58  3.27           H
ATOM    446  HG3BGLU A  23      10.306  11.966  -1.006  0.42  2.13           H
ATOM    447  N   ALA A  24       7.188  15.227   1.041  1.00  1.63           N
ANISOU  447  N   ALA A  24      244    204    172    -11     41    -31       N
ATOM    448  CA  ALA A  24       6.619  16.195   1.970  1.00  1.65           C
ANISOU  448  CA  ALA A  24      227    186    213    -23     25    -26       C
ATOM    449  C   ALA A  24       5.192  15.819   2.387  1.00  1.51           C
ANISOU  449  C   ALA A  24      221    179    172     12     15     -6       C
ATOM    450  O   ALA A  24       4.795  16.037   3.532  1.00  1.85           O
ANISOU  450  O   ALA A  24      233    263    205    -30     25    -19       O
ATOM    451  CB  ALA A  24       6.663  17.597   1.363  1.00  2.43           C
ANISOU  451  CB  ALA A  24      351    195    377     23     72    -56       C
ATOM    452  H   ALA A  24       7.422  15.499   0.098  1.00  1.96           H
ATOM    453  HA  ALA A  24       7.244  16.200   2.874  1.00  1.98           H
ATOM    454  HB1 ALA A  24       7.696  17.841   1.079  1.00  3.63           H
ATOM    455  HB2 ALA A  24       6.304  18.327   2.101  1.00  3.63           H
ATOM    456  HB3 ALA A  24       6.021  17.630   0.472  1.00  3.63           H
ATOM    457  N  ALEU A  25       4.398  15.289   1.441  0.57  1.61           N
ANISOU  457  N  ALEU A  25      226    194    191      4     15    -28       N
ATOM    458  CA ALEU A  25       3.048  14.822   1.781  0.57  1.48           C
ANISOU  458  CA ALEU A  25      201    173    186      9     -3     -4       C
ATOM    459  C  ALEU A  25       3.113  13.568   2.640  0.57  1.50           C
ANISOU  459  C  ALEU A  25      194    194    179     25     16     -3       C
ATOM    460  O  ALEU A  25       2.332  13.396   3.580  0.57  2.01           O
ANISOU  460  O  ALEU A  25      272    281    210     49     75     28       O
ATOM    461  CB ALEU A  25       2.209  14.621   0.512  0.57  1.70           C
ANISOU  461  CB ALEU A  25      254    190    201     30    -48     22       C
ATOM    462  CG ALEU A  25       1.717  15.929  -0.108  0.57  1.80           C
ANISOU  462  CG ALEU A  25      184    242    258     83    -13     47       C
ATOM    463  CD1ALEU A  25       1.207  15.625  -1.514  0.57  3.58           C
ANISOU  463  CD1ALEU A  25      497    578    285     -4   -115    240       C
ATOM    464  CD2ALEU A  25       0.595  16.583   0.794  0.57  2.15           C
ANISOU  464  CD2ALEU A  25      178    251    386    -37    -34     53       C
ATOM    465  H  ALEU A  25       4.733  15.199   0.495  0.57  1.94           H
ATOM    466  HA ALEU A  25       2.567  15.612   2.380  0.57  1.77           H
ATOM    467  HB2ALEU A  25       2.806  14.080  -0.225  0.57  1.61           H
ATOM    468  HB3ALEU A  25       1.337  13.994   0.770  0.57  1.61           H
ATOM    469  HG ALEU A  25       2.565  16.642  -0.141  0.57  2.02           H
ATOM    470 HD11ALEU A  25       0.243  16.147  -1.682  0.57  5.46           H
ATOM    471 HD12ALEU A  25       1.105  14.573  -1.667  0.57  5.46           H
ATOM    472 HD13ALEU A  25       1.941  16.049  -2.253  0.57  5.46           H
ATOM    473 HD21ALEU A  25       0.118  17.396   0.216  0.57  3.21           H
ATOM    474 HD22ALEU A  25       1.043  16.996   1.701  0.57  3.21           H
ATOM    475 HD23ALEU A  25      -0.145  15.824   1.041  0.57  3.21           H
ATOM    476  N  BILE A  25       4.398  15.289   1.441  0.21  1.61           N
ANISOU  476  N  BILE A  25      226    194    191      4     15    -28       N
ATOM    477  N  CILE A  25       4.398  15.289   1.441  0.22  1.61           N
ANISOU  477  N  CILE A  25      226    194    191      4     15    -28       N
ATOM    478  CA BILE A  25       3.048  14.822   1.781  0.21  1.48           C
ANISOU  478  CA BILE A  25      201    173    186      9     -3     -4       C
ATOM    479  CA CILE A  25       3.048  14.822   1.781  0.22  1.48           C
ANISOU  479  CA CILE A  25      201    173    186      9     -3     -4       C
ATOM    480  C  BILE A  25       3.113  13.568   2.640  0.21  1.50           C
ANISOU  480  C  BILE A  25      194    194    179     25     16     -3       C
ATOM    481  C  CILE A  25       3.113  13.568   2.640  0.22  1.50           C
ANISOU  481  C  CILE A  25      194    194    179     25     16     -3       C
ATOM    482  O  BILE A  25       2.332  13.396   3.580  0.21  2.01           O
ANISOU  482  O  BILE A  25      272    281    210     49     75     28       O
ATOM    483  O  CILE A  25       2.332  13.396   3.580  0.22  2.01           O
ANISOU  483  O  CILE A  25      272    281    210     49     75     28       O
ATOM    484  CB BILE A  25       2.225  14.590   0.511  0.21  1.67           C
ATOM    485  CB CILE A  25       2.194  14.590   0.526  0.22  2.08           C
ATOM    486  CG1BILE A  25       1.931  15.856  -0.269  0.21  2.53           C
ATOM    487  CG1CILE A  25       1.693  15.919  -0.061  0.22  2.48           C
ATOM    488  CG2BILE A  25       0.955  13.756   0.691  0.21  2.16           C
ATOM    489  CG2CILE A  25       0.939  13.672   0.877  0.22  2.83           C
ATOM    490  CD1BILE A  25       0.819  16.720   0.588  0.21  1.98           C
ATOM    491  CD1CILE A  25       1.188  15.934  -1.404  0.22  3.60           C
ATOM    492  H  BILE A  25       4.733  15.199   0.495  0.21  1.94           H
ATOM    493  H  CILE A  25       4.733  15.199   0.495  0.22  1.94           H
ATOM    494  HA BILE A  25       2.567  15.612   2.380  0.21  1.77           H
ATOM    495  HA CILE A  25       2.567  15.612   2.380  0.22  1.77           H
ATOM    496  HB BILE A  25       2.872  13.991  -0.145  0.21  4.26           H
ATOM    497  HB CILE A  25       2.808  14.078  -0.229  0.22  4.26           H
ATOM    498 HG12BILE A  25       1.534  15.605  -1.263  0.21  4.26           H
ATOM    499 HG12CILE A  25       0.897  16.295   0.598  0.22  4.26           H
ATOM    500 HG13BILE A  25       2.851  16.443  -0.399  0.21  4.26           H
ATOM    501 HG13CILE A  25       2.521  16.639  -0.008  0.22  4.26           H
ATOM    502 HG21BILE A  25       1.203  12.817   1.205  0.21  5.32           H
ATOM    503 HG21CILE A  25       0.421  13.388  -0.050  0.22  5.32           H
ATOM    504 HG22BILE A  25       0.522  13.531  -0.294  0.21  5.32           H
ATOM    505 HG22CILE A  25       1.282  12.766   1.397  0.22  5.32           H
ATOM    506 HG23BILE A  25       0.227  14.321   1.290  0.21  5.32           H
ATOM    507 HG23CILE A  25       0.249  14.228   1.527  0.22  5.32           H
ATOM    508 HD11BILE A  25       0.481  17.578  -0.010  0.21  5.32           H
ATOM    509 HD12BILE A  25       1.275  17.081   1.521  0.21  5.32           H
ATOM    510 HD13BILE A  25      -0.041  16.078   0.825  0.21  5.32           H
ATOM    511  N   CYS A  26       4.028  12.634   2.294  1.00  1.57           N
ANISOU  511  N   CYS A  26      215    187    192     32     27      4       N
ATOM    512  CA  CYS A  26       4.137  11.461   3.154  1.00  1.52           C
ANISOU  512  CA  CYS A  26      213    184    179     24      5    -11       C
ATOM    513  C   CYS A  26       4.607  11.823   4.564  1.00  1.58           C
ANISOU  513  C   CYS A  26      228    208    162     22     18     -7       C
ATOM    514  O   CYS A  26       4.231  11.137   5.527  1.00  2.03           O
ANISOU  514  O   CYS A  26      309    259    201     54     17    -60       O
ATOM    515  CB  CYS A  26       5.038  10.395   2.541  1.00  1.82           C
ANISOU  515  CB  CYS A  26      257    205    228      0      5     17       C
ATOM    516  SG  CYS A  26       4.363   9.697   1.004  1.00  2.01           S
ANISOU  516  SG  CYS A  26      362    216    186      0      6     14       S
ATOM    517  H   CYS A  26       4.606  12.743   1.485  1.00  1.87           H
ATOM    518  HA  CYS A  26       3.132  11.025   3.248  1.00  1.81           H
ATOM    519  HB2 CYS A  26       6.023  10.835   2.331  1.00  2.18           H
ATOM    520  HB3 CYS A  26       5.181   9.584   3.269  1.00  2.18           H
ATOM    521  N   ALA A  27       5.399  12.889   4.697  1.00  1.58           N
ANISOU  521  N   ALA A  27      213    227    161     19     11    -17       N
ATOM    522  CA  ALA A  27       5.848  13.355   6.011  1.00  1.58           C
ANISOU  522  CA  ALA A  27      192    236    170     23     -1     -5       C
ATOM    523  C   ALA A  27       4.662  13.846   6.849  1.00  1.61           C
ANISOU  523  C   ALA A  27      202    216    193     27      8      1       C
ATOM    524  O   ALA A  27       4.481  13.369   7.973  1.00  2.00           O
ANISOU  524  O   ALA A  27      243    343    174     42     12     24       O
ATOM    525  CB  ALA A  27       6.896  14.453   5.817  1.00  2.02           C
ANISOU  525  CB  ALA A  27      246    302    218     32     -1    -62       C
ATOM    526  H   ALA A  27       5.696  13.387   3.871  1.00  1.89           H
ATOM    527  HA  ALA A  27       6.324  12.513   6.533  1.00  1.89           H
ATOM    528  HB1 ALA A  27       7.723  14.066   5.206  1.00  3.03           H
ATOM    529  HB2 ALA A  27       7.281  14.770   6.796  1.00  3.03           H
ATOM    530  HB3 ALA A  27       6.436  15.312   5.308  1.00  3.03           H
ATOM    531  N   THR A  28       3.855  14.766   6.317  1.00  1.80           N
ANISOU  531  N   THR A  28      245    254    182     26     15     39       N
ATOM    532  CA  THR A  28       2.711  15.207   7.154  1.00  2.02           C
ANISOU  532  CA  THR A  28      247    255    263      9     37     47       C
ATOM    533  C   THR A  28       1.709  14.078   7.372  1.00  2.17           C
ANISOU  533  C   THR A  28      311    254    259     20     88     35       C
ATOM    534  O   THR A  28       1.005  14.078   8.394  1.00  3.76           O
ANISOU  534  O   THR A  28      623    383    419    -45    310    -81       O
ATOM    535  CB  THR A  28       2.024  16.440   6.551  1.00  2.05           C
ANISOU  535  CB  THR A  28      226    215    338      1     -1      9       C
ATOM    536  OG1 THR A  28       1.701  16.141   5.201  1.00  2.19           O
ANISOU  536  OG1 THR A  28      244    241    345      5    -30     17       O
ATOM    537  CG2 THR A  28       2.895  17.679   6.662  1.00  2.85           C
ANISOU  537  CG2 THR A  28      306    269    506    -17    -53    -49       C
ATOM    538  H   THR A  28       4.002  15.153   5.404  1.00  2.16           H
ATOM    539  HA  THR A  28       3.109  15.487   8.125  1.00  2.41           H
ATOM    540  HB  THR A  28       1.090  16.619   7.102  1.00  2.46           H
ATOM    541  HG1 THR A  28       0.931  16.659   4.931  1.00  3.28           H
ATOM    542 HG21 THR A  28       2.374  18.534   6.209  1.00  4.24           H
ATOM    543 HG22 THR A  28       3.844  17.507   6.135  1.00  4.24           H
ATOM    544 HG23 THR A  28       3.096  17.891   7.721  1.00  4.24           H
ATOM    545  N   TYR A  29       1.615  13.121   6.447  1.00  1.81           N
ANISOU  545  N   TYR A  29      202    265    219     40     21     29       N
ATOM    546  CA  TYR A  29       0.683  12.006   6.638  1.00  2.09           C
ANISOU  546  CA  TYR A  29      178    346    269    104      6      0       C
ATOM    547  C   TYR A  29       1.098  11.099   7.795  1.00  1.98           C
ANISOU  547  C   TYR A  29      184    340    225     88     36     25       C
ATOM    548  O   TYR A  29       0.235  10.553   8.485  1.00  3.44           O
ANISOU  548  O   TYR A  29      217    653    437    311     80     28       O
ATOM    549  CB  TYR A  29       0.610  11.302   5.324  1.00  3.00           C
ANISOU  549  CB  TYR A  29      393    453    291     72    -28   -149       C
ATOM    550  CG ATYR A  29       0.080   9.859   5.257  0.36  2.22           C
ATOM    551  CG BTYR A  29      -0.574  10.377   5.324  0.31  1.83           C
ATOM    552  CG CTYR A  29      -0.126   9.896   5.414  0.33  5.29           C
ATOM    553  CD1ATYR A  29      -1.270   9.619   5.525  0.36  2.53           C
ATOM    554  CD1BTYR A  29      -1.804  10.544   5.928  0.31  2.68           C
ATOM    555  CD1CTYR A  29      -1.474   9.767   5.525  0.33  6.05           C
ATOM    556  CD2ATYR A  29       0.939   8.787   4.966  0.36  2.12           C
ATOM    557  CD2BTYR A  29      -0.364   9.249   4.564  0.31  8.57           C
ATOM    558  CD2CTYR A  29       0.569   8.620   5.369  0.33  7.83           C
ATOM    559  CE1ATYR A  29      -1.759   8.287   5.481  0.36  2.69           C
ATOM    560  CE1BTYR A  29      -2.782   9.582   5.794  0.31  2.70           C
ATOM    561  CE1CTYR A  29      -2.209   8.565   5.593  0.33  5.76           C
ATOM    562  CE2ATYR A  29       0.450   7.473   4.944  0.36  2.09           C
ATOM    563  CE2BTYR A  29      -1.342   8.324   4.429  0.31 10.63           C
ATOM    564  CE2CTYR A  29      -0.126   7.362   5.458  0.33  7.19           C
ATOM    565  CZ ATYR A  29      -0.900   7.233   5.212  0.36  2.14           C
ATOM    566  CZ BTYR A  29      -2.572   8.472   5.033  0.31  5.29           C
ATOM    567  CZ CTYR A  29      -1.474   7.381   5.570  0.33  6.65           C
ATOM    568  OH ATYR A  29      -1.390   5.956   5.212  0.36  2.52           O
ATOM    569  OH BTYR A  29      -3.510   7.492   4.877  0.31  7.13           O
ATOM    570  OH CTYR A  29      -2.251   6.252   5.660  0.33  7.72           O
ATOM    571  H   TYR A  29       2.187  13.164   5.617  1.00  2.17           H
ATOM    572  HA  TYR A  29      -0.310  12.421   6.863  1.00  2.50           H
ATOM    573  HB2 TYR A  29      -0.017  11.913   4.659  1.00  3.68           H
ATOM    574  HB3 TYR A  29       1.622  11.300   4.897  1.00  3.68           H
ATOM    575  HD1ATYR A  29      -1.945  10.451   5.769  0.36  3.68           H
ATOM    576  HD1BTYR A  29      -2.004  11.448   6.519  0.31  3.68           H
ATOM    577  HD1CTYR A  29      -2.054  10.699   5.568  0.33  3.68           H
ATOM    578  HD2ATYR A  29       2.001   8.978   4.755  0.36  3.68           H
ATOM    579  HD2BTYR A  29       0.603   9.099   4.063  0.31  3.68           H
ATOM    580  HD2CTYR A  29       1.662   8.615   5.263  0.33  3.68           H
ATOM    581  HE1ATYR A  29      -2.826   8.091   5.660  0.36  3.68           H
ATOM    582  HE1BTYR A  29      -3.745   9.713   6.308  0.31  3.68           H
ATOM    583  HE1CTYR A  29      -3.306   8.562   5.659  0.33  3.68           H
ATOM    584  HE2ATYR A  29       1.125   6.636   4.716  0.36  3.68           H
ATOM    585  HE2BTYR A  29      -1.151   7.429   3.821  0.31  3.68           H
ATOM    586  HE2CTYR A  29       0.425   6.411   5.436  0.33  3.68           H
ATOM    587  HH ATYR A  29      -0.676   5.337   5.006  0.36  4.60           H
ATOM    588  HH BTYR A  29      -4.307   7.726   5.372  0.31  4.60           H
ATOM    589  HH CTYR A  29      -3.152   6.458   5.376  0.33  4.60           H
ATOM    590  N   THR A  30       2.412  10.896   7.976  1.00  1.83           N
ANISOU  590  N   THR A  30      182    250    262     82     26     10       N
ATOM    591  CA  THR A  30       2.926   9.885   8.890  1.00  2.32           C
ANISOU  591  CA  THR A  30      234    283    364    159     62     36       C
ATOM    592  C   THR A  30       3.531  10.416  10.185  1.00  2.73           C
ANISOU  592  C   THR A  30      227    477    332    210     30     29       C
ATOM    593  O   THR A  30       3.704   9.609  11.108  1.00  4.05           O
ANISOU  593  O   THR A  30      449    707    380    332      0     37       O
ATOM    594  CB  THR A  30       4.031   9.054   8.197  1.00  3.05           C
ANISOU  594  CB  THR A  30      324    290    544    190    141    102       C
ATOM    595  OG1 THR A  30       5.123   9.910   7.843  1.00  2.66           O
ANISOU  595  OG1 THR A  30      230    431    348    165     42     68       O
ATOM    596  CG2 THR A  30       3.499   8.284   7.008  1.00  4.52           C
ANISOU  596  CG2 THR A  30      613    251    852    -75    252    -57       C
ATOM    597  H   THR A  30       3.067  11.463   7.460  1.00  2.20           H
ATOM    598  HA  THR A  30       2.101   9.207   9.151  1.00  2.77           H
ATOM    599  HB  THR A  30       4.405   8.323   8.928  1.00  3.68           H
ATOM    600  HG1 THR A  30       4.859  10.481   7.108  1.00  3.93           H
ATOM    601 HG21 THR A  30       4.315   7.705   6.553  1.00  6.77           H
ATOM    602 HG22 THR A  30       3.091   8.987   6.269  1.00  6.77           H
ATOM    603 HG23 THR A  30       2.706   7.600   7.340  1.00  6.77           H
ATOM    604  N   GLY A  31       3.931  11.687  10.203  1.00  2.56           N
ANISOU  604  N   GLY A  31      203    496    272    119     16      3       N
ATOM    605  CA  GLY A  31       4.732  12.209  11.290  1.00  3.13           C
ANISOU  605  CA  GLY A  31      231    727    229     24     38     49       C
ATOM    606  C   GLY A  31       6.229  12.148  11.039  1.00  2.12           C
ANISOU  606  C   GLY A  31      221    372    212     22     15     24       C
ATOM    607  O   GLY A  31       6.995  12.658  11.864  1.00  2.49           O
ANISOU  607  O   GLY A  31      288    419    239    -65    -14     60       O
ATOM    608  H   GLY A  31       3.671  12.298   9.443  1.00  3.08           H
ATOM    609  HA2 GLY A  31       4.446  13.255  11.469  1.00  3.72           H
ATOM    610  HA3 GLY A  31       4.503  11.640  12.202  1.00  3.72           H
ATOM    611  N   CYS A  32       6.670  11.511   9.952  1.00  1.96           N
ANISOU  611  N   CYS A  32      202    347    195     15     23    -44       N
ATOM    612  CA  CYS A  32       8.069  11.595   9.568  1.00  1.82           C
ANISOU  612  CA  CYS A  32      198    260    231     -9     30    -42       C
ATOM    613  C   CYS A  32       8.384  13.045   9.130  1.00  1.88           C
ANISOU  613  C   CYS A  32      227    253    231     -6     37    -14       C
ATOM    614  O   CYS A  32       7.488  13.854   8.918  1.00  2.55           O
ANISOU  614  O   CYS A  32      262    348    359     95     -6     18       O
ATOM    615  CB  CYS A  32       8.382  10.621   8.435  1.00  1.92           C
ANISOU  615  CB  CYS A  32      249    256    223     -4     35    -35       C
ATOM    616  SG  CYS A  32       8.012   8.869   8.821  1.00  2.05           S
ANISOU  616  SG  CYS A  32      247    246    283      0    -21    -76       S
ATOM    617  H   CYS A  32       6.029  10.967   9.394  1.00  2.35           H
ATOM    618  HA  CYS A  32       8.693  11.342  10.437  1.00  2.18           H
ATOM    619  HB2 CYS A  32       7.803  10.915   7.548  1.00  2.31           H
ATOM    620  HB3 CYS A  32       9.447  10.708   8.181  1.00  2.31           H
ATOM    621  N   ILE A  33       9.688  13.311   8.988  1.00  2.20           N
ANISOU  621  N   ILE A  33      235    204    395    -32     98    -13       N
ATOM    622  CA  ILE A  33      10.176  14.645   8.666  1.00  2.19           C
ANISOU  622  CA  ILE A  33      277    206    349    -24    107    -22       C
ATOM    623  C   ILE A  33      11.242  14.531   7.578  1.00  2.20           C
ANISOU  623  C   ILE A  33      233    279    322    -29     77    -35       C
ATOM    624  O   ILE A  33      11.868  13.485   7.382  1.00  2.85           O
ANISOU  624  O   ILE A  33      357    311    413     -3    161     20       O
ATOM    625  CB  ILE A  33      10.748  15.355   9.917  1.00  2.70           C
ANISOU  625  CB  ILE A  33      439    191    395    -44     65    -50       C
ATOM    626  CG1 ILE A  33      11.996  14.655  10.484  1.00  3.08           C
ANISOU  626  CG1 ILE A  33      489    297    384      0    -27    -71       C
ATOM    627  CG2 ILE A  33       9.654  15.480  10.971  1.00  3.59           C
ANISOU  627  CG2 ILE A  33      662    336    362    -85    146     70       C
ATOM    628  CD1 ILE A  33      12.693  15.430  11.579  1.00  4.51           C
ANISOU  628  CD1 ILE A  33      767    424    520    -10   -153   -211       C
ATOM    629  H   ILE A  33      10.355  12.563   9.108  1.00  2.63           H
ATOM    630  HA  ILE A  33       9.337  15.241   8.279  1.00  2.63           H
ATOM    631  HB  ILE A  33      11.042  16.371   9.619  1.00  3.24           H
ATOM    632 HG12 ILE A  33      11.700  13.673  10.880  1.00  3.73           H
ATOM    633 HG13 ILE A  33      12.707  14.483   9.665  1.00  3.73           H
ATOM    634 HG21 ILE A  33       8.779  15.981  10.533  1.00  5.36           H
ATOM    635 HG22 ILE A  33      10.028  16.071  11.819  1.00  5.36           H
ATOM    636 HG23 ILE A  33       9.366  14.479  11.321  1.00  5.36           H
ATOM    637 HD11 ILE A  33      13.561  14.857  11.937  1.00  6.68           H
ATOM    638 HD12 ILE A  33      11.996  15.596  12.412  1.00  6.68           H
ATOM    639 HD13 ILE A  33      13.031  16.398  11.185  1.00  6.68           H
ATOM    640  N   ILE A  34      11.452  15.662   6.905  1.00  2.63           N
ANISOU  640  N   ILE A  34      241    321    436     39    116     -7       N
ATOM    641  CA  ILE A  34      12.511  15.815   5.919  1.00  2.58           C
ANISOU  641  CA  ILE A  34      224    389    368     38     73    -38       C
ATOM    642  C   ILE A  34      13.505  16.814   6.473  1.00  2.65           C
ANISOU  642  C   ILE A  34      225    324    454     92     30    -25       C
ATOM    643  O   ILE A  34      13.103  17.913   6.899  1.00  3.64           O
ANISOU  643  O   ILE A  34      306    371    703     -9    -11     13       O
ATOM    644  CB AILE A  34      11.943  16.410   4.601  0.77  2.58           C
ANISOU  644  CB AILE A  34      249    394    337    -51      8    -52       C
ATOM    645  CB BILE A  34      11.930  15.960   4.530  0.23  2.82           C
ATOM    646  CG1AILE A  34      10.907  15.505   3.988  0.77  3.88           C
ANISOU  646  CG1AILE A  34      306    504    662   -216    -93    -39       C
ATOM    647  CG1BILE A  34      10.646  15.066   4.227  0.23  3.42           C
ATOM    648  CG2AILE A  34      13.188  16.567   3.597  0.77  4.54           C
ANISOU  648  CG2AILE A  34      354   1129    242     28     24   -103       C
ATOM    649  CG2BILE A  34      12.953  15.674   3.361  0.23  5.02           C
ATOM    650  CD1AILE A  34      10.214  16.126   2.774  0.77  4.86           C
ANISOU  650  CD1AILE A  34      362   1061    423   -390   -112    106       C
ATOM    651  CD1BILE A  34      10.915  13.658   4.166  0.23  4.90           C
ATOM    652  H   ILE A  34      10.850  16.457   7.091  1.00  3.16           H
ATOM    653  HA  ILE A  34      12.999  14.860   5.732  1.00  3.11           H
ATOM    654  HB AILE A  34      11.546  17.419   4.767  0.77  3.18           H
ATOM    655  HB BILE A  34      11.594  17.042   4.417  0.23  5.82           H
ATOM    656 HG12AILE A  34      11.379  14.558   3.690  0.77  4.67           H
ATOM    657 HG12BILE A  34      10.000  15.400   4.720  0.23  5.82           H
ATOM    658 HG13AILE A  34      10.168  15.285   4.769  0.77  4.67           H
ATOM    659 HG13BILE A  34      10.570  15.490   3.330  0.23  5.82           H
ATOM    660 HG21AILE A  34      13.924  17.239   4.042  0.77  6.79           H
ATOM    661 HG21BILE A  34      12.468  16.057   2.467  0.23  7.28           H
ATOM    662 HG22AILE A  34      12.804  17.021   2.656  0.77  6.79           H
ATOM    663 HG22BILE A  34      13.188  14.712   3.412  0.23  7.28           H
ATOM    664 HG23AILE A  34      13.602  15.595   3.398  0.77  6.79           H
ATOM    665 HG23BILE A  34      13.798  16.386   3.626  0.23  7.28           H
ATOM    666 HD11AILE A  34       9.436  15.451   2.406  0.77  7.28           H
ATOM    667 HD11BILE A  34       9.905  13.064   4.008  0.23  7.28           H
ATOM    668 HD12AILE A  34      10.947  16.322   1.983  0.77  7.28           H
ATOM    669 HD12BILE A  34      11.310  13.266   5.107  0.23  7.28           H
ATOM    670 HD13AILE A  34       9.746  17.087   3.076  0.77  7.28           H
ATOM    671 HD13BILE A  34      11.540  13.357   3.329  0.23  7.28           H
ATOM    672  N   ILE A  35      14.790  16.458   6.442  1.00  2.97           N
ANISOU  672  N   ILE A  35      215    362    549     72     49    -34       N
ATOM    673  CA  ILE A  35      15.847  17.376   6.893  1.00  3.14           C
ANISOU  673  CA  ILE A  35      266    456    470     71     28    -82       C
ATOM    674  C   ILE A  35      16.855  17.522   5.750  1.00  3.18           C
ANISOU  674  C   ILE A  35      230    395    581    126     61    -35       C
ATOM    675  O   ILE A  35      17.024  16.622   4.923  1.00  3.74           O
ANISOU  675  O   ILE A  35      309    467    642     60    112    -69       O
ATOM    676  CB  ILE A  35      16.545  16.890   8.176  1.00  4.30           C
ANISOU  676  CB  ILE A  35      375    709    549    195    -60   -200       C
ATOM    677  CG1 ILE A  35      17.227  15.531   7.987  1.00  4.97           C
ANISOU  677  CG1 ILE A  35      434    695    757    364   -155   -134       C
ATOM    678  CG2 ILE A  35      15.532  16.851   9.299  1.00  6.65           C
ANISOU  678  CG2 ILE A  35      625   1404    496    182     17   -321       C
ATOM    679  CD1 ILE A  35      18.146  15.152   9.138  1.00  7.82           C
ANISOU  679  CD1 ILE A  35      588   1219   1163    767   -423   -377       C
ATOM    680  H   ILE A  35      15.032  15.548   6.123  1.00  3.56           H
ATOM    681  HA  ILE A  35      15.402  18.361   7.092  1.00  3.77           H
ATOM    682  HB  ILE A  35      17.318  17.624   8.441  1.00  5.14           H
ATOM    683 HG12 ILE A  35      16.455  14.757   7.878  1.00  6.02           H
ATOM    684 HG13 ILE A  35      17.812  15.553   7.057  1.00  6.02           H
ATOM    685 HG21 ILE A  35      15.093  17.849   9.432  1.00  9.79           H
ATOM    686 HG22 ILE A  35      16.028  16.541  10.230  1.00  9.79           H
ATOM    687 HG23 ILE A  35      14.738  16.132   9.051  1.00  9.79           H
ATOM    688 HD11 ILE A  35      18.613  14.179   8.930  1.00 11.67           H
ATOM    689 HD12 ILE A  35      17.562  15.087  10.067  1.00 11.67           H
ATOM    690 HD13 ILE A  35      18.928  15.917   9.251  1.00 11.67           H
ATOM    691  N   PRO A  36      17.593  18.645   5.733  1.00  3.57           N
ANISOU  691  N   PRO A  36      284    402    669    147     52    -59       N
ATOM    692  CA  PRO A  36      18.581  18.845   4.683  1.00  3.77           C
ANISOU  692  CA  PRO A  36      308    513    609    202     20   -109       C
ATOM    693  C   PRO A  36      19.866  18.079   4.953  1.00  4.27           C
ANISOU  693  C   PRO A  36      260    597    764    159     58    -96       C
ATOM    694  O   PRO A  36      20.605  17.835   3.982  1.00  6.26           O
ANISOU  694  O   PRO A  36      421    977    981     89    245    -54       O
ATOM    695  CB APRO A  36      18.725  20.367   4.596  0.68  4.58           C
ANISOU  695  CB APRO A  36      438    532    770    346    -48   -139       C
ATOM    696  CB BPRO A  36      19.047  20.307   4.847  0.32  7.48           C
ANISOU  696  CB BPRO A  36      625    447   1769    246    491   -144       C
ATOM    697  CG APRO A  36      18.403  20.829   6.030  0.68  4.64           C
ANISOU  697  CG APRO A  36      511    431    821    136   -227   -208       C
ATOM    698  CG BPRO A  36      18.192  20.880   5.853  0.32  7.85           C
ANISOU  698  CG BPRO A  36      982    586   1414    -40    390   -362       C
ATOM    699  CD  PRO A  36      17.286  19.902   6.471  1.00  4.70           C
ANISOU  699  CD  PRO A  36      470    447    866     18     44   -109       C
ATOM    700  HA  PRO A  36      18.154  18.485   3.736  1.00  4.52           H
ATOM    701  HB2APRO A  36      19.746  20.653   4.307  0.68  5.43           H
ATOM    702  HB2BPRO A  36      20.098  20.345   5.166  0.32  8.94           H
ATOM    703  HB3APRO A  36      18.015  20.792   3.873  0.68  5.43           H
ATOM    704  HB3BPRO A  36      18.947  20.854   3.898  0.32  8.94           H
ATOM    705  HG2APRO A  36      19.281  20.726   6.683  0.68  5.53           H
ATOM    706  HG2BPRO A  36      18.817  21.332   6.637  0.32  9.50           H
ATOM    707  HG3APRO A  36      18.072  21.877   6.041  0.68  5.53           H
ATOM    708  HG3BPRO A  36      17.594  21.682   5.399  0.32  9.50           H
ATOM    709  HD2 PRO A  36      17.309  19.741   7.558  1.00  5.61           H
ATOM    710  HD3 PRO A  36      16.302  20.301   6.186  1.00  5.61           H
ATOM    711  N   GLY A  37      20.154  17.799   6.202  1.00  4.59           N
ANISOU  711  N   GLY A  37      281    589    872    257    -88    -91       N
ATOM    712  CA  GLY A  37      21.334  17.013   6.608  1.00  6.65           C
ANISOU  712  CA  GLY A  37      318    583   1627    402   -328   -165       C
ATOM    713  C   GLY A  37      21.082  15.528   6.415  1.00  5.02           C
ANISOU  713  C   GLY A  37      252    600   1056    272   -141   -118       C
ATOM    714  O   GLY A  37      20.097  15.097   5.840  1.00  6.64           O
ANISOU  714  O   GLY A  37      391    663   1469    188   -374    -94       O
ATOM    715  H   GLY A  37      19.534  18.130   6.933  1.00  5.48           H
ATOM    716  HA2 GLY A  37      22.187  17.355   5.979  1.00  7.83           H
ATOM    717  HA3 GLY A  37      21.574  17.256   7.647  1.00  7.83           H
ATOM    718  N   ALA A  38      22.008  14.746   6.971  1.00  4.34           N
ANISOU  718  N   ALA A  38      276    539    832    236    -85   -113       N
ATOM    719  CA  ALA A  38      21.995  13.320   6.837  1.00  4.98           C
ANISOU  719  CA  ALA A  38      363    554    972    156   -141   -110       C
ATOM    720  C   ALA A  38      21.843  12.609   8.193  1.00  5.36           C
ANISOU  720  C   ALA A  38      334    532   1168    324    -76   -102       C
ATOM    721  O   ALA A  38      21.806  11.376   8.221  1.00  7.76           O
ANISOU  721  O   ALA A  38      889    535   1524    383   -155    -99       O
ATOM    722  CB  ALA A  38      23.235  12.802   6.109  1.00  6.76           C
ANISOU  722  CB  ALA A  38      632    839   1096    -39     38    -48       C
ATOM    723  H   ALA A  38      22.755  15.183   7.494  1.00  5.19           H
ATOM    724  HA  ALA A  38      21.120  13.055   6.227  1.00  5.95           H
ATOM    725  HB1 ALA A  38      23.289  13.257   5.110  1.00  9.94           H
ATOM    726  HB2 ALA A  38      23.172  11.710   6.011  1.00  9.94           H
ATOM    727  HB3 ALA A  38      24.134  13.068   6.682  1.00  9.94           H
ATOM    728  N   THR A  39      21.787  13.377   9.290  1.00  4.88           N
ANISOU  728  N   THR A  39      218    678    956    429     -8    -48       N
ATOM    729  CA  THR A  39      21.840  12.801  10.610  1.00  5.83           C
ANISOU  729  CA  THR A  39      211    946   1059    605      2    -86       C
ATOM    730  C   THR A  39      20.535  13.026  11.330  1.00  4.95           C
ANISOU  730  C   THR A  39      264    715    899    364    -32   -131       C
ATOM    731  O   THR A  39      20.250  14.149  11.772  1.00  6.84           O
ANISOU  731  O   THR A  39      578    710   1308    172    -23   -278       O
ATOM    732  CB ATHR A  39      23.123  13.277  11.318  0.57  7.03           C
ANISOU  732  CB ATHR A  39       62   1559   1048    754     -8    -64       C
ATOM    733  CB BTHR A  39      22.850  13.578  11.475  0.43  5.67           C
ANISOU  733  CB BTHR A  39      144   1182    827    556      8      6       C
ATOM    734  OG1ATHR A  39      24.242  13.046  10.381  0.57  5.41           O
ANISOU  734  OG1ATHR A  39      241    829    985    532      5    -48       O
ATOM    735  OG1BTHR A  39      24.173  13.586  10.841  0.43  3.62           O
ANISOU  735  OG1BTHR A  39      175    468    729    233     15    -44       O
ATOM    736  CG2ATHR A  39      23.351  12.187  12.361  0.57  6.86           C
ANISOU  736  CG2ATHR A  39      420   1462    722    530     15     60       C
ATOM    737  CG2BTHR A  39      23.191  12.939  12.903  0.43  5.02           C
ANISOU  737  CG2BTHR A  39      356    965    586    271     20    -38       C
ATOM    738  H   THR A  39      21.706  14.378   9.190  1.00  5.83           H
ATOM    739  HA  THR A  39      21.940  11.715  10.475  1.00  6.89           H
ATOM    740  HB BTHR A  39      22.501  14.611  11.609  0.43  6.13           H
ATOM    741 HG21BTHR A  39      23.929  13.568  13.419  0.43  7.66           H
ATOM    742 HG22BTHR A  39      23.602  11.930  12.764  0.43  7.66           H
ATOM    743 HG23BTHR A  39      22.274  12.881  13.506  0.43  7.66           H
ATOM    744  N   CYS A  40      19.748  11.982  11.477  1.00  4.08           N
ANISOU  744  N   CYS A  40      236    598    713    197     67    -62       N
ATOM    745  CA  CYS A  40      18.460  12.120  12.139  1.00  3.64           C
ANISOU  745  CA  CYS A  40      226    564    591    106     12    -48       C
ATOM    746  C   CYS A  40      18.660  12.202  13.669  1.00  3.83           C
ANISOU  746  C   CYS A  40      242    596    616     31    -56    -14       C
ATOM    747  O   CYS A  40      19.515  11.523  14.227  1.00  4.96           O
ANISOU  747  O   CYS A  40      319    845    719     -9   -116    134       O
ATOM    748  CB  CYS A  40      17.591  10.914  11.825  1.00  3.70           C
ANISOU  748  CB  CYS A  40      243    613    549    100     36    -91       C
ATOM    749  SG  CYS A  40      17.124  10.807  10.067  1.00  4.08           S
ANISOU  749  SG  CYS A  40      295    711    543      2    146    -61       S
ATOM    750  H   CYS A  40      20.039  11.081  11.128  1.00  4.91           H
ATOM    751  HA  CYS A  40      17.962  13.033  11.784  1.00  4.36           H
ATOM    752  HB2 CYS A  40      18.133  10.000  12.107  1.00  4.44           H
ATOM    753  HB3 CYS A  40      16.678  10.963  12.435  1.00  4.44           H
ATOM    754  N   PRO A  41      17.847  13.009  14.329  1.00  4.47           N
ANISOU  754  N   PRO A  41      271    627    798    -71    -62     -1       N
ATOM    755  CA  PRO A  41      17.975  13.139  15.787  1.00  4.95           C
ANISOU  755  CA  PRO A  41      378    686    816   -185    -69    -72       C
ATOM    756  C   PRO A  41      17.355  11.965  16.530  1.00  4.16           C
ANISOU  756  C   PRO A  41      287    660    631   -214    -60     19       C
ATOM    757  O   PRO A  41      16.627  11.147  15.969  1.00  4.00           O
ANISOU  757  O   PRO A  41      296    672    549   -189    -27    -11       O
ATOM    758  CB  PRO A  41      17.215  14.451  16.070  1.00  6.44           C
ANISOU  758  CB  PRO A  41      693    607   1145   -292     -4    -91       C
ATOM    759  CG  PRO A  41      16.102  14.430  15.016  1.00  5.94           C
ANISOU  759  CG  PRO A  41      523    553   1180    -76     62    111       C
ATOM    760  CD  PRO A  41      16.799  13.881  13.768  1.00  5.16           C
ANISOU  760  CD  PRO A  41      404    583    970     63    -15     50       C
ATOM    761  HA  PRO A  41      19.033  13.246  16.065  1.00  5.97           H
ATOM    762  HB2 PRO A  41      16.800  14.459  17.088  1.00  7.65           H
ATOM    763  HB3 PRO A  41      17.869  15.325  15.941  1.00  7.65           H
ATOM    764  HG2 PRO A  41      15.277  13.774  15.328  1.00  7.13           H
ATOM    765  HG3 PRO A  41      15.709  15.440  14.837  1.00  7.13           H
ATOM    766  HD2 PRO A  41      16.100  13.309  13.143  1.00  6.20           H
ATOM    767  HD3 PRO A  41      17.236  14.692  13.169  1.00  6.20           H
ATOM    768  N   GLY A  42      17.643  11.915  17.853  1.00  4.91           N
ANISOU  768  N   GLY A  42      421    742    702   -247   -217    119       N
ATOM    769  CA  GLY A  42      17.226  10.779  18.683  1.00  5.06           C
ANISOU  769  CA  GLY A  42      535    691    695   -181   -270    265       C
ATOM    770  C   GLY A  42      15.746  10.584  18.832  1.00  4.15           C
ANISOU  770  C   GLY A  42      578    515    480   -107   -188    204       C
ATOM    771  O   GLY A  42      15.331   9.485  19.187  1.00  6.31           O
ANISOU  771  O   GLY A  42      720    442   1235    -32   -364    174       O
ATOM    772  H   GLY A  42      18.156  12.674  18.276  1.00  5.91           H
ATOM    773  HA2 GLY A  42      17.653   9.863  18.253  1.00  6.06           H
ATOM    774  HA3 GLY A  42      17.660  10.906  19.684  1.00  6.06           H
ATOM    775  N   ASP A  43      14.940  11.626  18.615  1.00  3.30           N
ANISOU  775  N   ASP A  43      444    478    330    -98    -69    150       N
ATOM    776  CA  ASP A  43      13.491  11.518  18.676  1.00  3.12           C
ANISOU  776  CA  ASP A  43      454    452    278    -52      3    135       C
ATOM    777  C   ASP A  43      12.866  11.265  17.292  1.00  2.37           C
ANISOU  777  C   ASP A  43      322    311    264    -36     63     47       C
ATOM    778  O   ASP A  43      11.637  11.131  17.212  1.00  2.79           O
ANISOU  778  O   ASP A  43      321    408    331    -20    129      0       O
ATOM    779  CB AASP A  43      13.091  12.931  19.136  0.25  3.47           C
ATOM    780  CB BASP A  43      12.802  12.630  19.421  0.75  2.76           C
ANISOU  780  CB BASP A  43      398    376    273    -49     99      1       C
ATOM    781  CG AASP A  43      13.560  14.348  18.472  0.25  3.47           C
ATOM    782  CG BASP A  43      13.085  14.014  18.859  0.75  2.63           C
ANISOU  782  CG BASP A  43      302    318    379    -88     45      4       C
ATOM    783  OD1AASP A  43      14.415  14.363  17.612  0.25  4.15           O
ATOM    784  OD1BASP A  43      14.068  14.164  18.085  0.75  3.64           O
ANISOU  784  OD1BASP A  43      474    336    572    -10    221      3       O
ATOM    785  OD2AASP A  43      12.986  15.459  18.868  0.25  5.01           O
ANISOU  785  OD2AASP A  43      625    613    664     19    323    131       O
ATOM    786  OD2BASP A  43      12.311  14.944  19.211  0.75  3.43           O
ANISOU  786  OD2BASP A  43      402    366    533    -88    109     66       O
ATOM    787  H   ASP A  43      15.352  12.521  18.399  1.00  3.95           H
ATOM    788  HA  ASP A  43      13.177  10.756  19.403  1.00  3.76           H
ATOM    789  HB2AASP A  43      11.992  12.947  19.118  0.25  3.76           H
ATOM    790  HB2BASP A  43      11.717  12.453  19.397  0.75  3.36           H
ATOM    791  HB3AASP A  43      13.380  12.990  20.194  0.25  3.76           H
ATOM    792  HB3BASP A  43      13.121  12.603  20.473  0.75  3.36           H
ATOM    793  N   TYR A  44      13.711  11.175  16.260  1.00  2.18           N
ANISOU  793  N   TYR A  44      245    301    280    -51     46      8       N
ATOM    794  CA  TYR A  44      13.267  10.722  14.926  1.00  1.98           C
ANISOU  794  CA  TYR A  44      197    260    294    -47     49    -21       C
ATOM    795  C   TYR A  44      14.251   9.661  14.439  1.00  2.25           C
ANISOU  795  C   TYR A  44      187    297    369    -68     91    -27       C
ATOM    796  O   TYR A  44      14.931   9.812  13.426  1.00  2.78           O
ANISOU  796  O   TYR A  44      291    383    379    -75    149    -36       O
ATOM    797  CB  TYR A  44      13.132  11.883  13.924  1.00  2.40           C
ANISOU  797  CB  TYR A  44      286    336    288     -1     79    -24       C
ATOM    798  CG  TYR A  44      11.978  12.797  14.251  1.00  2.26           C
ANISOU  798  CG  TYR A  44      262    274    319     -1     20    -37       C
ATOM    799  CD1 TYR A  44      12.083  13.835  15.179  1.00  2.62           C
ANISOU  799  CD1 TYR A  44      295    304    397    -52    -29    -27       C
ATOM    800  CD2 TYR A  44      10.765  12.585  13.608  1.00  2.35           C
ANISOU  800  CD2 TYR A  44      286    316    289    -48     10    -29       C
ATOM    801  CE1 TYR A  44      10.989  14.643  15.462  1.00  2.71           C
ANISOU  801  CE1 TYR A  44      327    280    420    -67    -25    -18       C
ATOM    802  CE2 TYR A  44       9.649  13.380  13.883  1.00  2.41           C
ANISOU  802  CE2 TYR A  44      275    339    301    -40    -15    -15       C
ATOM    803  CZ  TYR A  44       9.770  14.410  14.819  1.00  2.30           C
ANISOU  803  CZ  TYR A  44      298    250    325     -2     10     -9       C
ATOM    804  OH  TYR A  44       8.716  15.223  15.106  1.00  2.78           O
ANISOU  804  OH  TYR A  44      327    312    416    -57     -7     29       O
ATOM    805  H   TYR A  44      14.672  11.391  16.410  1.00  2.60           H
ATOM    806  HA  TYR A  44      12.279  10.275  15.025  1.00  2.38           H
ATOM    807  HB2 TYR A  44      14.063  12.462  13.920  1.00  2.87           H
ATOM    808  HB3 TYR A  44      12.987  11.459  12.924  1.00  2.87           H
ATOM    809  HD1 TYR A  44      13.039  14.015  15.690  1.00  3.16           H
ATOM    810  HD2 TYR A  44      10.682  11.777  12.868  1.00  2.81           H
ATOM    811  HE1 TYR A  44      11.081  15.462  16.189  1.00  3.27           H
ATOM    812  HE2 TYR A  44       8.693  13.197  13.372  1.00  2.90           H
ATOM    813  HH  TYR A  44       7.946  14.945  14.590  1.00  4.17           H
ATOM    814  N   ALA A  45      14.353   8.612  15.274  1.00  2.25           N
ANISOU  814  N   ALA A  45      182    307    365    -72     40     17       N
ATOM    815  CA  ALA A  45      15.411   7.633  15.171  1.00  2.49           C
ANISOU  815  CA  ALA A  45      180    369    397   -116    -10     42       C
ATOM    816  C   ALA A  45      15.176   6.504  14.196  1.00  2.46           C
ANISOU  816  C   ALA A  45      176    378    378   -116    -10     65       C
ATOM    817  O   ALA A  45      16.091   5.695  13.991  1.00  3.45           O
ANISOU  817  O   ALA A  45      191    479    638   -268    -65    110       O
ATOM    818  CB  ALA A  45      15.631   7.055  16.574  1.00  3.41           C
ANISOU  818  CB  ALA A  45      363    531    401   -107    -58    175       C
ATOM    819  H   ALA A  45      13.657   8.499  15.996  1.00  2.69           H
ATOM    820  HA  ALA A  45      16.330   8.156  14.871  1.00  2.99           H
ATOM    821  HB1 ALA A  45      15.811   7.874  17.284  1.00  5.14           H
ATOM    822  HB2 ALA A  45      16.501   6.383  16.561  1.00  5.14           H
ATOM    823  HB3 ALA A  45      14.739   6.493  16.883  1.00  5.14           H
ATOM    824  N   ASN A  46      13.968   6.428  13.644  1.00  2.37           N
ANISOU  824  N   ASN A  46      160    311    428   -111     -2     51       N
ATOM    825  CA  ASN A  46      13.545   5.347  12.780  1.00  2.48           C
ANISOU  825  CA  ASN A  46      174    316    450   -105    -41     37       C
ATOM    826  C   ASN A  46      13.314   5.798  11.331  1.00  2.63           C
ANISOU  826  C   ASN A  46      202    343    454   -112    -48     28       C
ATOM    827  O   ASN A  46      13.722   6.914  10.977  1.00  2.76           O
ANISOU  827  O   ASN A  46      279    370    398   -115     41     10       O
ATOM    828  CB  ASN A  46      12.289   4.685  13.379  1.00  3.21           C
ANISOU  828  CB  ASN A  46      220    418    579     21    -49     -5       C
ATOM    829  CG AASN A  46      12.552   4.058  14.708  0.57  3.22           C
ANISOU  829  CG AASN A  46      357    332    534    -12     20     37       C
ATOM    830  CG BASN A  46      12.511   4.381  14.835  0.43  4.18           C
ANISOU  830  CG BASN A  46      263    817    507   -121    -76     13       C
ATOM    831  OD1AASN A  46      11.884   4.464  15.644  0.57  4.43           O
ANISOU  831  OD1AASN A  46      447    749    487    -27     45     91       O
ATOM    832  OD1BASN A  46      11.976   5.015  15.832  0.43  6.89           O
ANISOU  832  OD1BASN A  46      532   1372    713   -377    163   -101       O
ATOM    833  ND2AASN A  46      13.527   3.162  14.799  0.57  4.29           N
ANISOU  833  ND2AASN A  46      569    571    487     56     -7    254       N
ATOM    834  ND2BASN A  46      13.361   3.391  15.159  0.43  6.66           N
ANISOU  834  ND2BASN A  46      512   1486    532    164     31    436       N
ATOM    835  OXT ASN A  46      12.720   4.982  10.590  1.00  3.55           O
ANISOU  835  OXT ASN A  46      401    392    553   -114   -149    -52       O
ATOM    836  H   ASN A  46      13.308   7.167  13.839  1.00  2.84           H
ATOM    837  HA  ASN A  46      14.347   4.595  12.771  1.00  2.97           H
ATOM    838  HB2 ASN A  46      11.501   5.442  13.488  1.00  3.85           H
ATOM    839  HB3 ASN A  46      11.923   3.915  12.684  1.00  3.85           H
ATOM    840 HD21AASN A  46      13.764   2.762  15.695  0.57  5.14           H
ATOM    841 HD21BASN A  46      13.547   3.183  16.129  0.43  7.99           H
ATOM    842 HD22AASN A  46      14.032   2.880  13.972  0.57  5.14           H
ATOM    843 HD22BASN A  46      13.813   2.856  14.433  0.43  7.99           H
TER     844      ASN A  46
CONECT   60  749
CONECT   70  616
CONECT  310  516
CONECT  516  310
CONECT  616   70
CONECT  749   60
MASTER      266    0    0    2    2    0    0    6  340    1    6    4
END
"""
    molecular_weight, isometric_point = calculate_protein_properties(sequence)
    hydrophobic_state = is_hydrophilic_or_hydrophobic(sequence)

    return {
        "sequence": sequence.upper(),
        "confidence": round(random.uniform(0.7, 0.95), 2),  # Mock confidence score
        "molecular_weight": molecular_weight,
        "isometric_point": isometric_point,  # Mock molecular weight
        "hydrophobic_state": hydrophobic_state,
        "pdb_data": mock_pdb,
    }
