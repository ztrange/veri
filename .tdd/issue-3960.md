# Plan for #3960 — PRD 022.8: a token-shaped string never reaches a posted comment

- [x] redact replaces a token of each prefix gh[pousr]_ followed by 36 or more letters and digits with [redacted] ⟦criterion 1⟧
- [x] redact replaces a github_pat_ token with [redacted] ⟦criterion 1⟧
- [x] redact replaces an sk-ant- key with [redacted] ⟦criterion 1⟧
- [x] redact replaces an AKIA access key id with [redacted] ⟦criterion 1⟧
- [x] redact replaces every occurrence of the value of a variable VERI_REDACT_VARS names ⟦criterion 1⟧
- [x] redact leaves alone a listed variable's value shorter than 8 characters ⟦criterion 1⟧
- [x] with VERI_REDACT_VARS unset GH_TOKEN's value is redacted, and set to another name that name's value is ⟦criterion 2⟧
- [x] gh_issue_comment hands gh the body redacted ⟦criterion 3⟧
- [x] a comment body with nothing to redact reaches gh byte-identical ⟦criterion 4⟧
- [x] gh_comment_post and gh_comment_edit hand gh the body redacted
- [x] a token wrapped across a line break or a JSON \n escape is redacted
- [x] a token inside a URL, a query string or glued to text with no word boundary is redacted
- [x] the base64 of a token or of a listed variable's value is redacted
- [x] a 1 MB body holding tokens is redacted within the case timeout
- [x] no veri module names a gh command line outside github.bounded's callers, save preflight's reads and queued_merge's merge, which carry no body
- [x] the comment.sh entry of SCRIPTS.md says comments are redacted, naming the patterns and VERI_REDACT_VARS ⟦criterion 5⟧
