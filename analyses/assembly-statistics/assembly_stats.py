#!/usr/bin/env python3
import sys
lengths=[]
length=None
with open(sys.argv[1]) as f:
    for line in f:
        if line.startswith('>'):
            if length is not None: lengths.append(length)
            length=0
        elif length is None: raise ValueError('sequence before FASTA header')
        else: length += len(line.strip())
if length is not None: lengths.append(length)
if not lengths: raise ValueError('empty FASTA')
total=sum(lengths); cumulative=0
for n in sorted(lengths, reverse=True):
    cumulative+=n
    if cumulative*2>=total: break
print(f'contigs\t{len(lengths)}\ntotal_bases\t{total}\ncontig_N50\t{n}')
