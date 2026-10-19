#!/usr/bin/env python3
"""soc-evals: score a managed SOC proposal against the five questions that matter.

  1. telemetry coverage    percent of the estate instrumented on day one
  2. escalation SLA        minutes for the worst severity, to a human acknowledging
  3. data location         where your data sits while they triage it
  4. response authority    what they can do inside your environment
  5. tuning ownership      who tunes detection, and how often

Run it with no arguments for the interactive version.

Usage:
  soc-evals.py --coverage 85 --sla 15 --data in-country --authority full --tuning shared --cadence quarterly
"""

import argparse
import sys
import time

QUESTIONS = [
    ('coverage', 'Telemetry in scope, percent of the estate instrumented', 85),
    ('sla', 'Escalation SLA for the worst severity, minutes to a human acknowledging', 15),
    ('data', 'Where your data sits while they triage it (in-country, offshore, unknown)', 'in-country'),
    ('authority', 'What they can do inside your environment (none, limited, full)', 'full'),
    ('tuning', 'Who tunes detection (vendor, customer, shared)', 'shared'),
    ('cadence', 'How often detection is tuned (monthly, quarterly, never)', 'quarterly'),
]

GOOD, WARN, BAD = 'GOOD', 'WARN', 'BAD'


def score_coverage(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return BAD, 'coverage must be a number'
    if number >= 80:
        return GOOD, 'enough telemetry to work with'
    if number >= 50:
        return WARN, 'half the estate is dark on day one'
    return BAD, 'no telemetry means no detection, whatever is sold'


def score_sla(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return BAD, 'sla must be a number'
    if number <= 15:
        return GOOD, 'fast enough for a live incident'
    if number <= 60:
        return WARN, 'an hour is an hour of exposure'
    return BAD, 'too slow for anything that is still running'


def score_data(value):
    text = str(value).lower()
    if text in ('unknown', 'no', 'not-sure', ''):
        return BAD, 'ask where the data sits and get it in writing'
    if text in ('in-country', 'local', 'on-prem', 'on-premises'):
        return GOOD, 'data stays where your policy expects it'
    if text == 'offshore':
        return WARN, 'fine only if your policy allows it'
    return WARN, 'confirm the location in writing'


def score_authority(value):
    text = str(value).lower()
    if text == 'full':
        return GOOD, 'they can contain, not just report'
    if text == 'limited':
        return WARN, 'reports arrive faster than actions can be taken'
    if text == 'none':
        return BAD, 'detection without authority is a reporting service'
    return BAD, 'be specific about what they may do'


def score_tuning(value):
    text = str(value).lower()
    if text in ('shared', 'customer'):
        return GOOD, 'detection quality improves after month one'
    if text == 'vendor':
        return WARN, 'ask what happens to your tuning requests'
    return BAD, 'nobody owns detection quality'


def score_cadence(value):
    text = str(value).lower()
    if text in ('monthly', 'weekly', 'continuous'):
        return GOOD, 'detection keeps up with your estate'
    if text == 'quarterly':
        return WARN, 'enough for a stable estate'
    if text in ('never', 'on-request'):
        return BAD, 'detection decays without review'
    return WARN, 'agree a review cadence in the contract'


SCORERS = {
    'coverage': score_coverage,
    'sla': score_sla,
    'data': score_data,
    'authority': score_authority,
    'tuning': score_tuning,
    'cadence': score_cadence,
}


def evaluate(answers):
    results = []
    for key, label, _default in QUESTIONS:
        grade, note = SCORERS[key](answers.get(key))
        results.append({'key': key, 'label': label, 'grade': grade, 'note': note})
    return results


def verdict(results):
    grades = [r['grade'] for r in results]
    if BAD in grades:
        return 'NOT READY', 'fix the failing answers before signing anything'
    if WARN in grades:
        return 'NEEDS WORK', 'close the gaps in writing before go-live'
    return 'READY', 'the basics are covered, keep checking the evidence'


def first_fix(results):
    for grade in (BAD, WARN):
        for result in results:
            if result['grade'] == grade:
                return result
    return None


def render(results, answers):
    lines = []
    lines.append('SOCaaS evaluation')
    lines.append('=' * 66)
    for result in results:
        mark = {GOOD: 'OK  ', WARN: 'GAP ', BAD: 'FAIL'}[result['grade']]
        lines.append('  %s %-12s %s' % (mark, result['key'], result['note']))
    lines.append('')
    verdict_text, verdict_note = verdict(results)
    lines.append('  Verdict: %s' % verdict_text)
    lines.append('  %s' % verdict_note)
    fix = first_fix(results)
    if fix:
        lines.append('')
        lines.append('  Start here: %s (%s)' % (fix['label'], fix['note']))
    return '\n'.join(lines)


def report_line(results, answers):
    verdict_text, _note = verdict(results)
    gaps = [r['key'] for r in results if r['grade'] == BAD]
    warns = [r['key'] for r in results if r['grade'] == WARN]
    parts = ['SOCaaS evaluation: %s.' % verdict_text]
    if gaps:
        parts.append('Failing: %s.' % ', '.join(gaps))
    if warns:
        parts.append('Weak: %s.' % ', '.join(warns))
    parts.append('Coverage %s percent, escalation %s minutes, data %s, authority %s, tuning %s %s.'
                 % (answers.get('coverage'), answers.get('sla'), answers.get('data'),
                    answers.get('authority'), answers.get('tuning'), answers.get('cadence')))
    parts.append('Checked %s.' % time.strftime('%Y-%m-%d'))
    parts.append('Tool: https://github.com/rahmankhanjohn/soc-evals')
    return ' '.join(parts)


def interactive():
    print('=' * 66)
    print('SOCaaS evaluation, five questions')
    print('=' * 66)
    print('Press Enter to accept the default shown in brackets.')
    print()
    answers = {}
    for key, label, default in QUESTIONS:
        raw = input('%s [%s]: ' % (label, default)).strip()
        answers[key] = raw or default
    print()
    results = evaluate(answers)
    print(render(results, answers))
    print()
    try:
        input('Press Enter to close...')
    except (EOFError, KeyboardInterrupt):
        pass


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        interactive()
        return 0
    parser = argparse.ArgumentParser(description='Score a managed SOC proposal on five questions.')
    parser.add_argument('--coverage', default='85', help='percent of the estate instrumented')
    parser.add_argument('--sla', default='15', help='escalation minutes to a human acknowledging')
    parser.add_argument('--data', default='in-country', help='in-country, offshore, unknown')
    parser.add_argument('--authority', default='full', help='none, limited, full')
    parser.add_argument('--tuning', default='shared', help='vendor, customer, shared')
    parser.add_argument('--cadence', default='quarterly', help='monthly, quarterly, never')
    parser.add_argument('--json', action='store_true', help='machine-readable output')
    parser.add_argument('--report', action='store_true', help='one paste-ready summary line')
    args = parser.parse_args(argv)

    answers = {'coverage': args.coverage, 'sla': args.sla, 'data': args.data,
               'authority': args.authority, 'tuning': args.tuning, 'cadence': args.cadence}
    results = evaluate(answers)
    verdict_text, _note = verdict(results)

    if args.json:
        import json
        print(json.dumps({'answers': answers, 'verdict': verdict_text, 'results': results}, indent=2))
    elif args.report:
        print(report_line(results, answers))
    else:
        print(render(results, answers))
    return 0 if verdict_text == 'READY' else 1


if __name__ == '__main__':
    sys.exit(main())
