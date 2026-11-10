#!/usr/bin/env python3
import csv,sys
from pathlib import Path
p=Path(sys.argv[1])
with (p/'merqury_summary.tsv').open('w') as out:
 w=csv.writer(out,delimiter='\t');w.writerow(['assembly','assembly_only_kmers','total_assembly_kmers','QV','error_rate','solid_read_kmers_in_assembly','solid_read_kmers_total','completeness_percent'])
 for sample in ('hifiasm','verkko','grcr8'):
  q=(p/sample/(sample+'.qv')).read_text().strip().splitlines()[0].split()
  c=(p/sample/(sample+'.completeness.stats')).read_text().strip().splitlines()[0].split()
  w.writerow([sample]+q[1:5]+c[2:5])
