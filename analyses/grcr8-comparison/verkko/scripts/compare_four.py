#!/usr/bin/env python3
import bisect,collections,csv,os,re,sys
from pathlib import Path
root=Path(sys.argv[1]); refs={}; names={}
with open(root/'GRCr8.fai') as f:
 for line in f:
  a=line.rstrip().split('\t'); refs[a[0]]=int(a[1])
for i in range(19,41): names[f'NC_0860{i}.1']=str(i-18) if i<=38 else ('X' if i==39 else 'Y')
chroms=[c for c in names if c in refs]
if 'NC_086019.1' not in refs or refs['NC_086019.1']!=270518180: raise RuntimeError('Reference chr1 accession or length does not match GRCr8 RefSeq')
def merge(v):
 out=[]
 for s,e in sorted(v):
  if out and s<=out[-1][1]:out[-1]=(out[-1][0],max(e,out[-1][1]))
  else:out.append((s,e))
 return out
def length(v):return sum(e-s for s,e in v)
def subtract(a,b):
 out=[];j=0
 for s,e in a:
  while j<len(b) and b[j][1]<=s:j+=1
  x=s;k=j
  while k<len(b) and b[k][0]<e:
   u,v=b[k]
   if u>x:out.append((x,min(u,e)))
   x=max(x,v)
   if x>=e:break
   k+=1
  if x<e:out.append((x,e))
 return out
def dupl(v):
 # Count overlap among distinct query contigs; merge each contig's alignments first.
 by=collections.defaultdict(list)
 for s,e,q in v:by[q].append((s,e))
 events=[]
 for parts in by.values():
  for s,e in merge(parts):events.extend([(s,1),(e,-1)])
 events.sort();last=0;depth=0;result=[]
 for pos,delta in events:
  if depth>=2 and pos>last:result.append((last,pos))
  depth+=delta;last=pos
 return merge(result)
allint={};hi={};dup={};qsum={};sect={}; query_stats={}
for sample in ('primary','hap1','hap2','verkko'):
 vals=collections.defaultdict(list); high=collections.defaultdict(list); dups=collections.defaultdict(list); q=collections.Counter(); sec=collections.defaultdict(list); query_all=collections.defaultdict(list); query_hi=collections.defaultdict(list)
 with open(root/'alignments'/f'{sample}.paf') as f:
  for line in f:
   a=line.rstrip().split('\t');
   if len(a)<12:continue
   query,ctg=a[0],a[5]
   s,e=int(a[7]),int(a[8]); mapq=int(a[11]); tags={x[:2]:x[5:] for x in a[12:] if len(x)>5 and x[2:5] in (':A:',':i:',':f:',':Z:')}; primary=tags.get('tp')=='P'
   if primary:
    query_all[query].append((int(a[2]),int(a[3])))
    if mapq>=20:query_hi[query].append((int(a[2]),int(a[3])))
   if ctg not in names:continue
   if primary:
    vals[ctg].append((s,e));q[ctg]+=int(a[3])-int(a[2])
    if mapq>=20:high[ctg].append((s,e));dups[ctg].append((s,e,query))
   else:sec[ctg].append((s,e))
 query_stats[sample]=(sum(length(merge(v)) for v in query_all.values()),sum(length(merge(v)) for v in query_hi.values()))
 allint[sample]={c:merge(vals[c]) for c in chroms};hi[sample]={c:merge(high[c]) for c in chroms};dup[sample]={c:dupl(dups[c]) for c in chroms};sect[sample]={c:merge(sec[c]) for c in chroms};qsum[sample]=q
out=root/'results';out.mkdir(exist_ok=True)
with (out/'assembly_query_alignment_summary.tsv').open('w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['assembly','contigs','total_bases','query_bases_covered_by_primary_alignment','query_bases_covered_by_MAPQ20_primary','query_bases_without_MAPQ20_primary'])
 for sample in ('primary','hap1','hap2','verkko'):
  with open(root/'fasta'/f'{sample}.fai') as idx: lens=[int(line.split('\t')[1]) for line in idx]
  allq,hiq=query_stats[sample];w.writerow([sample,len(lens),sum(lens),allq,hiq,sum(lens)-hiq])
with (out/'chromosome_comparison.tsv').open('w') as f:
 cols=['chromosome','ref_accession','ref_length']
 for x in ('primary','hap1','hap2','verkko'):cols += [x+'_primary_ref_covered_bp',x+'_primary_ref_coverage_pct',x+'_mapq20_ref_covered_bp',x+'_mapq20_ref_coverage_pct',x+'_primary_query_aligned_bp_sum',x+'_mapq20_distinct_contig_overlap_bp',x+'_secondary_ref_covered_bp']
 cols+=['hap2_minus_hap1_mapq20_ref_covered_bp','hap2_minus_hap1_primary_query_aligned_bp_sum'];w=csv.writer(f,delimiter='\t');w.writerow(cols)
 for c in chroms:
  row=[names[c],c,refs[c]]
  for x in ('primary','hap1','hap2','verkko'):
   a=length(allint[x][c]);b=length(hi[x][c]);row += [a,round(100*a/refs[c],4),b,round(100*b/refs[c],4),qsum[x][c],length(dup[x][c]),length(sect[x][c])]
  row += [length(hi['hap2'][c])-length(hi['hap1'][c]),qsum['hap2'][c]-qsum['hap1'][c]];w.writerow(row)
with (out/'large_unaligned_regions.bed').open('w') as f:
 f.write('# 0-based half-open; sample reference start end length confidence\n')
 for x in ('primary','hap1','hap2','verkko'):
  for c in chroms:
   for s,e in subtract([(0,refs[c])],hi[x][c]):
    if e-s>=100000:f.write(f'{c}\t{s}\t{e}\t{x}\t{e-s}\tno_MAPQ20_primary\n')
with (out/'haplotype_coverage_differences.bed').open('w') as f:
 f.write('# 0-based half-open; reference start end covered_by length\n')
 for c in chroms:
  for x,y in [('hap1','hap2'),('hap2','hap1')]:
   for s,e in subtract(hi[x][c],hi[y][c]):
    if e-s>=100000:f.write(f'{c}\t{s}\t{e}\t{x}_only\t{e-s}\n')
with (out/'potential_duplicated_reference_regions.bed').open('w') as f:
 f.write('# 0-based half-open; overlap of >=2 distinct contigs, MAPQ >=20; candidate only\n')
 for x in ('primary','hap1','hap2','verkko'):
  for c in chroms:
   for s,e in dup[x][c]:
    if e-s>=10000:f.write(f'{c}\t{s}\t{e}\t{x}\t{e-s}\n')
# Self-contained SVG, chromosome bars show covered reference, not copy number.
W=1250;H=140+len(chroms)*45;colors={'primary':'#4977af','hap1':'#d78b33','hap2':'#3b9b7a','verkko':'#894fa0'}
with (out/'chromosome_reference_coverage.svg').open('w') as f:
 f.write(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><rect width="100%" height="100%" fill="white"/><g font-family="sans-serif" font-size="12"><text x="20" y="25" font-size="18">GRCr8 chromosome coverage (primary alignments, MAPQ ≥20)</text>')
 for idx,x in enumerate(('primary','hap1','hap2','verkko')):f.write(f'<rect x="{430+idx*160}" y="10" width="12" height="12" fill="{colors[x]}"/><text x="{447+idx*160}" y="21">{x}</text>')
 for i,c in enumerate(chroms):
  y=60+i*45;f.write(f'<text x="20" y="{y+15}">chr{names[c]}</text>')
  for j,x in enumerate(('primary','hap1','hap2','verkko')):
   a=length(hi[x][c])/refs[c];f.write(f'<rect x="80" y="{y+j*8}" width="{a*1000:.2f}" height="7" fill="{colors[x]}"/>')
 f.write('</g></svg>')
with (out/'interpretation.md').open('w') as f:
 f.write('''# Interpretation and definitions\n\nGRCr8 RefSeq chromosome accessions NC_086019.1–NC_086040.1 are included; nonchromosomal and mitochondrial sequences are retained during alignment but excluded from the chromosome table. Coordinates in BED files are 0-based, half-open. Coverage is the union of target spans of minimap2 primary PAF alignments; MAPQ >=20 is a conservative view, and all-primary coverage provides context. Target spans include indels and are not exact matched-base counts. Query aligned-base sums are not deduplicated and may exceed chromosome lengths. Potential duplicated regions are reference spans covered by two distinct assembly contigs with primary MAPQ >=20; they are candidates, not confirmed duplications. Secondary alignment coverage is a repeat/ambiguity indicator, limited by minimap2 reporting.\n\nLarge unaligned regions are >=100 kb without primary MAPQ >=20 alignment; these can reflect repeats, low mapping confidence, reference gaps, structural variation, divergence, or missing sequence. Haplotype-only regions >=100 kb indicate differential unique coverage, not proven deletions. The assembly size difference can include unaligned sequence, duplications and sequence divergence; chromosome coverage differences alone do not necessarily sum to the total length difference. Examine alignments and repeat/reference gap annotation before biological conclusions.\n''')
