When performing a code review on this repository, before writing
your review:

1. Find the GitHub Actions workflow run for this pull request's head
   commit (repository `inghvar/query_check`), triggered by the
   "Query Doctor" workflow.
2. In that workflow run, find the artifact named `query-doctor-log`
   and download it.
3. Unzip it and read `query_doctor.log` inside — it is the raw,
   unedited output of `django-query-doctor` for this exact commit.
   This file is NOT committed to the repository; it only exists as
   a workflow artifact, so you must fetch it using your available
   GitHub tools.
4. Each `[WARNING]`/`[CRITICAL]` line in that log is a required,
   distinct finding. Leave one review comment per such line, at the
   file/line it names, even if several lines share the same root
   cause. Do not merge, paraphrase away, or skip any of them.
