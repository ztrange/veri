"""comment-class.sh's classification, run in-process."""
import re
import sys

USAGE = "usage: comment-class.sh [--sweepable] <file>…"

BLANKS = " \t\n\v\f\r"
SPACE = "[" + BLANKS + "]"
NAME = "[A-Za-z_][A-Za-z0-9_]*"


def not_space(extra=""):
    return "[^" + extra + BLANKS + "]"


WRITER = r"\|" + SPACE + "*(tee|dd|sponge)" + SPACE
COMMENT = re.compile("^" + SPACE + "*#")
MARKED = re.compile("^" + SPACE + "*# (hazard|pass-through):")
MD_ASSIGNMENT = re.compile("(" + NAME + ")=" + not_space(";") + "*\\.md[\"']?(" + SPACE + "|;|$)")
HEREDOC = re.compile("<<(-?)" + SPACE + "*[\"']?(" + NAME + ")")
FD_REDIRECT = re.compile("[02-9]>+" + SPACE + "*" + not_space() + "*")
TO_FILE = re.compile(">" + SPACE + "*" + not_space("&"))
TO_WRITER = re.compile(WRITER)
TO_MD = re.compile("(>|" + WRITER + "[^|]*)" + SPACE + "*" + not_space("&|") + "*\\.md[\"']?(" + SPACE + "|$)")
TO_VARIABLE = re.compile(">" + SPACE + "*\"?\\$(" + NAME + ")")


class Scanner:
    def __init__(self, sweepable, out):
        self.sweepable = sweepable
        self.out = out
        self.cls = self.dash = self.body = 0

    def reset(self, first):
        self.delim, self.q, self.mdvar = "", "", set()
        self.header = first.startswith("#!")

    def pop(self):
        self.q = self.q[:-1]

    def scan(self, s):
        u = []
        i = 0
        while i < len(s):
            c, t = s[i], self.q[-1:]
            u.append("_" if t in ("'", '"') and c == "<" else c)
            if t == "'":
                if c == "'":
                    self.pop()
            elif c == "\\":
                i += 1
            elif t == '"':
                if c == '"':
                    self.pop()
                elif c == "$" and s[i + 1:i + 2] == "(":
                    self.q += "("
                    i += 1
            elif t == "(" and c == ")":
                self.pop()
            elif t == "(" and c == "(":
                self.q += "("
            elif c == "#" and i > 0 and re.match(SPACE, s[i - 1]):
                return "".join(u)
            elif c in ("'", '"'):
                self.q += c
            i += 1
        return "".join(u)

    def record(self, name, number, line):
        if number == 1:
            self.reset(line)
        comment = COMMENT.match(line) is not None
        if not comment:
            self.header = False
        if self.delim != "":
            end = line.lstrip("\t") if self.dash else line
            if end == self.delim:
                self.delim = ""
            elif comment and not (self.sweepable and (self.cls == 3 or (self.body and end.startswith("#!")))):
                self.out.write("%s:%d:%d\n" % (name, number, self.cls))
            self.body = 0
            return
        if self.q != "":
            self.scan(line)
            return
        if comment:
            if not (self.sweepable and (self.header or MARKED.match(line))):
                self.out.write("%s:%d:1\n" % (name, number))
            return
        line = self.scan(line).replace("<<<", "")
        assigned = MD_ASSIGNMENT.search(line)
        if assigned:
            self.mdvar.add(assigned.group(1))
        opener = HEREDOC.search(line)
        if opener:
            out = FD_REDIRECT.sub("", line)
            self.cls = 2 if TO_FILE.search(out) or TO_WRITER.search(out) else 3
            if TO_MD.search(out):
                self.cls = 3
            self.dash = opener.group(1) == "-"
            self.body = 1
            self.delim = opener.group(2)
            variable = TO_VARIABLE.search(out)
            if variable and variable.group(1) in self.mdvar:
                self.cls = 3


ASSIGNMENT = re.compile(NAME + "=")


def read_lines(name):
    if name == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(name, "rb") as f:
            data = f.read()
    lines = data.decode("latin-1").split("\n")
    if lines[-1] == "":
        lines.pop()
    return lines


def main(argv):
    args = list(argv)
    sweepable = bool(args) and args[0] == "--sweepable"
    if sweepable:
        args.pop(0)
    if not args or args[0] == "":
        print(USAGE, file=sys.stderr)
        return 2
    scanner = Scanner(sweepable, sys.stdout)
    for name in args:
        if name == "" or ASSIGNMENT.match(name):
            continue
        try:
            lines = read_lines(name)
        except OSError as error:
            print("comment-class.sh: can't open file %s: %s" % (name, error.strerror), file=sys.stderr)
            return 2
        for number, line in enumerate(lines, 1):
            scanner.record(name, number, line)
    return 0


if __name__ == "__main__":
    import entry
    entry.run(main, sys.argv[1:])
