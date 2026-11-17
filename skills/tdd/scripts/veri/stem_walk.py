"""The whole-word stem walk: which files of a tree name a path, in any language (PRD 031.4's LG24).

Interface:
  stem(path)            the path's basename without its last extension, `-` read as `_`.
  tree_files()          every file git does not ignore (tracked, or untracked and not excluded) that exists in the
                        working tree, outside `.git`, `.tdd`, `.venv` and `node_modules`, in git's order. Raises
                        git.GitFailed when the listing fails.
  naming(stem_, paths)  the paths among <paths> whose text holds <stem_> as a whole word, `-` and `_` counted alike;
                        an unreadable file names nothing.
"""
import os
import re

import git

SKIPPED = frozenset((".git", ".tdd", ".venv", "node_modules"))


def stem(path):
    return os.path.splitext(os.path.basename(path))[0].replace("-", "_")


def tree_files():
    listed = git.out("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    return [p for p in dict.fromkeys(listed.split("\0"))
            if p and not SKIPPED.intersection(p.split("/")[:-1]) and os.path.isfile(p)]


def naming(stem_, paths):
    word = re.compile(rb"(?<!\w)" + re.escape(os.fsencode(stem_)) + rb"(?!\w)")
    found = []
    for path in paths:
        try:
            with open(path, "rb") as handle:
                text = handle.read().replace(b"-", b"_")
        except OSError:
            continue
        if word.search(text):
            found.append(path)
    return found
