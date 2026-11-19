# Defect Report Template

Copy this into a new `DEF-NNN_short-title.md` file for each defect found during test
execution. One file per defect.

---

**Defect ID:** DEF-NNN
**Title:**
**Reported by:** (tester)
**Date found:**
**Found via:** (TC ID from `../test-cases/Test_Cases.csv`, or manual/exploratory)
**Module:** (M1-M9)
**Rule ID(s) affected:**
**Severity:** Critical / High / Medium / Low
**Priority:** P1 / P2 / P3
**Environment:** `APP_ENV=test`, `FIXED_NOW=2026-11-10T09:00:00`, commit `<hash>`

## Summary

One or two sentences: what's wrong.

## Steps to reproduce

1. ...
2. ...

## Expected result

## Actual result

## Evidence

Screenshot(s) in `../evidence/screenshots/`, relevant log excerpt, etc.

## Root cause

(Filled in once diagnosed.)

## Fix

(File(s) changed, commit hash.)

## Status

Open / Fixed / Verified / Closed
