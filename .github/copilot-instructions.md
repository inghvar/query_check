When performing a code review on this repository, before writing
your review, read the file `query_doctor.log` at the repository
root. It is committed directly to the repository (not generated at
review time), and contains the raw output of `django-query-doctor`
for this branch.

Each `[WARNING]`/`[CRITICAL]` line in it is a required, distinct
finding. Leave one review comment per such line, at the file/line it
names, describing the problem and the suggested fix. Do not merge,
paraphrase away, or skip any of them.

If `query_doctor.log` is missing or empty when you check, state that
explicitly in your review summary instead of silently skipping this
step.
