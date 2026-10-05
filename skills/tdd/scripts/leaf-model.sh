#!/bin/sh
# leaf-model.sh — say which model one leaf runs on: a shim over veri/leaf_model.py.
#
# usage: leaf-model.sh <leaf-name>
#        VERI_MODEL=<x> leaf-model.sh <leaf-name>          every leaf
#        VERI_MODEL_DEVELOPER=<x> leaf-model.sh <leaf-name> develop-* and revise-*, beating VERI_MODEL
#        VERI_MODEL_VERIFIER=<x> leaf-model.sh <leaf-name>  verify-*, beating VERI_MODEL
# Exit:  0 the model on stdout, or nothing when none is set; 2 no leaf name, a name leaf-role.sh
#        refuses, or a model value containing whitespace
exec python3 "$(dirname "$0")/veri/leaf_model.py" "$@"
