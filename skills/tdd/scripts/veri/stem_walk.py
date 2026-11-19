"""The whole-word stem walk: which files of a tree name a path, in any language (PRD 031.4's LG24).

Interface:
  stem(path)            the path's basename without its last extension, `-` read as `_`.
  tree_files()          every file git does not ignore (tracked, or untracked and not excluded) that exists in the
                        working tree, outside `.git`, `.tdd`, `.venv` and `node_modules`, in git's order. Raises
                        git.GitFailed when the listing fails.
  naming(stem_, paths)  the paths among <paths> whose text holds <stem_> as a whole word, `-` and `_` counted alike;
                        an unreadable file names nothing.
  texts(paths)          each readable path among <paths> with its text, `-` read as `_`, so a caller matching many stems
                        reads each file once.
  naming_in(stems, texts_)  the paths among <texts_> (pairs as texts() gives them) whose text holds any of <stems>
                        as a whole word.
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


def texts(paths):
    found = []
    for path in paths:
        try:
            with open(path, "rb") as handle:
                found.append((path, handle.read().replace(b"-", b"_")))
        except OSError:
            continue
    return found


def naming_in(stems, texts_):
    encoded = [os.fsencode(s) for s in stems]
    word = re.compile(rb"(?<!\w)(?:" + b"|".join(re.escape(s) for s in encoded) + rb")(?!\w)")
    # The substring test first: a lookbehind regex scans every byte, a substring search does not.
    return [path for path, text in texts_ if any(s in text for s in encoded) and word.search(text)]


def naming(stem_, paths):
    return naming_in([stem_], texts(paths))
