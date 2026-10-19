When performing a code review on this repository, before writing
your review, fetch the latest `django-query-doctor` findings for
this exact commit using the GitHub MCP server's Actions tools:

1. Call `actions_list` with method `list_workflow_runs` for the
   `query-doctor.yml` workflow, filtered to the head commit SHA of
   this pull request.
2. Call `actions_list` with method `list_workflow_run_artifacts` for
   the matched run to find the artifact named `query-doctor-log`.
3. Call `actions_get` with method `download_workflow_run_artifact`
   for that artifact's ID, and read its contents (it is a zip
   containing `query_doctor.log`).

`query_doctor.log` is the raw, unedited output of `django-query-doctor`
for this exact commit. Each `[WARNING]`/`[CRITICAL]` line in it is a
required, distinct finding. Leave one review comment per such line,
at the file/line it names, even if several lines share the same root
cause. Do not merge, paraphrase away, or skip any of them.

If you cannot find a completed `query-doctor.yml` run for this commit,
or the `query-doctor-log` artifact is missing, state that explicitly
in your review summary instead of silently skipping this step.
