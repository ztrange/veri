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

file 40
skills/tdd/scripts/veri/install_links.py
old 16
else os.getcwd()
new 19
else "/nonexistent"
command 332
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmppgvqsrm3/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_with_no_argument_installs_into_the_repository_holding_the_current_directory

file 40
skills/tdd/scripts/veri/install_links.py
old 74
os.symlink(os.path.join(_veri_skills(), name), os.path.join(target, name))
new 241
os.symlink(os.path.join(_veri_skills(), name), os.path.join(target, name)) if name != "vcoord" else os.symlink(os.path.join(_veri_skills(), "vdev", "..", "vdev"), os.path.join(target, name)) or os.symlink("/tmp", os.path.join(target, "tdd"))
command 334
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp80y1pz_6/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_link_lets_the_filesystem_resolve_dotdot_to_the_unlinked_tdd_and_vmerge_skills

file 40
skills/tdd/scripts/veri/install_links.py
old 63
os.path.join(_veri_skills(), name), os.path.join(target, name))
new 186
os.path.join(_veri_skills(), name), os.path.join(target, name)) if name != "vcoord" else (os.makedirs(target + "/x/vcoord"), os.symlink(target + "/x/vcoord", os.path.join(target, name)))
command 334
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp80y1pz_6/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_link_lets_the_filesystem_resolve_dotdot_to_the_unlinked_tdd_and_vmerge_skills

file 40
skills/tdd/scripts/veri/install_links.py
old 80
target = os.path.join(os.path.dirname(done.stdout.strip()), ".claude", "skills")
new 48
target = os.path.join(root, ".claude", "skills")
command 355
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp80y1pz_6/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_run_against_a_linked_worktree_of_a_project_installs_into_its_main_tree_and_nothing_in_the_worktree

file 40
skills/tdd/scripts/veri/install_links.py
old 52
                return 2
        for name in LINKED:
new 48
                pass
        for name in LINKED:
command 336
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp80y1pz_6/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_leaves_a_symlink_elsewhere_untouched_and_exits_2_naming_it_with_no_link_created

file 40
skills/tdd/scripts/veri/install_links.py
old 38
if os.path.lexists(link) and not held:
new 22
if False and not held:
command 329
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmp80y1pz_6/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_leaves_a_lone_dangling_symlink_elsewhere_untouched_and_exits_2_naming_it

