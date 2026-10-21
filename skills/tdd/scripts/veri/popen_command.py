"""The command a subprocess.Popen `args` names."""
import os


def command_words(args):
    return [args] if isinstance(args, (str, bytes, os.PathLike)) else list(args)


def command_basename(args):
    words = command_words(args)
    return os.path.basename(os.fsdecode(words[0])) if words else ""
