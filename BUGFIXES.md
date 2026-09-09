# Bug fixes

- Corrected GitHub endpoint handling and added default-branch discovery.
- Added retry logic, large-file download fallback, and per-file sync failure isolation.
- Normalized historical timestamps to UTC before merge and deduplication.
- Removed the false label previously assigned to the newest candle.
- Separated completed training labels from the latest inference row.
- Made the learning target fee/slippage aware over a three-candle horizon.
- Corrected AUC tie handling and the labeled-row count used by the gate.
- Selects the highest-scoring learned-ready asset, not merely the overall leader.
- Prevents repeated signal rows for the same processed candle.
- Corrected cooldown timing and added immediate entry/exit checkpoints.
- Added five-error circuit breaking and safe final GitHub sync.
- Corrected final mark-to-market equity reporting for an open position.
