When performing a code review on this repository, before writing
your review, fetch the `django-query-doctor` findings for this
pull request's exact head commit using these concrete GitHub API
calls (repository `inghvar/query_check`):

1. `GET /repos/inghvar/query_check/actions/artifacts?name=query-doctor-log`
   — list artifacts named `query-doctor-log`. Each entry includes
   `workflow_run.head_sha` and `expired`. Select the entry where
   `workflow_run.head_sha` equals this pull request's current head
   commit SHA and `expired` is `false`. Read that entry's `id` field
   (call it `ARTIFACT_ID`).
2. `GET /repos/inghvar/query_check/actions/artifacts/ARTIFACT_ID/zip`
   — downloads the artifact as a ZIP archive (or use the
   `archive_download_url` field from step 1's response directly).
3. Unzip the downloaded archive and read the `query_doctor.log` file
   inside it — it is the raw, unedited output of `django-query-doctor`
   for this exact commit. This file is NOT committed to the
   repository; it only exists as this workflow artifact, so you must
   fetch it with the above calls using your available GitHub tools.
4. Each `[WARNING]`/`[CRITICAL]` line in that log is a required,
   distinct finding. Leave one review comment per such line, at the
   file/line it names, even if several lines share the same root
   cause. Do not merge, paraphrase away, or skip any of them.
