#!/usr/bin/env python3
import csv,collections,pathlib
base=pathlib.Path(__file__).resolve().parents[1]
chrom={f'NC_0860{i}.1':(str(i-18) if i<=38 else 'X' if i==39 else 'Y') for i in range(19,41)}
wanted={'4','7','9','18','19','X','Y'}
def union(v):
 out=[]
 for s,e in sorted(v):
  if out and s<=out[-1][1]:out[-1]=(out[-1][0],max(e,out[-1][1]))
  else:out.append((s,e))
 return sum(e-s for s,e in out)
groups=collections.defaultdict(lambda:{'ref':[],'query':[],'secondary':0,'n':0,'qlen':0,'max_mapq':0})
for sample in ('primary','hap1','hap2','verkko'):
 path = base/'verkko_comparison'/'alignments'/'verkko.paf' if sample=='verkko' else base/'alignments'/f'{sample}.paf'
 if not path.exists(): continue
 with open(path) as f:
  for line in f:
   a=line.rstrip().split('\t'); name=chrom.get(a[5]);
   if name not in wanted:continue
   typ=next((v[5:] for v in a[12:] if v.startswith('tp:A:')),'?');q=int(a[11]);d=groups[(sample,name,a[0])];d['qlen']=int(a[1]);d['max_mapq']=max(d['max_mapq'],q)
   if typ=='P' and q>=20:d['ref'].append((int(a[7]),int(a[8])));d['query'].append((int(a[2]),int(a[3])));d['n']+=1
   else:d['secondary']+=1
with open(base/'chromosome_investigation'/'contig_chromosome_alignments.tsv','w') as f:
 w=csv.writer(f,delimiter='\t');w.writerow(['assembly','chromosome','contig','contig_length','mapq20_primary_query_bp_union','mapq20_primary_ref_bp_union','mapq20_primary_segments','other_segments','max_mapq'])
 for (sample,chr,contig),d in sorted(groups.items()):w.writerow([sample,chr,contig,d['qlen'],union(d['query']),union(d['ref']),d['n'],d['secondary'],d['max_mapq']])
