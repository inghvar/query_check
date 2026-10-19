## django-query-doctor findings for this change

`django-query-doctor` ran against the full test suite for this branch's
head commit and reported the following DB-query issues. Treat each one
as a required review finding: leave an inline comment at the given
file/line describing the problem and the suggested fix.

- `articles/tests.py:62` in `test_get_article()` — Duplicate query:
  2 identical queries for table `accounts_user`.
  Fix: assign the queryset result to a variable and reuse it instead
  of executing the same query multiple times.
- `articles/tests.py:82` in `test_update_article()` — Duplicate query:
  2 identical queries for table `accounts_user`.
  Fix: assign the queryset result to a variable and reuse it instead
  of executing the same query multiple times.
- `articles/tests.py:91` in `test_delete_article()` — Duplicate query:
  2 identical queries for table `accounts_user`.
  Fix: assign the queryset result to a variable and reuse it instead
  of executing the same query multiple times.
- `articles/tests.py:98` in `test_favorite_article()` — Duplicate query:
  2 identical queries for table `accounts_user`.
  Fix: assign the queryset result to a variable and reuse it instead
  of executing the same query multiple times.
- `articles/tests.py:105` in `test_unfavorite_article()` — Duplicate
  query: 2 identical queries for table `accounts_user`.
  Fix: assign the queryset result to a variable and reuse it instead
  of executing the same query multiple times.

These duplicate queries are caused by `ArticleView.queryset` in
`articles/views.py` missing `select_related("author")` in this PR.
