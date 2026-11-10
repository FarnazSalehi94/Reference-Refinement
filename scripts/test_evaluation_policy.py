#!/usr/bin/env python3
"""Documentation generation tests using only tiny curated files and mocked accounting."""
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from repository_guard import ROOT
from sync_project import approved_remote, prepare


class EvaluationPolicyTests(unittest.TestCase):
    def test_exact_repository_remote_allowlist(self):
        self.assertTrue(approved_remote('git@github.com:FarnazSalehi94/Reference-Refinement.git'))
        self.assertTrue(approved_remote('https://github.com/FarnazSalehi94/Reference-Refinement.git'))
        self.assertFalse(approved_remote('git@github.com:someone-else/Reference-Refinement.git'))
        self.assertFalse(approved_remote('https://example.org/Reference-Refinement.git'))

    def test_latest_completed_bn_execution_has_preliminary_interpretation(self):
        manifest = list(csv.DictReader(io.StringIO((ROOT/'metadata/import_manifest.tsv').read_text()), delimiter='\t'))
        config = json.loads((ROOT/'configs/import_allowlist.json').read_text())
        states = json.loads((ROOT/'metadata/slurm_status.json').read_text())
        with tempfile.TemporaryDirectory(prefix='bn_docs_policy_') as tmp:
            source = Path(tmp)
            for row in manifest:
                path = source/row['source_relative']
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes((ROOT/row['repository_path']).read_bytes())
            # Fixture completion markers; no real analysis is run.
            for entry in config['verified_figures']:
                if 'log' in entry:
                    path = source/entry['log']
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text('Done!\n')
            with patch('sync_project.accounting', return_value=states):
                result = prepare(source)
                self.assertEqual(result, prepare(source))
        readme = result['README.md'].decode()
        headline = readme.split('<!-- BEGIN VERIFIED_METRICS -->')[1].split('<!-- END VERIFIED_METRICS -->')[0]
        self.assertIn('QV (preliminary interpretation)', headline)
        self.assertIn('completeness (%) (preliminary interpretation)', headline)
        self.assertIn('64.2134', headline)
        self.assertIn('99.7451', headline)
        self.assertIn('latest completed BN evaluations', readme)
        self.assertNotIn('historical/preliminary', readme)
        status = result['PROJECT_STATUS.md'].decode()
        self.assertIn('COMPLETED on 2026-11-09', status)
        self.assertIn('Further quality validation', status)
        self.assertIn('Planned; not confirmed running', status)
        self.assertIn('Older legacy analyses', status)
        self.assertIn('Latest completed BN evaluation; scientific interpretation preliminary', result['figures/README.md'].decode())
        self.assertIn('latest completed Brown Norway evaluation', result['results/assembly/COMPARISON.md'].decode())
        self.assertEqual(result['results/merqury/merqury_summary.tsv'], (ROOT/'results/merqury/merqury_summary.tsv').read_bytes())
        self.assertEqual(result['results/assembly/comparison.tsv'], (ROOT/'results/assembly/comparison.tsv').read_bytes())


if __name__ == '__main__':
    unittest.main()
