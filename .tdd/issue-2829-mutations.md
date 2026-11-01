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

