When performing a code review, apply the checks in the
`.github/query-doctor-findings.md` file: it lists exact DB-query
findings from `django-query-doctor` for this PR's head commit. Treat
every numbered finding in that file as a required, distinct review
comment on its given file/line — leave one review comment per
numbered finding, even if several findings share the same root cause.
Do not merge or skip any of them.
