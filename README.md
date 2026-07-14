# genolab

`genolab` is a lazy and small bioinformatics toolkit

The current commands:
1. `blastReport` → clean BLAST outfmt 6, infer strand and add normalized coordinates (because BLAST output has end - start <0).
2. `dicti`      → rename `sseqid` using a 2‑column dictionary table (check input example "old_name new_name").
3. `blastBed`   → convert the processed BLAST output into BED

---

## Project structure
```text
.
├── bin
│   └── genolab            
├── config
│   └── bed.conf           # BED aesthetics (name, score, RGB, format, zero-based)
├── input                  # example inputs
│   └── dicHSA.txt		   # example of dictionary
├── output                 # example outputs
│   └── test.bed
└── scripts                # processing logic
    ├── blastBed.R
    ├── blastReport.py
    └── dicti.sh

```

---

## Requirements

- Linux / WSL (tested on Ubuntu under WSL).
- Conda environment with:
  - Python 3
  - R (e.g. 4.5.x)
  - Bioconductor `GenomicRanges` and dependencies

Example conda setup (simplified):

```bash
conda create -n genolab python r-base
conda activate genolab

# Inside R:
# install.packages("BiocManager")
# BiocManager::install("GenomicRanges")
```

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url> genolab
cd genolab
```

2. Make the main CLI executable:

```bash
chmod +x bin/genolab
```

3. Add `bin/` to your `PATH` (e.g. in `~/.bashrc`):

```bash
export PATH="$HOME/Desktop/genolab/bin:$PATH"
```

Reload your shell:

```bash
source ~/.bashrc
```

Now you can call `genolab` directly from anywhere:

```bash
genolab -h
```

---

## Commands

### `blastReport`
- Clean BLAST outfmt 6, infer strand and add normalized coordinates (because BLAST output has end - start <0)

**Input contract**
- BLAST outfmt 6 (extended), with `sseqid` in column 2.

**Output**
- Headered tab-separated file with columns:
  ```text
  qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore strand sstart_norm send_norm
  ```

**Example**
```bash
genolab blastReport -i input/testBLASTout.txt -o output/blastReport.txt
```

---

### `dicti`
- rename `sseqid` using a 2‑column dictionary table (check input example "old_name new_name")

**Input**
- `-i` BLAST report from `blastReport` (tab‑separated, header present).
- `-d` dictionary table (2 columns: original `sseqid`, new name).

**Output**
- Headerless tab-separated file with `sseqid` renamed.

**Example**
```bash
genolab dicti -i output/blastReport.txt -d input/dicHSA.txt -o output/d_blast.txt
```

Typical stats printed:

- Number of rows renamed.
- Number of unmatched subjects.
- List of new unique `sseqid` names.

---

### `blastBed`
- Convert processed BLAST output into BED

**Input contract**
- blastReport output:
	- Headerless tab-separated file.
	- At least 15 columns.
	- Column 2  = chromosome / renamed `sseqid`.
	- Column 13 = strand.
	- Column 14 = normalized start.
	- Column 15 = normalized end.

**Configuration**
- BED styling is controlled via `config/bed.conf`:
```bash
BED_NAME="HSat1B"
BED_SCORE="900"
BED_RGB="4,32,105"
BED_FORMAT="BED9"
BED_ZERO_BASED="true"
```

**Output format**
  ```text
  chr start end name score strand thickStart thickEnd itemRgb
  ```

**Example**
```bash
genolab blastBed -i output/d_blast.txt -o output/test.bed
```

genolab is distributed under the European Union Public Licence v. 1.2 (EUPL).
