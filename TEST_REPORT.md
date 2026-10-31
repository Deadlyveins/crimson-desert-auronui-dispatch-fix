# v0.5.1 Beta Test Report

October 31, 2026

## Coverage

- Recognizes observed metadata profiles `(1,1,1)`, `(2,2,2)`, `(3,3,3)`, `(4,4,4)` and `(4,4,5)` with supported record layouts.
- Tests unobserved combinations including `(3,4,5)` with explicit additional confirmation before patching.
- Checks both known 56-byte and 64-byte Auronui record layouts and rejects modified fixed record bytes.
- Tests combined Stage 1 plus Stage 2 output, original Stage 1 and Stage 2, save encoding and decoding, and no-overwrite behavior.
- Verifies that invalid, unexpected, or already-zero Stage 1 inputs do not generate a successful repair.

## Local checks performed for this source update

- Twelve automated regression test cases passed on the v0.5.1 source (including multi-profile and both-layout subtests).
- Combined repair, save-authentication and encode/decode roundtrip passed for three private original broken saves: `(3,3,3)`, `(4,4,4)`, and `(4,4,5)`. These files were only read; no player data is included in the package.
- One previously repaired save with a different structure was rejected by preflight as expected.
- Stage 2 applied to a prior Stage 1 output reproduced the decoded bytes of the user-supplied Stage 2 result exactly.

## In-game status

- A combined Stage 1 plus Stage 2 output, without an intermediate game save, successfully reset the dispatch and allowed a new construction timer to start in-game. The v0.5.1 build has also been reported working by the tester.
- Previous independent users have reported successful repairs with the original two-stage method.
- Not every newly accepted numeric combination has been verified in-game. Full quest completion is not established for every case.
- The Windows EXE must be compiled and checked on a Windows system. Source tests are not a substitute for executable or gameplay testing.

Real player save files are **not included** with this repository or public release ZIP.

Run tests after installing requirements:

```powershell
py -3 -m unittest discover -s tests -v
```
