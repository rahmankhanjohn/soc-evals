# soc-evals

Score a managed SOC proposal against the five questions that decide whether it works.

Most SOC-as-a-Service comparisons are a feature checklist. This is a decision tool. Five questions, and a verdict you can act on.

1. **Telemetry coverage** — what percentage of the estate is instrumented on day one
2. **Escalation SLA** — minutes for the worst severity, to a human acknowledging, not to a ticket existing
3. **Data location** — where your data sits while they triage it
4. **Response authority** — what they are allowed to do inside your environment
5. **Tuning ownership** — who tunes detection, and how often

## Requirements

Python 3.9+, no dependencies.

## Usage

```
python3 soc_evals.py --coverage 85 --sla 15 --data in-country --authority full --tuning shared --cadence quarterly
python3 soc_evals.py            # interactive, press Enter for defaults
python3 soc_evals.py --report   # one paste-ready line
```

```
SOCaaS evaluation
==================================================================
  OK   coverage   enough telemetry to work with
  OK   sla        fast enough for a live incident
  OK   data       data stays where your policy expects it
  OK   authority  they can contain, not just report
  WARN tuning     ask what happens to your tuning requests
  WARN cadence    enough for a stable estate

  Verdict: NEEDS WORK
  close the gaps in writing before go-live

  Start here: Who tunes detection (tuning)
```

Exit code 0 only when the verdict is READY.

## How the scoring works

| Question | Fails when | Warns when |
|----------|------------|------------|
| coverage | under 50% of the estate instrumented | under 80% |
| sla | over 60 minutes to a human acknowledging | over 15 minutes |
| data | unknown, or not confirmed | offshore when your policy may not allow it |
| authority | nobody can act inside your environment | limited authority |
| tuning | nobody owns it | vendor only, with no commitment on your requests |
| cadence | never, or on request | quarterly |

The two that fail most often in practice are coverage and authority. No telemetry means the provider has nothing to work with, and no authority means their detection produces reports nobody can act on at 3 AM.

## Tests

```
python3 -m unittest test_soc_evals -v
```

## Where this comes from

Written while preparing *SOCaaS: Three Use Cases That Justify It, Two That Never Will*.

## License

MIT
