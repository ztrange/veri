"""In-process cases for veri/seam_contract.py, the stages' seam contracts (PRD 038.1 SC5, #4342)."""
import importlib


def test_each_record_stage_owes_the_keys_its_next_stage_reads_with_no_committed_source_4342():
    seam_contract = importlib.import_module("veri.seam_contract")
    assert seam_contract.CONTRACTS == {"red-half": ("test_path", "target_test"), "green-half": ("test_path",),
                                       "refactor-half": ()}
    assert seam_contract.READS == {"green-half": ("red-half",), "revise": ("red-half",), "reroute": ("red-half",),
                                   "refactor-half": ("green-half", "red-half"),
                                   "step-close": ("refactor-half",)}
