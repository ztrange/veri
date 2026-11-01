file 40
skills/tdd/scripts/veri/install_links.py
old 32
argv[0] if argv else os.getcwd()
new 27
argv[0] if argv else "/tmp"
command 346
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmppgvqsrm3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_refuses_a_directory_outside_git_naming_it_and_with_no_argument_uses_the_current_directory

file 40
skills/tdd/scripts/veri/install_links.py
old 70
print("install-links: not a git repository: " + root, file=sys.stderr)
new 61
print("install-links: not a git repository", file=sys.stderr)
command 346
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmppgvqsrm3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_refuses_a_directory_outside_git_naming_it_and_with_no_argument_uses_the_current_directory

file 40
skills/tdd/scripts/veri/install_links.py
old 26
os.path.join(SKILLS, name)
new 25
os.path.join("rel", name)
command 331
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmppgvqsrm3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_points_each_link_at_the_normalised_absolute_path_of_its_skill_in_the_clone

