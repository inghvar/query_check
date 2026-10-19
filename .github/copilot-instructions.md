When performing a code review, apply the checks in the
`.github/query-doctor-findings.log` file: it is the raw, unedited
output of `django-query-doctor` for this PR's head commit. Each
`[WARNING]`/`[CRITICAL]` line is a required, distinct finding —
leave one review comment per such line, at the file/line it names,
even if several lines share the same root cause. Do not merge,
paraphrase away, or skip any of them.
