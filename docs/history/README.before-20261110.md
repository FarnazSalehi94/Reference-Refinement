# Reference-Refinement


> **Historical documentation—not current results.** This is the pre-reorganization README, with only its unsupported MIT badge/license claim removed for publication review. Methods and metrics below are historical and have not been validated for the current assembly runs. The exact original remains in Git at `bfce107:README.md`. The repository license is undecided.

A comprehensive pipeline for generating high-quality de novo genome assemblies using long-read sequencing technologies. This workflow integrates PacBio HiFi, Oxford Nanopore (ONT), and Hi-C data to produce chromosome-level assemblies with thorough quality assessment and error correction.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Input Data](#input-data)
- [Pipeline](#pipeline)
  - [1. Basecalling](#1-basecalling)
  - [2. Read Preparation](#2-read-preparation)
  - [3. De Novo Assembly](#3-de-novo-assembly)
  - [4. Assembly Statistics](#4-assembly-statistics)
  - [5. Quality Assessment and Correction](#5-quality-assessment-and-correction)
- [Output Files](#output-files)
- [Results](#results)
- [Troubleshooting](#troubleshooting)
- [Citations](#citations)
- [License](#license)

## Overview

This pipeline performs de novo genome assembly using a hybrid approach that leverages the strengths of multiple sequencing technologies:

| Technology | Purpose | Advantage |
|------------|---------|-----------|
| PacBio HiFi | Primary assembly | High accuracy (~99.9%) |
| Oxford Nanopore | Gap filling, scaffolding | Ultra-long reads (>100kb) |
| Hi-C | Chromosome scaffolding | Long-range contact information |

The workflow produces two parallel assemblies using **Hifiasm** and **Verkko**, enabling comparison and selection of the best result.

## Requirements

### Hardware

- CPU: 32+ cores recommended
- RAM: 128GB+ for mammalian genomes
- Storage: ~2TB free space for intermediate files

### Software

| Tool | Version | Purpose |
|------|---------|---------|
| [Dorado](https://github.com/nanoporetech/dorado) | ≥0.5.0 | ONT basecalling |
| [Hifiasm](https://github.com/chhylp123/hifiasm) | ≥0.19.0 | Genome assembly |
| [Verkko](https://github.com/marbl/verkko) | ≥2.3 | Genome assembly |
| [gfastats](https://github.com/vgl-hub/gfastats) | ≥1.3.0 | Assembly statistics |
| [NucFlag](https://github.com/lbcb-sci/NucFlag) | ≥1.0.0 | Misassembly detection |
| [Inspector](https://github.com/Maggi-Chen/Inspector) | ≥1.3.0 | Error correction |
| [minimap2](https://github.com/lh3/minimap2) | ≥2.26 | Read alignment |
| [samtools](https://github.com/samtools/samtools) | ≥1.17 | BAM processing |

## Installation

### Option 1: Conda environments (recommended)

```bash
# Hifiasm
conda create -n hifiasm -c bioconda hifiasm -y

# Verkko
mamba create -n verkko -c conda-forge -c bioconda verkko=2.3 python=3.10 setuptools -y

# NucFlag
conda create -n nucflag -c bioconda nucflag -y

# gfastats
conda create -n gfastats -c bioconda gfastats -y

# Inspector (from source due to dependency conflicts)
conda create -n inspector -c conda-forge -c bioconda python=3.9 minimap2 samtools openssl -y
conda activate inspector
pip install pysam statsmodels numpy scipy
git clone https://github.com/Maggi-Chen/Inspector.git ~/Inspector
chmod +x ~/Inspector/inspector.py ~/Inspector/inspector-correct.py
```

### Option 2: Docker

```bash
# Coming soon
```

## Input Data

| Data Type | Format | Example |
|-----------|--------|---------|
| ONT raw | POD5 | `*.pod5` |
| ONT basecalled | BAM/FASTQ | `reads.fastq` |
| PacBio HiFi | FASTQ | `hifi_reads.fastq` |
| Hi-C | Paired FASTQ | `hic_R1.fastq.gz`, `hic_R2.fastq.gz` |

## Pipeline

### 1. Basecalling

Convert raw ONT signal data to sequences using Dorado with the SUP (super accuracy) model.

```bash
dorado basecaller sup pod5_folder/ > basecalled.bam
```

**Parameters:**
- `sup`: Super accuracy model for highest quality basecalls
- Add `--modified-bases 5mCG_5hmCG` for methylation calling

### 2. Read Preparation

Convert basecalled BAM to FASTQ format.

```bash
samtools fastq basecalled.bam > ont_reads.fastq
```

For multiple BAM files:

```bash
samtools cat *.bam | samtools fastq > ont_reads.fastq
```

### 3. De Novo Assembly

#### 3.1 Hifiasm

Hifiasm produces haplotype-resolved assemblies using HiFi reads with ONT and Hi-C integration.

```bash
hifiasm -o hifiasm_output \
        -t 32 \
        --ul ont_reads.fastq \
        --h1 hic_R1.fastq.gz \
        --h2 hic_R2.fastq.gz \
        hifi_reads.fastq
```

Convert GFA to FASTA:

```bash
awk '/^S/{print ">"$2; print $3}' hifiasm_output.hic.p_ctg.gfa > hifiasm_assembly.fasta
```

**Output files:**
| File | Description |
|------|-------------|
| `*.hic.p_ctg.gfa` | Primary contigs |
| `*.hic.hap1.p_ctg.gfa` | Haplotype 1 |
| `*.hic.hap2.p_ctg.gfa` | Haplotype 2 |

#### 3.2 Verkko

Verkko creates high-quality assemblies optimized for telomere-to-telomere completeness.

```bash
verkko -d verkko_output \
       --hifi hifi_reads.fastq \
       --nano ont_reads.fastq \
       --hic1 hic_R1.fastq.gz \
       --hic2 hic_R2.fastq.gz \
       --threads 32
```

Copy assembly:

```bash
cp verkko_output/assembly.fasta verkko_assembly.fasta
```

### 4. Assembly Statistics

Generate assembly metrics using gfastats.

```bash
# Hifiasm
gfastats hifiasm_assembly.fasta -t > hifiasm_stats.txt

# Verkko
gfastats verkko_assembly.fasta -t > verkko_stats.txt
```

### 5. Quality Assessment and Correction

#### 5.1 NucFlag: Misassembly Detection

NucFlag identifies structural errors by analyzing read alignments.

**HiFi-based detection:**

```bash
minimap2 -ax map-hifi assembly.fasta hifi_reads.fastq -t 32 | \
    samtools sort -o hifi_aligned.bam -@ 32
samtools index hifi_aligned.bam
nucflag -i hifi_aligned.bam -o nucflag_hifi -t 32
```

**ONT-based detection:**

```bash
minimap2 -ax map-ont assembly.fasta ont_reads.fastq -t 32 | \
    samtools sort -o ont_aligned.bam -@ 32
samtools index ont_aligned.bam
nucflag -i ont_aligned.bam -o nucflag_ont -t 32
```

#### 5.2 Inspector: Error Detection and Correction

Inspector identifies and corrects base-level and structural errors.

**HiFi-based correction:**

```bash
# Detection
python ~/Inspector/inspector.py \
    -c assembly.fasta \
    -r hifi_reads.fastq \
    -o inspector_hifi \
    --datatype hifi \
    -t 32

# Correction
python ~/Inspector/inspector-correct.py \
    -i inspector_hifi \
    --datatype pacbio-hifi \
    -o assembly_corrected_hifi.fasta \
    -t 32
```

**ONT-based correction:**

```bash
# Detection
python ~/Inspector/inspector.py \
    -c assembly.fasta \
    -r ont_reads.fastq \
    -o inspector_ont \
    --datatype nanopore \
    -t 32

# Correction
python ~/Inspector/inspector-correct.py \
    -i inspector_ont \
    --datatype nano-raw \
    -o assembly_corrected_ont.fasta \
    -t 32
```

## Output Files

```
project/
├── hifiasm_assembly.fasta          # Hifiasm primary assembly
├── hifiasm_hap1.fasta              # Hifiasm haplotype 1
├── hifiasm_hap2.fasta              # Hifiasm haplotype 2
├── verkko_assembly.fasta           # Verkko assembly
├── hifiasm_stats.txt               # Hifiasm statistics
├── verkko_stats.txt                # Verkko statistics
├── nucflag_hifi/                   # NucFlag HiFi results
├── nucflag_ont/                    # NucFlag ONT results
├── inspector_hifi/                 # Inspector HiFi results
│   └── summary_statistics          # QV and error rates
├── inspector_ont/                  # Inspector ONT results
├── hifiasm_corrected_hifi.fasta    # Corrected assembly (HiFi)
└── hifiasm_corrected_ont.fasta     # Corrected assembly (ONT)
```

## Results

### Assembly Metrics

| Metric | Hifiasm | Verkko |
|--------|---------|--------|
| Total length | 2.82 Gb | TBD |
| Number of contigs | 88 | TBD |
| N50 | 129.7 Mb | TBD |
| Longest contig | 435.2 Mb | TBD |
| QV (quality value) | 54.57 | TBD |

### Quality Interpretation

| QV Score | Accuracy | Error Rate |
|----------|----------|------------|
| 40 | 99.99% | 1 in 10,000 |
| 50 | 99.999% | 1 in 100,000 |
| 60 | 99.9999% | 1 in 1,000,000 |

## Troubleshooting

### Common Issues

**Verkko: `pkg_resources` error**
```bash
conda activate verkko
pip install setuptools
```

**Inspector: Missing modules**
```bash
pip install statsmodels pysam numpy scipy
```

**Samtools: `libcrypto` error**
```bash
conda install -c conda-forge openssl
```

## Citations

If you use this pipeline, please cite the following tools:

- **Hifiasm**: Cheng, H., et al. (2021). Haplotype-resolved de novo assembly using phased assembly graphs with hifiasm. *Nature Methods*, 18(2), 170-175.

- **Verkko**: Rautiainen, M., et al. (2023). Telomere-to-telomere assembly of diploid chromosomes with Verkko. *Nature Biotechnology*, 41(10), 1474-1482.

- **Inspector**: Chen, Y., et al. (2021). Efficient assembly of nanopore reads via highly accurate and intact error correction. *Nature Communications*, 12(1), 60.

- **Dorado**: Oxford Nanopore Technologies. https://github.com/nanoporetech/dorado

## License

License undecided. No LICENSE file accompanied the recovered repository. No MIT license is asserted by this archived document.

## Contact

For questions or issues, please open a GitHub issue or contact [your.email@example.com].
