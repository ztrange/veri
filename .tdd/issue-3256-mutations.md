before 40
0c22e1761008c4cc4a4d838f46b2a39f7d07da9e
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 163
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_the_posted_red_and_verify_red_headings_match_the_red_metrics_family_as_hand_composed_ones_do

before 40
25a2f314d78c018383e70b3dd60c3b8fc4042f20
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 170
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_the_red_metrics_family_pattern_matches_the_emoji_heading_text_each_red_and_verify_red_comment_posts

file 34
skills/tdd/scripts/veri/metrics.py
old 20
"🔴 Red|🔎 verify-red"
new 16
"Red|verify-red"
context 36
    ("🔴 Red", "🔴 Red|🔎 verify-red"),
command 170
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_the_red_metrics_family_pattern_matches_the_emoji_heading_text_each_red_and_verify_red_comment_posts

before 40
559053c95f14e77f1b8cd8397dfe7ee3de34f0d8
keep 48
skills/tdd/scripts/tests/py/unit/test_comment.py
command 184
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_red_with_an_unknown_flag_or_a_note_file_lacking_its_path_exits_2_with_usage_posting_nothing_unlike_the_valid_call

file 34
skills/tdd/scripts/veri/comment.py
old 64
len(argv) == 4 and argv[1] == "red" and argv[2] == "--note-file"
new 35
len(argv) >= 3 and argv[1] == "red"
context 72
    if len(argv) == 4 and argv[1] == "red" and argv[2] == "--note-file":
command 184
make test TESTS=skills/tdd/scripts/tests/py/unit/test_comment.py::test_red_with_an_unknown_flag_or_a_note_file_lacking_its_path_exits_2_with_usage_posting_nothing_unlike_the_valid_call

