# query-doctor findings for this PR's head commit

`django-query-doctor` ran the full test suite against this branch and
reported 5 findings below. Each is a separate, distinct finding, even
though they share one root cause.

1. `articles/tests.py:62` in `test_get_article()` — Duplicate query:
   2 identical queries for table `accounts_user`.
2. `articles/tests.py:82` in `test_update_article()` — Duplicate query:
   2 identical queries for table `accounts_user`.
3. `articles/tests.py:91` in `test_delete_article()` — Duplicate query:
   2 identical queries for table `accounts_user`.
4. `articles/tests.py:98` in `test_favorite_article()` — Duplicate query:
   2 identical queries for table `accounts_user`.
5. `articles/tests.py:105` in `test_unfavorite_article()` — Duplicate
   query: 2 identical queries for table `accounts_user`.

Root cause: `ArticleView.queryset` in `articles/views.py` is missing
`select_related("author")` in this PR, so `ArticleSerializer.get_author()`
fetches the author row separately from the one JWT auth already fetched
for `request.user`.

Fix: restore `queryset = Article.objects.select_related("author")`.
