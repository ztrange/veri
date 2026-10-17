# Plan for #1615 — A Red that fails only on an undefined helper in the test file passes verify-red, then tests-frozen makes Green impossible

- [x] The red developer prompt built by build-develop-prompt.sh red states that a helper the test needs is defined in Red, inside the test file, and that a failure caused only by an undefined name in the test file (a NameError, or an ImportError of a name the test file defines nowhere) is not a red ⟦criterion 1⟧
- [x] The red verifier prompt built by build-verify-prompt.sh red tells the verifier to REJECT a red whose only failure is a NameError, or an equivalent undefined-name error, on a name the test file references and never defines or imports ⟦criterion 2⟧ ⟂ refactor pending
