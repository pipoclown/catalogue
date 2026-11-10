# Definition of done

A change to the catalogue is done when all of these are true. Not most of them.

1. `python build.py` ends in `BUILD OK` on a clean checkout.
2. Every new behaviour has a test that failed before the change.
3. The owner in `CODEOWNERS` has reviewed it.
4. Configuration that differs between environments comes from the environment,
   never from an edit to the code.
5. The service still answers `/health` and `/version` after the change.
6. The person who made the change knows how to tell it works in production.
