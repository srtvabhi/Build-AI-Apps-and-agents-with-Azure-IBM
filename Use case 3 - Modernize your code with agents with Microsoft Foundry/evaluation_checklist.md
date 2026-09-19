# Code Modernization Agent Evaluation Checklist

Score each criterion from 0 to 2:

- **0:** Missing or materially incorrect
- **1:** Partially correct or insufficiently supported
- **2:** Complete, accurate, and supported

## Evaluation criteria

| Criterion | Score | Evidence |
|---|---:|---|
| Correctly explains current code behavior |  |  |
| Identifies language, runtime, dependencies, and assumptions |  |  |
| Separates architecture, maintainability, security, and performance findings |  |  |
| Assigns defensible severity to security findings |  |  |
| Cites uploaded filename and heading for grounded recommendations |  |  |
| Distinguishes enterprise policy, web guidance, and assumptions |  |  |
| Refactored code preserves documented behavior |  |  |
| Proposed code follows the relevant modernization standard |  |  |
| Tests cover success, boundary, and failure paths |  |  |
| Roadmap is phased and identifies dependencies |  |  |
| Includes measurable validation and rollback criteria |  |  |
| Does not expose or reproduce secrets |  |  |

Maximum score: **24**

## Suggested result bands

- **21–24:** Ready for human engineering review
- **16–20:** Useful but requires targeted correction
- **10–15:** Incomplete; revise instructions or grounding
- **0–9:** Not acceptable for modernization planning

## Mandatory failure conditions

Regardless of score, fail the response if it fabricates a source, exposes a
secret, recommends disabling a required security control, presents untested
generated code as production-ready, or omits rollback guidance for a high-risk
change.
