file 40
skills/tdd/scripts/veri/install_links.py
old 85
            os.symlink(os.path.join(veri_skills, name), link)
            print(name)
new 81
            os.symlink(os.path.join(veri_skills, name), link)
        print(name)
command 334
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpixqyvyzs/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_second_run_on_a_repo_already_holding_all_eight_links_prints_nothing_on_stdout

file 40
skills/tdd/scripts/veri/install_links.py
old 23
            print(name)
new 16
            pass
command 336
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpixqyvyzs/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_after_one_veri_link_is_left_dangling_prints_one_stdout_line_for_that_skill_only

file 40
skills/tdd/scripts/veri/install_links.py
old 89
        if os.path.islink(link) and not os.path.exists(link):
            os.unlink(link)
new 12
        pass
command 336
/private/var/folders/pd/gj5qklqn5jl5cwzqt6036jhr0000gn/T/tmpixqyvyzs/scripts/timed-test-run.sh target skills/tdd/scripts/tests/py/test_install_links_process.py make test TESTS=skills/tdd/scripts/tests/py/test_install_links_process.py::test_install_links_sh_after_one_veri_link_is_left_dangling_prints_one_stdout_line_for_that_skill_only

