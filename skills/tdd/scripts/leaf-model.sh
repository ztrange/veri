#!/bin/sh
# leaf-model.sh — say which model one leaf runs on: a shim over veri/leaf_model.py.
#
# usage: leaf-model.sh <leaf-name>
#        VERI_MODEL=<x> leaf-model.sh <leaf-name>          every leaf
#        VERI_MODEL_DEVELOPER=<x> leaf-model.sh <leaf-name> develop-* and revise-*, beating VERI_MODEL
#        VERI_MODEL_REVISE=<x> leaf-model.sh <leaf-name>    revise-* and develop-exhausted, beating VERI_MODEL_DEVELOPER
#        VERI_MODEL_VERIFIER=<x> leaf-model.sh <leaf-name>  verify-*, beating VERI_MODEL
# Exit:  0 the model on stdout (sonnet, or opus for revise-* and develop-exhausted, when none is set); 2 no leaf name, a name leaf-role.sh
#        refuses, or a model value containing whitespace
py="${VERI_VENV:-$HOME/.veri-tools/venv}/bin/python3"
[ -x "$py" ] || py=python3
exec "$py" "$(dirname "$0")/veri/leaf_model.py" "$@"
