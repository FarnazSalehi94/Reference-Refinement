#!/usr/bin/env python3
import csv,sys
from pathlib import Path

def get_stats(path):
    records=[]; contigs=[]; gaps=0; gap_bases=0; rec_len=0; contig_len=0; in_gap=False; seen_header=False
    def flush_contig():
        nonlocal contig_len
        if contig_len: contigs.append(contig_len)
        contig_len=0
    def flush_record():
        nonlocal rec_len
        if seen_header:
            records.append(rec_len)
        rec_len=0
    with open(path,'rb',buffering=8*1024*1024) as f:
        for line in f:
            if line.startswith(b'>'):
                if seen_header:
                    if in_gap:in_gap=False
                    flush_contig();flush_record()
                seen_header=True
                continue
            seq=line.strip()
            if not seq:continue
            if not seen_header:raise ValueError(f'{path}: sequence before first FASTA header')
            rec_len+=len(seq)
            i=0
            while i<len(seq):
                if seq[i] in (78,110):
                    j=i+1
                    while j<len(seq) and seq[j] in (78,110):j+=1
                    if not in_gap:gaps+=1
                    run=j-i;gap_bases+=run
                    flush_contig();in_gap=True;i=j
                else:
                    j=i+1
                    while j<len(seq) and seq[j] not in (78,110):j+=1
                    contig_len+=j-i;in_gap=False;i=j
        if seen_header:
            flush_contig();flush_record()
    def n50(vals):
        if not vals:return 0
        total=sum(vals); c=0
        for n in sorted(vals,reverse=True):
            c+=n
            if c*2>=total:return n
        return 0
    return {'path':str(path),'fasta_records_scaffolds':len(records),'total_sequence_bp':sum(records),'scaffold_N50_bp':n50(records),'contigs_split_at_N_runs':len(contigs),'contig_N50_bp':n50(contigs),'N_run_gap_count':gaps,'total_N_gap_bases':gap_bases}

paths=[Path(p) for p in sys.argv[1:]]
out=Path(__file__).resolve().parent/'results'/'gap_stats.tsv'
rows=[]
for p in paths:
 print(f'Scanning {p}',flush=True)
 rows.append(get_stats(p))
with out.open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),delimiter='\t');w.writeheader();w.writerows(rows)
print(out)
for r in rows:print(r)
