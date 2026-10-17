# Runbook: Admitting a System

1. Open a work package in `04-work-packages/` describing the system.
2. Create `02-systems/<system-name>/` with the four focus-area folders.
3. Add the system artifact (type: system) to `2.2-architecture/`,
   binding its interfaces and standards by id.
4. Run `python3 00-meta-model/verify.py` and open the pull request.
   CODEOWNERS routes ratification to the owning architects.
