When performing a code review on this repository, before writing
your review, read the file `query_doctor.log` at the repository
root of your current working directory.

This file is placed there automatically by the
`.github/workflows/copilot-code-review.yml` setup steps, which run
before you start reviewing: they look up the most recent completed
"Query Doctor" GitHub Actions run for this exact commit, download its
`query-doctor-log` artifact, and unzip it into the workspace. It is
NOT committed to the repository, so you will only find it on disk,
not in git history.

`query_doctor.log` is the raw, unedited output of `django-query-doctor`
for this exact commit. Each `[WARNING]`/`[CRITICAL]` line in it is a
required, distinct finding. Leave one review comment per such line,
at the file/line it names, even if several lines share the same root
cause. Do not merge, paraphrase away, or skip any of them.

If `query_doctor.log` is missing or empty when you check, state that
explicitly in your review summary instead of silently skipping this
step.
