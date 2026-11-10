#!/usr/bin/env python3
"""Tiny regression tests for publication exclusions (no HPC or network needed)."""
import unittest
from repository_guard import inspect


class GuardTests(unittest.TestCase):
    def test_small_document(self):
        inspect('docs/test.md', b'# Research notes\n')

    def test_reject_data(self):
        for path in ('reads.fastq', 'assembly.fasta', 'results/x.cool', 'tools/run.bin', 'secrets.key'):
            with self.assertRaises(ValueError):
                inspect(path, b'not publishable')

    def test_reject_size(self):
        with self.assertRaises(ValueError):
            inspect('results/too_big.tsv', b'x' * (5 * 1024 * 1024 + 1))

    def test_reject_secret(self):
        with self.assertRaises(ValueError):
            inspect('docs/test.md', ('gh' + 'p_' + 'a' * 36).encode())
        with self.assertRaises(ValueError):
            inspect('docs/test.md', ('-----BEGIN ' + 'PRIVATE KEY-----').encode())

    def test_reject_active_svg(self):
        with self.assertRaises(ValueError):
            inspect('figures/test.svg', b'<svg><script>bad</script></svg>')

    def test_reject_traversal(self):
        with self.assertRaises(ValueError):
            inspect('../outside.md', b'bad')


if __name__ == '__main__':
    unittest.main()
