# V0 Universe Selection Rule

**Status:** Not frozen yet.

The 20-stock V0 universe must be selected mechanically and committed before B001
results are viewed.

The rule and thresholds remain pending until the data-validation and universe
selection step in Phase 1.

Before the 20-symbol list is frozen, run the corporate-action parser over the
full intended research window for every candidate symbol. Exclude any candidate
with an `UNSUPPORTED` corporate action inside that window unless deterministic
support is added before universe selection.

The universe-freeze artifact must report:

- candidate count before this exclusion;
- symbols excluded by unsupported corporate actions;
- excluded action purposes and dates;
- candidate count after this exclusion.

Every V0 report must label both known universe biases:

```text
SURVIVORSHIP-BIASED: YES
POINT-IN-TIME UNIVERSE: NO
UNSUPPORTED-CORPORATE-ACTION FILTER: YES
```

Liquidity ranking must use raw traded value, or raw close multiplied by raw
volume if no reliable raw traded-value field is available.
