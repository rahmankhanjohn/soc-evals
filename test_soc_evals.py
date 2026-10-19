import unittest

import soc_evals as se

GOOD = {'coverage': '90', 'sla': '10', 'data': 'in-country', 'authority': 'full',
        'tuning': 'shared', 'cadence': 'monthly'}
BAD = {'coverage': '20', 'sla': '240', 'data': 'unknown', 'authority': 'none',
       'tuning': 'never', 'cadence': 'never'}


class TestScoring(unittest.TestCase):
    def test_good_answers_are_ready(self):
        results = se.evaluate(GOOD)
        verdict, _note = se.verdict(results)
        self.assertEqual(verdict, 'READY')

    def test_bad_answers_are_not_ready(self):
        results = se.evaluate(BAD)
        verdict, _note = se.verdict(results)
        self.assertEqual(verdict, 'NOT READY')

    def test_low_coverage_is_a_failure(self):
        results = se.evaluate(dict(GOOD, coverage='30'))
        grades = {r['key']: r['grade'] for r in results}
        self.assertEqual(grades['coverage'], se.BAD)

    def test_slow_sla_is_a_failure(self):
        results = se.evaluate(dict(GOOD, sla='180'))
        grades = {r['key']: r['grade'] for r in results}
        self.assertEqual(grades['sla'], se.BAD)

    def test_offshore_data_is_a_warning(self):
        results = se.evaluate(dict(GOOD, data='offshore'))
        grades = {r['key']: r['grade'] for r in results}
        self.assertEqual(grades['data'], se.WARN)

    def test_no_authority_is_a_failure(self):
        results = se.evaluate(dict(GOOD, authority='none'))
        grades = {r['key']: r['grade'] for r in results}
        self.assertEqual(grades['authority'], se.BAD)

    def test_vendor_only_tuning_is_a_warning(self):
        results = se.evaluate(dict(GOOD, tuning='vendor'))
        grades = {r['key']: r['grade'] for r in results}
        self.assertEqual(grades['tuning'], se.WARN)

    def test_never_cadence_is_a_failure(self):
        results = se.evaluate(dict(GOOD, cadence='never'))
        grades = {r['key']: r['grade'] for r in results}
        self.assertEqual(grades['cadence'], se.BAD)

    def test_first_fix_prefers_a_failure(self):
        results = se.evaluate(dict(GOOD, coverage='10'))
        fix = se.first_fix(results)
        self.assertEqual(fix['key'], 'coverage')
        self.assertEqual(fix['grade'], se.BAD)

    def test_render_mentions_verdict(self):
        text = se.render(se.evaluate(GOOD), GOOD)
        self.assertIn('Verdict: READY', text)
        self.assertIn('coverage', text)

    def test_report_line_is_one_line(self):
        line = se.report_line(se.evaluate(GOOD), GOOD)
        self.assertNotIn('\n', line)
        self.assertIn('READY', line)
        self.assertIn('github.com/rahmankhanjohn/soc-evals', line)


if __name__ == '__main__':
    unittest.main()
