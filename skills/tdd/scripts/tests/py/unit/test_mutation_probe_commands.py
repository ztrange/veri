"""The verifier's probe commands never use a suffixless `sed -i`, which BSD sed misreads."""
import re
from pathlib import Path

import pytest
from veri import mutation_probe

SCRIPTS = Path(mutation_probe.__file__).resolve().parent.parent
SUFFIXLESS_SED_I = re.compile(r"\bsed\s+(?:-\w+\s+)*-i(?=\s|$)")


@pytest.mark.tree_audit("every prompt template")
def test_no_prompt_template_or_mutation_probe_source_uses_sed_i_without_a_backup_suffix():
    sources = sorted((SCRIPTS / "prompts").rglob("*.md")) + [SCRIPTS / "veri" / "mutation_probe.py"]
    assert len(sources) > 2
    offenders = [
        f"{path.name}: {line.strip()}"
        for path in sources
        for line in path.read_text().splitlines()
        if SUFFIXLESS_SED_I.search(line)
    ]
    assert offenders == []
