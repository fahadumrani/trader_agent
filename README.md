# Crypto Sentinel Pro — Live UI Edition

Self-learning Kaggle paper-trading notebook with a live dashboard and GitHub persistence.

## Dashboard shows
- Total virtual equity, available cash, net P/L and drawdown
- Current open position with entry, live price, stop, target and unrealized P/L
- BTC/ETH/SOL live prices, scores, regimes and model confidence
- Latest agent action
- Recent completed trades with BUY price, SELL price and P/L
- Price/EMA chart with green BUY and red SELL markers

## Run on Kaggle
1. Import `crypto_sentinel_live_UI_kaggle.ipynb`.
2. Enable Internet.
3. Optional GitHub sync: attach a Kaggle Secret named `GITHUB_TOKEN` with Contents read/write access to `fahadumrani/trader_agent`.
4. Select **Run → Run All**.
5. Scroll to the final cell. The dashboard appears after the first scan and refreshes after every completed five-minute candle.

## Safety
Paper trading only. Do not commit tokens, wallet seeds, passwords, exchange credentials, or private financial data. Profit is not guaranteed.
