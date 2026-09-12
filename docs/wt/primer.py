"""primer.py — the bash reference: one entry per construct.

id    the anchor, and the key used in commentary as {{id|display text}}
sig   what the construct looks like
name  its title
gloss short, shown in the hover tooltip
body  the full reference entry (HTML)
seen  where it appears in veri
"""

PRIMER = [{'id': 'p-header',
  'name': 'Header &amp; safety',
  'items': [{'id': 'p-shebang',
             'sig': '#!/usr/bin/env bash',
             'name': 'Shebang',
             'body': '',
             'seen': 'All 14 scripts, line 1.',
             'gloss': 'Tells the kernel to run this file with bash, found via PATH rather than a '
                      'hard-coded location.'},
            {'id': 'p-strict',
             'sig': 'set -euo pipefail',
             'name': 'Strict mode',
             'body': '<ul>\n'
                     '      <li><code>-e</code> — <strong>exit immediately</strong> if any command '
                     'returns\n'
                     '          non-zero. Fail fast instead of continuing on corrupt state.</li>\n'
                     '      <li><code>-u</code> — <strong>error on an unset variable</strong> '
                     'instead of quietly\n'
                     '          substituting an empty string. Catches typos in variable names, '
                     'which are\n'
                     '          otherwise invisible.</li>\n'
                     '      <li><code>-o pipefail</code> — a <strong>pipeline fails if any stage '
                     'fails</strong>.\n'
                     "          By default <code>a | b</code> reports only <code>b</code>'s "
                     'status, so a crash in\n'
                     '          <code>a</code> vanishes.</li>\n'
                     '    </ul>',
             'seen': '12 of 13 scripts. Read it as "make bash behave like a normal language".',
             'gloss': 'Fail fast: exit on any error, error on unset variables, and let a pipeline '
                      'fail if any stage does.'},
            {'id': 'p-strict-partial',
             'sig': 'set -uo pipefail',
             'name': 'Strict mode without <code>-e</code>',
             'body': '',
             'seen': '<code>supervise.sh</code> and <code>wait-leaf.sh</code> &mdash; the two scripts whose whole job is reporting a non-zero result rather than dying of one.',
             'gloss': 'Strict mode with <code>-e</code> deliberately left out, so an expected '
                      "non-zero exit doesn't kill the script."},
            {'id': 'p-sete',
             'sig': 'set +e … rc=$? … set -e',
             'name': 'Temporarily disabling fail-fast',
             'body': '<p>\n'
                     '      Wherever you see this, the exit code is <strong>meaningful '
                     'information</strong>, not a\n'
                     '      malfunction — the script wants to branch on it.\n'
                     '    </p>',
             'seen': '<code>run-leaf.sh</code>, <code>verify.sh</code> (twice).',
             'gloss': 'Turn fail-fast off around one command so you can capture its exit code '
                      'instead of dying on it.'},
            {'id': 'p-shopt',
             'sig': 'shopt -u patsub_replacement 2&gt;/dev/null || true',
             'name': 'A shell option, disabled portably',
             'body': '<p>\n'
                     '      <code>shopt</code> flips a named shell behaviour on or off &mdash; finer-grained '
                     'switches than <a class="ref" href="#p-strict">set -o</a> covers. bash 5.2 added '
                     '<code>patsub_replacement</code> and turned it ON by default: inside '
                     '<a class="ref" href="#p-subst">${var//pattern/replacement}</a>, an unescaped '
                     '<code>&amp;</code> in the <em>replacement</em> now expands to whatever the pattern just '
                     'matched, the way <code>sed</code>&rsquo;s <code>&amp;</code> does. A value carrying a '
                     'literal <code>&amp;</code> is then rewritten silently &mdash; no error, no bad exit '
                     'code.\n'
                     '    </p><p>\n'
                     '      <code>shopt -u patsub_replacement</code> turns that back off, restoring the older '
                     'purely-literal meaning every <code>${v//a/b}</code> below it relies on. macOS ships bash '
                     '3.2, which predates the option entirely: there <code>shopt -u patsub_replacement</code> '
                     'fails because the name is unknown, so '
                     '<a class="ref" href="#p-redirect">2&gt;/dev/null</a> discards the complaint and the '
                     'trailing <a class="ref" href="#p-shortcircuit">||</a> <code>true</code> makes the whole '
                     'line a no-op &mdash; real work on 5.2+, harmless everywhere older.\n'
                     '    </p>',
             'seen': '<code>build-develop-prompt.sh</code> and <code>build-verify-prompt.sh</code>, right '
                     'after <code>set -euo pipefail</code>, guarding every <code>${var//pattern/repl}</code> '
                     'substitution below it.',
             'gloss': 'Turns one named shell behaviour on or off. Here: disable bash 5.2&rsquo;s '
                      '<code>&amp;</code>-means-the-match default in <code>${v//a/b}</code>, portably '
                      'no-op&rsquo;d on bash 3.2 where the option does not exist.'}]},
 {'id': 'p-vars',
  'name': 'Variables &amp; expansion',
  'items': [{'id': 'p-quote',
             'sig': '"$var"',
             'name': 'Quoting — the one habit that matters most',
             'body': '<p>\n'
                     '      Wrapping it in double quotes suppresses both, making the variable '
                     'behave like a single\n'
                     '      value the way it would in any other language. Practically every '
                     'variable reference in\n'
                     "      these scripts is quoted, and the few that aren't are marked with a "
                     'comment explaining\n'
                     '      why.\n'
                     '    </p>',
             'seen': 'Everywhere. Treat an unquoted <code>$x</code> as a bug until proven '
                     'otherwise.',
             'gloss': 'Quoting stops the shell splitting the value on whitespace and expanding it '
                      'as a filename pattern.'},
            {'id': 'p-required',
             'sig': '"${1:?usage: …}"',
             'name': 'Required-argument assertion',
             'body': '<p>\n'
                     '      The exit status on failure is <code>1</code> from the shell itself, so '
                     'a script wanting\n'
                     '      a specific code for bad arguments still validates separately.\n'
                     '    </p>',
             'seen': 'Opening lines of nearly every script — this is how they declare their '
                     'signature.',
             'gloss': 'Use this argument, or print the message and abort. An inline precondition '
                      'check.'},
            {'id': 'p-default',
             'sig': '"${2:-default}"',
             'name': 'Default value',
             'body': '<p>\n'
                     '      This is how every tunable in veri works: '
                     '<code>"${VERI_TIMEOUT:-900}"</code> means\n'
                     '      "whatever the environment says, else 900". That single idiom is what '
                     'makes the scripts\n'
                     '      testable — a test can set <code>VERI_TIMEOUT=2</code> and not wait '
                     'fifteen minutes.\n'
                     '    </p>',
             'seen': 'All tunables; every optional argument.',
             'gloss': 'Use this value if set and non-empty, otherwise fall back to the default. '
                      'Never assigns.'},
            {'id': 'p-guard',
             'sig': '"${VAR:-}"',
             'name': 'The empty-default guard',
             'body': '',
             'seen': '<code>${CLAUDE_BIN:-claude}</code>, <code>${VERIFY_LEAF_ARGS:-}</code>, '
                     '<code>${GH_REPO:-}</code>.',
             'gloss': "Default to nothing, so reading an optional variable doesn't abort under "
                      '<code>set -u</code>.'},
            {'id': 'p-cmdsub',
             'sig': '$( … )',
             'name': 'Command substitution',
             'body': '<p>\n'
                     '      Two consequences worth holding onto. First, it is a separate process, '
                     'so it cannot\n'
                     "      modify the caller's variables. Second — and this catches everyone — "
                     'it\n'
                     '      <strong>strips all trailing newlines</strong> from what it captures. '
                     'Scripts that need\n'
                     '      the newline back add it explicitly with <a class="ref" '
                     'href="#p-printf">printf \'%s\\n\'</a>.\n'
                     '    </p>',
             'seen': 'Everywhere. The backtick form <code>` … `</code> means the same thing but '
                     "doesn't nest; it is not used here.",
             'gloss': 'Run a command in a child process and evaluate to its stdout. Strips all '
                      'trailing newlines.'},
            {'id': 'p-special',
             'sig': '$? &nbsp; $! &nbsp; $@ &nbsp; $# &nbsp; $0',
             'name': 'Special parameters',
             'body': '',
             'seen': '',
             'gloss': '<code>$?</code> last exit status · <code>$!</code> last background PID · '
                      '<code>$@</code> all arguments · <code>$#</code> count · <code>$0</code> '
                      'script path.'},
            {'id': 'p-subst',
             'sig': '${v//search/replace}',
             'name': 'Substring replacement',
             'body': '<p>\n'
                     '      Crucially it is a <strong>literal</strong> replacement. That is why '
                     'veri templates\n'
                     '      prompts with this instead of <code>sed</code>: an issue body is '
                     'arbitrary human text\n'
                     '      full of <code>&amp;</code>, <code>\\</code> and <code>/</code>, all of '
                     'which\n'
                     '      <code>sed</code> treats as special and would corrupt.\n'
                     '    </p>',
             'seen': '<code>build-verify-prompt.sh</code> — the whole templating engine is four of '
                     'these.',
             'gloss': 'Replace every occurrence, literally — no pattern language, so arbitrary '
                      'text passes through intact.'},
            {'id': 'p-strip',
             'sig': '${v#pat} &nbsp; ${v##pat} &nbsp; ${v%pat} &nbsp; ${v%%pat}',
             'name': 'Prefix and suffix stripping',
             'body': '<p>\n'
                     '      Mnemonic: on a US keyboard <code>#</code> sits left of <code>%</code>, '
                     'matching which\n'
                     '      end each one bites. These build the whitespace-trimming helpers and '
                     'the "first token of\n'
                     '      a line" extraction in <code>parse-verdict.sh</code>, with no external '
                     'process involved.\n'
                     '    </p>',
             'seen': '<code>parse-verdict.sh</code> heavily; <code>supervise.sh</code>.',
             'gloss': 'Cut a matching pattern off one end. <code>#</code> from the front, '
                      '<code>%</code> from the back; doubled is greedy.'},
            {'id': 'p-printfv',
             'sig': 'printf -v name \'%s\\n\' "${arr[@]}"',
             'name': 'Printf into a variable',
             'body': '',
             'seen': '<code>parse-verdict.sh</code>, rejoining the reason lines.',
             'gloss': "Write printf's output into a variable instead of stdout, preserving "
                      'trailing newlines.'},
            {'id': 'p-ansic',
             'sig': "$'\\n'",
             'name': 'ANSI-C quoting',
             'body': '',
             'seen': '<code>parse-verdict.sh</code>, splitting the reason on its last line.',
             'gloss': 'Interprets C escapes, so this is a real newline character rather than a '
                      'backslash and an n.'},
            {'id': 'p-envprefix',
             'sig': 'VAR=value command',
             'name': 'Per-command environment',
             'body': '',
             'seen': '<code>tick-criterion.sh</code>, passing the matcher to <code>awk</code>.',
             'gloss': 'Set a variable for one command only, without leaking it into the rest of '
                      'the script.'}]},
 {'id': 'p-tests',
  'name': 'Tests &amp; arithmetic',
  'items': [{'id': 'p-test',
             'sig': '[[ … ]]',
             'name': 'Conditional expression',
             'body': '<ul>\n'
                     '      <li><code>-f path</code> — a regular file exists</li>\n'
                     '      <li><code>-r path</code> — the file is readable</li>\n'
                     '      <li><code>-n "$s"</code> — the string is non-empty · <code>-z '
                     '"$s"</code> — it is empty</li>\n'
                     '      <li><code>"$a" == "$b"</code> — string equality</li>\n'
                     '      <li><code>-ge -lt</code> — numeric comparison (inside <code>[[ '
                     ']]</code>, unlike\n'
                     '          <code>(( ))</code>, you cannot use <code>&gt;</code> for numbers — '
                     'it would mean\n'
                     '          redirect)</li>\n'
                     '    </ul>',
             'seen': 'All over. <code>[[ -f "$rcfile" ]]</code> is the heart of the watch loop.',
             'gloss': "Bash's conditional expression: file tests, string tests, and numeric "
                      'comparison.'},
            {'id': 'p-regex',
             'sig': '[[ "$s" =~ regex ]] &nbsp;→&nbsp; BASH_REMATCH',
             'name': 'Built-in regular expressions',
             'body': '<p>\n'
                     '      The right-hand side must be <strong>unquoted</strong> to be treated as '
                     'a pattern —\n'
                     '      quoting it makes it a literal string. That is why these scripts assign '
                     'a regex to a\n'
                     '      variable and then write <code>=~ $re</code> bare.\n'
                     '    </p>',
             'seen': '<code>parse-verdict.sh</code>, <code>next-unchecked.sh</code>.',
             'gloss': 'Built-in regex match; captures land in <code>BASH_REMATCH</code>. The '
                      'pattern must be unquoted.'},
            {'id': 'p-arith',
             'sig': '(( … ))',
             'name': 'Arithmetic evaluation',
             'body': '<p>\n'
                     '      One inversion to remember: it follows <em>C</em> truthiness, not shell '
                     'truthiness. A\n'
                     '      result of zero is "false" and so returns exit status '
                     '<strong>1</strong>. Harmless in an\n'
                     '      <code>if</code>, but <code>(( count++ ))</code> as a bare statement '
                     'under\n'
                     '      <a class="ref" href="#p-strict">set -e</a> will kill your script when '
                     'the count is zero.\n'
                     '      veri sidesteps it entirely with <code>x=$(( x + 1 ))</code>.\n'
                     '    </p>',
             'seen': '<code>supervise.sh</code> — both clocks and the retry counter.',
             'gloss': 'Integer maths with C syntax — variables need no <code>$</code> and '
                      'comparisons read normally.'},
            {'id': 'p-case',
             'sig': 'case "$x" in … esac',
             'name': 'Pattern dispatch',
             'body': '',
             'seen': '<code>classify-bail.sh</code> is essentially nothing else; also the '
                     'status→exit-code mapping in <code>supervise.sh</code>.',
             'gloss': "Bash's switch. Glob patterns, <code>|</code> for alternatives, "
                      '<code>*)</code> as the default, no fall-through.'},
            {'id': 'p-shortcircuit',
             'sig': 'cmd1 || cmd2 &nbsp;·&nbsp; cmd1 &amp;&amp; cmd2',
             'name': 'Short-circuit chaining',
             'body': '<p>\n'
                     '      A second, subtler use: a command on the left of <code>||</code> is '
                     'exempt from\n'
                     '      <a class="ref" href="#p-strict">set -e</a>, because its failure is '
                     'being handled. That\n'
                     '      is why <code>cmd || true</code> is the idiom for "let this one fail '
                     'harmlessly".\n'
                     '    </p>',
             'seen': 'The portability fallbacks and kill attempts in <code>supervise.sh</code>.',
             'gloss': '<code>||</code> runs the right side only on failure, '
                      '<code>&amp;&amp;</code> only on success. Also exempts the left from '
                      '<code>set -e</code>.'}]},
 {'id': 'p-arrays',
  'name': 'Arrays',
  'items': [{'id': 'p-array',
             'sig': 'arr=( a b c ) &nbsp;→&nbsp; "${arr[@]}"',
             'name': 'Arrays, and why they exist',
             'body': '<p>\n'
                     '      The reason it matters: if you keep arguments in a plain string and '
                     'pass\n'
                     '      <code>$args</code>, the shell re-splits it on whitespace, so an '
                     'argument containing a\n'
                     '      space silently becomes two. An array preserves the boundaries you '
                     'meant. veri builds\n'
                     "      the verifier's command-line flags this way.\n"
                     '    </p>',
             'seen': '<code>verify.sh</code> (leaf flags), <code>tick-issue-criterion.sh</code> '
                     '(repo flags).',
             'gloss': 'Holds a list of arguments so each stays one argument, even when it contains '
                      'spaces.'},
            {'id': 'p-arrayidx',
             'sig': '"${!arr[@]}" &nbsp; ${#arr[@]} &nbsp; "${arr[@]:n}"',
             'name': 'Indices, length, slice',
             'body': '',
             'seen': '',
             'gloss': '<code>${!a[@]}</code> the indices · <code>${#a[@]}</code> the length · '
                      '<code>${a[@]:n}</code> a slice from n.'},
            {'id': 'p-arrayempty',
             'sig': '"${arr[@]+"${arr[@]}"}"',
             'name': 'The empty-array guard',
             'body': '<p>\n'
                     '      The <code>${x+…}</code> form means "if <code>x</code> is set, produce '
                     'this, otherwise\n'
                     '      produce nothing at all". Wrapping the array in it makes an empty array '
                     'expand to zero\n'
                     '      arguments instead of exploding. You only need it where the array is '
                     'legitimately\n'
                     '      allowed to be empty.\n'
                     '    </p>',
             'seen': '<code>tick-issue-criterion.sh</code>, where <code>--repo</code> may be '
                     'absent.',
             'gloss': 'Lets an empty array expand to zero arguments instead of aborting under '
                      '<code>set -u</code> on old bash.'}]},
 {'id': 'p-text',
  'name': 'Text &amp; I/O',
  'items': [{'id': 'p-redirect',
             'sig': '&gt; &nbsp; &gt;&gt; &nbsp; &lt; &nbsp; &lt;&lt;&lt; &nbsp; 2&gt;&amp;1 &nbsp; 2&gt;/dev/null',
             'name': 'Redirection',
             'body': '<ul>\n'
                     '      <li><code>&gt; file</code> — send stdout to the file, '
                     '<strong>truncating it to empty\n'
                     '          first</strong>. That truncation happens the instant the line is '
                     'parsed, before the\n'
                     '          command runs — the classic way to destroy a file you meant to '
                     'read.</li>\n'
                     '      <li><code>&gt;&gt; file</code> — append instead.</li>\n'
                     '      <li><code>&lt; file</code> — feed the file in as stdin.</li>\n'
                     '      <li><code>&lt;&lt;&lt; "$str"</code> — a <strong>here-string</strong>: '
                     'hand a variable to a command as its\n'
                     '          stdin, with no pipe and no temp file. Unlike a pipe, the command '
                     'on the left of a\n'
                     '          here-string is not a separate process, so a loop reading one can '
                     'set variables the\n'
                     '          rest of the script still sees afterwards.</li>\n'
                     '      <li><code>2&gt;&amp;1</code> — "make stream 2 go wherever stream 1 '
                     'currently goes". The\n'
                     '          <code>&amp;</code> means "this is a stream number, not a '
                     'filename". Order matters:\n'
                     '          it copies the <em>current</em> destination of stdout, so it must '
                     'come after any\n'
                     '          <code>&gt;</code>.</li>\n'
                     '      <li><code>2&gt;/dev/null</code> — discard stderr, for a command '
                     'expected to complain.</li>\n'
                     '    </ul>\n'
                     '    <p>\n'
                     '      The convention veri holds to throughout: <strong>stdout is data, '
                     'stderr is\n'
                     "      commentary.</strong> That is what lets a script's output be piped "
                     'straight into the\n'
                     '      next one while its status messages still reach a human.\n'
                     '    </p>',
             'seen': 'Every script.',
             'gloss': 'Rewires the three standard streams: 0 stdin, 1 stdout, 2 stderr. '
                      '<code>&gt;</code> truncates immediately; <code>&lt;&lt;&lt;</code> feeds '
                      'a variable in as stdin without a pipe.'},
            {'id': 'p-readloop',
             'sig': 'while IFS= read -r line || [[ -n "$line" ]]',
             'name': 'Reading lines without corrupting them',
             'body': '<ul>\n'
                     '      <li><code>IFS=</code> — empties the field separator for this command, '
                     'so leading and\n'
                     '          trailing whitespace on the line is <em>not</em> trimmed.</li>\n'
                     '      <li><code>read</code> — reads one line into the variable, returning '
                     'non-zero at\n'
                     '          end-of-file, which ends the loop.</li>\n'
                     '      <li><code>-r</code> — <strong>raw</strong>: do not treat backslashes '
                     'as escapes.\n'
                     '          Without it, <code>\\n</code> in the input gets mangled.</li>\n'
                     '      <li><code>|| [[ -n "$line" ]]</code> — the subtle one. If the final '
                     'line has no\n'
                     '          trailing newline, <code>read</code> stores it but still returns '
                     'non-zero, so the\n'
                     '          loop would drop it. This clause says "keep going if we did read '
                     'something".</li>\n'
                     '    </ul>\n'
                     '    <p>\n'
                     '      The naive alternatives — <code>for line in $(cat f)</code> — split on '
                     'spaces rather\n'
                     '      than newlines and glob-expand the results. They are simply broken.\n'
                     '    </p>',
             'seen': '<code>parse-verdict.sh</code>, <code>next-unchecked.sh</code>.',
             'gloss': 'The safe line reader: no trimming, no backslash mangling, and it keeps a '
                      'final unterminated line.'},
            {'id': 'p-glob',
             'sig': 'for f in dir/*.ext; do [ -f "$f" ]',
             'name': 'Globbing, and matching nothing',
             'body': '<ul>\n'
                     '      <li>Unquoted, a pattern like <code>dir/*.ext</code> is\n'
                     '          <strong>expanded by the shell itself</strong> before the loop ever '
                     'runs &mdash;\n'
                     '          one word per matching file.</li>\n'
                     '      <li>When nothing matches, bash\'s default behaviour is not to drop the '
                     'word: the\n'
                     '          pattern is left as <strong>its own literal text</strong>, spelled '
                     'exactly as\n'
                     '          written, and handed to the loop as if it had matched.</li>\n'
                     '      <li><code>[ -f "$f" ]</code> turns that literal-text case into false '
                     'the same way\n'
                     '          it would for any other non-existent file, so the loop body only '
                     'ever runs on\n'
                     '          a real match.</li>\n'
                     '    </ul>\n'
                     '    <p>\n'
                     '      The alternative is <code>shopt -s nullglob</code>, which makes a '
                     'non-matching\n'
                     '      pattern expand to <em>zero</em> words instead of one literal one, so '
                     'the loop\n'
                     '      runs zero times on its own and needs no <code>[ -f ]</code> guard. '
                     'Either shape\n'
                     '      works; this script picks the one that needs no global shell-option '
                     'change.\n'
                     '    </p>',
             'seen': '<code>detect-test-command.sh</code> &mdash; the only loop in the suite over '
                     'a filename pattern rather than a fixed path.',
             'gloss': 'Unquoted, a glob expands to one word per matching file &mdash; or, with '
                      'nothing to match, to its own literal text as a single word.'},
            {'id': 'p-printf',
             'sig': 'printf \'%s\\n\' "$x"',
             'name': 'printf, and why not echo',
             'body': '<p>\n'
                     "      That control is used deliberately: <code>printf '%s\\n'</code> "
                     'restores the newline\n'
                     '      that <a class="ref" href="#p-cmdsub">$( … )</a> stripped, while '
                     "<code>printf '%s'</code>\n"
                     '      writes a value with no trailing newline at all.\n'
                     '    </p>',
             'seen': 'Everywhere data is emitted. <code>echo</code> survives only for fixed '
                     'literal status strings.',
             'gloss': 'Portable and predictable, unlike <code>echo</code> — you control the '
                      'trailing newline exactly.'},
            {'id': 'p-pipe',
             'sig': 'a | b &nbsp;·&nbsp; tee file &nbsp;·&nbsp; "${PIPESTATUS[0]}"',
             'name': 'Pipes, tee, and recovering a lost status',
             'body': '<p>\n'
                     "      But a pipeline reports only the <strong>last</strong> command's exit "
                     'status, so the\n'
                     '      status of <code>a</code> is lost. <code>PIPESTATUS</code> is an array '
                     'holding the\n'
                     '      status of every stage, so <code>"${PIPESTATUS[0]}"</code> recovers the '
                     'first one. It is\n'
                     '      overwritten by the very next command, so it must be read immediately.\n'
                     '    </p>',
             'seen': "<code>run-leaf.sh</code> — how the leaf's real exit code survives being "
                     'teed.',
             'gloss': 'Pipes connect stdout to stdin; <code>tee</code> copies a stream aside; '
                      "<code>PIPESTATUS</code> recovers a stage's lost exit code."},
            {'id': 'p-noop',
             'sig': ': &nbsp;·&nbsp; : &gt; file &nbsp;·&nbsp; while :;',
             'name': 'The null command',
             'body': '',
             'seen': '<code>supervise.sh</code>: both, on adjacent lines.',
             'gloss': '<code>:</code> does nothing and succeeds. <code>: &gt; f</code> truncates a '
                      'file; <code>while :;</code> loops forever.'},
            {'id': 'p-mktemp',
             'sig': 'tmp="$(mktemp)"',
             'name': 'Temporary files',
             'body': '',
             'seen': '<code>run-leaf.sh</code>, <code>tick-issue-criterion.sh</code>.',
             'gloss': 'Atomically creates a uniquely-named temp file, avoiding the race and the '
                      'security hole of a fixed name.'},
            {'id': 'p-trap',
             'sig': 'trap \'rm -f "$tmp"\' EXIT',
             'name': 'Cleanup handlers',
             'body': '',
             'seen': '<code>run-leaf.sh</code>, <code>tick-issue-criterion.sh</code>.',
             'gloss': "Runs a command when the script exits, however it exits. Bash's "
                      '<code>finally</code> block.'},
            {'id': 'p-heredoc',
             'sig': "cmd &lt;&lt;'EOF' … EOF",
             'name': 'Here-documents',
             'body': '<p>\n'
                     '      Worth knowing chiefly for the constraint it creates: a here-document\n'
                     '      <strong>occupies stdin</strong>. A script that needs stdin for real '
                     'data cannot use one\n'
                     '      to supply a program — which is exactly why '
                     '<code>extract-result.sh</code> passes its\n'
                     '      Python via <code>-c</code> instead.\n'
                     '    </p>',
             'seen': 'The test suites; deliberately avoided in <code>extract-result.sh</code>.',
             'gloss': "Feeds a literal text block in as stdin — which is why it can't be used when "
                      'stdin carries real data.'},
            {'id': 'p-awk',
             'sig': "awk 'BEGIN{…} {…} END{…}'",
             'name': 'awk, and getting data into it safely',
             'body': '<p>\n'
                     '      Getting shell values <em>into</em> awk is where scripts go wrong: '
                     'interpolating them\n'
                     '      into the program text is an injection bug, since the value would be '
                     'parsed as code. The\n'
                     '      safe route is <a class="ref" href="#p-envprefix">the environment</a>, '
                     'read back with\n'
                     '      <code>ENVIRON["NAME"]</code>. And <code>exit 3</code> inside awk '
                     "becomes awk's exit\n"
                     '      status, which the shell can branch on.\n'
                     '    </p>',
             'seen': '<code>tick-criterion.sh</code>, entirely.',
             'gloss': 'Line-oriented text processor. Pass shell values through the environment, '
                      'never by interpolating into the program.'},
            {'id': 'p-exec',
             'sig': "exec python3 -c '…'",
             'name': 'Replacing the process',
             'body': '',
             'seen': '<code>extract-result.sh</code>, handing off to Python.',
             'gloss': 'Replaces the shell with the new program instead of forking — same PID, same '
                      'stdin, status passes straight through.'}]},
 {'id': 'p-proc',
  'name': 'Processes &amp; signals',
  'items': [{'id': 'p-func',
             'sig': 'name() { …; }',
             'name': 'Functions',
             'body': '<p>\n'
                     '      Variables are <strong>global by default</strong> unless declared '
                     '<code>local</code>.\n'
                     '      <code>supervise.sh</code> uses that deliberately: its '
                     '<code>attempt_once</code>\n'
                     '      function sets <code>status</code> and <code>reason</code> for the main '
                     'loop to read,\n'
                     '      which is how it returns four values from something that can only '
                     'return an integer.\n'
                     '    </p>',
             'seen': '<code>supervise.sh</code>, <code>parse-verdict.sh</code>.',
             'gloss': 'Arguments arrive as <code>$1</code>, <code>$2</code>…; it returns an exit '
                      'status, so data comes back via stdout or a global.'},
            {'id': 'p-bg',
             'sig': '( cmd ) &amp; &nbsp;→&nbsp; pid=$!',
             'name': 'Subshells and background jobs',
             'body': '<p>\n'
                     '      That non-waiting is the whole basis of supervision. You cannot watch a '
                     'process you are\n'
                     '      blocked on. <code>$!</code> then gives you its PID so you can watch '
                     'and, if necessary,\n'
                     '      kill it.\n'
                     '    </p>',
             'seen': '<code>supervise.sh</code> — the single most important line in veri.',
             'gloss': 'A subshell run in the background. The script continues immediately — which '
                      'is what makes watching it possible.'},
            {'id': 'p-jobcontrol',
             'sig': 'set -m &nbsp;…&nbsp; set +m',
             'name': 'Job control &amp; process groups',
             'body': '<p>\n'
                     '      <code>set -m</code> turns job control on, which puts each background '
                     'job in\n'
                     '      <strong>its own new process group</strong>, taking its children with '
                     'it. Enabling it\n'
                     '      just around the launch is the prerequisite for killing a whole process '
                     'tree in one\n'
                     '      signal.\n'
                     '    </p>',
             'seen': '<code>supervise.sh</code>, bracketing the leaf launch.',
             'gloss': 'Puts a background job in its own process group, so the whole tree can be '
                      'signalled at once.'},
            {'id': 'p-kill',
             'sig': 'kill -TERM -$pid &nbsp;·&nbsp; kill -0 $pid',
             'name': 'Signals — and the minus sign that matters',
             'body': '<ul>\n'
                     '      <li><strong>A negative PID means the process <em>group</em>.</strong>\n'
                     '          <code>kill -TERM -1234</code> signals every process in group 1234, '
                     'not just the\n'
                     "          leader. This is how you reach a leaf's own children — a test "
                     'runner it spawned —\n'
                     '          which would otherwise be orphaned and keep running.</li>\n'
                     '      <li><code>-0</code> sends <strong>no signal at all</strong>. It only '
                     'checks whether the\n'
                     '          process still exists, so it is used to poll "is it gone '
                     'yet?".</li>\n'
                     '      <li><code>-TERM</code> is the polite request: "please clean up and '
                     'exit". A program can\n'
                     '          catch it. <code>-KILL</code> cannot be caught or ignored — the '
                     'kernel destroys the\n'
                     '          process immediately, with no chance to clean up.</li>\n'
                     '    </ul>\n'
                     '    <p>\n'
                     '      The universal pattern is TERM, wait briefly, then KILL only if still '
                     'alive. Reaching\n'
                     '      for KILL first leaves temp files and half-written state behind.\n'
                     '    </p>',
             'seen': "<code>supervise.sh</code>'s <code>kill_tree</code>.",
             'gloss': 'Sends a signal. A negative PID targets the process group; <code>-0</code> '
                      'only probes; TERM asks, KILL cannot be refused.'},
            {'id': 'p-wait',
             'sig': 'wait "$pid"',
             'name': 'Reaping a child',
             'body': '<p>\n'
                     '      Note what it cannot do here: because it blocks, it is useless for '
                     'monitoring. veri\n'
                     '      calls it only <em>after</em> deciding the leaf is done, purely to '
                     'clean up. Detecting\n'
                     '      completion has to happen another way — see\n'
                     '      <a href="#supervise">how supervise.sh detects completion</a>.\n'
                     '    </p>',
             'seen': '<code>supervise.sh</code>, one line, after the watch loop ends.',
             'gloss': 'Blocks until a background process finishes and clears its zombie entry. '
                      'Useless for monitoring, precisely because it blocks.'}]}]
