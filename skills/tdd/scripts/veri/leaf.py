"""The one place a leaf is launched through supervise.sh."""
import os
import subprocess

from run_verdict import SCRIPTS


def launch(name, prompt, *args, env=None):
    return subprocess.run([os.path.join(SCRIPTS, "supervise.sh"), name,
                           os.path.join(SCRIPTS, "run-leaf.sh"), prompt, *args],
                          stdout=subprocess.PIPE, env=env)
