# Phase 3: Order Validation Core — Technical Explanation

## Why `payment_terms` was pulled out of OV-001 entirely

The spec text is internally contradictory: §6 Rule OV-001 lists `payment_terms` among the fields that "must not be empty" (implying Error severity, since every other OV-001 example is `Error`), while §6 Rule OV-007 separately covers the identical blank-`payment_terms` case with its own code and an explicit `Warning` severity in the §8 example table. Following both literally would mean a row with only a blank `payment_terms` gets flagged as both an Error (OV-001) and a Warning (OV-007) simultaneously — which contradicts the decision that Warning-only rows should remain in `valid_orders`. Since a row *is* disqualified the moment it has any Error, "blank payment_terms is Error via OV-001" and "blank payment_terms never disqualifies a row" cannot both be true. OV-007 was kept as the sole owner of this field because it's the more specific, deliberately-authored rule (it has its own number, its own example, and an explicit non-Error severity), while OV-001's required-fields list is the more generic, block-copied list where the conflict likely originated.

## Why blank fields skip their type/value rules instead of double-flagging

Rules OV-002 through OV-006 are "value quality" rules — they only make sense to evaluate when a value exists. Before this decision, an empty `priority` cell could produce *two* errors: `OV-001` ("Priority is missing.") *and* `OV-006` ("Priority must be High, Normal, or Low.") for the same underlying problem, because an empty string is also not one of `{High, Normal, Low}`. That's noise, not more information — the user needs to know the cell is empty exactly once, not twice under different rule numbers. The same logic applies to a blank `order_id` and OV-002 (nothing to compare for duplicates) and blank `sku`/`quantity`/dates and their respective rules.

## Why quantity parsing has three branches (int/float, numpy-ish, and string-coercible)

Excel cells arrive through `pandas.read_excel` in different underlying types depending on how the source cell was formatted: a genuinely numeric column reads back as `numpy.int64`/`numpy.float64`, but a column that mixes types (as any single `pd.Series` built from `df.iterrows()` does, since each row becomes an `object`-dtype `Series` spanning differently-typed columns) can hand back a boxed scalar that doesn't cleanly match `isinstance(value, (int, float))`. Rather than special-case every numpy scalar type, `_parse_quantity` falls through to `float(str(value).strip())` as a catch-all — this handles `numpy.int64`, `numpy.float64`, and genuine text like `"ten"` (which fails to parse and correctly reports "must be a valid whole number") through the same code path, without needing a numpy import.

## Why `active` string normalization checks `str(value).lower()` even for real booleans

`numpy.bool_` (what a boolean Excel column round-trips to inside an object-dtype row `Series`) is not a subtype of Python's `bool` in Python 3, so `isinstance(value, bool)` silently fails to catch it. Rather than importing numpy just to check `isinstance(value, np.bool_)` too, `_normalize_active` falls through to the same string-matching branch used for literal `"TRUE"`/`"FALSE"` cells — `str(numpy.bool_(True))` renders as `"True"`, which lowercases to `"true"` and matches the truthy-string set. One code path handles real Python `bool`, `numpy.bool_`, and spec-allowed string values identically.

## Why `invalid_orders` is computed from a distinct-row set, not summed from category counts

`duplicate_orders`, `invalid_skus`, and `missing_field_count` are each simple counts of matching `ValidationErrorRow` entries — but a single row can trigger more than one rule (e.g. a duplicate `order_id` on a row that also references an unknown SKU). Summing category counts to get `invalid_orders` would double-count that row. Instead, `invalid_orders` is the size of a `set` of `row_number`s that have at least one Error-severity entry, computed once during the per-row pass, independent of how many different rules that row happened to violate.

## Why error ordering is fixed at `(row_number, rule_order, ov001_field_order)`

`validate_orders` builds the error list by iterating rows and, within each row, evaluating rules in source order (OV-001 through OV-007) — this already produces the right order in the common case. The explicit `_sort_key`/`.sort()` pass exists as a guarantee, not an optimization: it makes the ordering a tested contract (`test_errors_are_ordered_by_row_then_rule_then_field`) rather than an implementation accident that could silently shift if the per-row rule evaluation order in `_validate_row` is ever reordered during a refactor.
