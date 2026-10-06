#!/usr/bin/env python3
# ib_insync Pipeline (TWS Socket only): Symbol -> gefilterte PUT-Optionen mit Delta -0.50 bis -0.10 + Greeks + Volume
# Usage: python3 tws_pipeline.py <SYMBOL> [MONTH_INDEX] [EXCHANGE]

import sys
import csv
import logging
from datetime import datetime
from ib_insync import IB, Stock, Option, util

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s : %(message)s')
logger = logging.getLogger(__name__)

HEADERS = [
    "conid", "symbol", "right", "expiration", "strike", "multiplier",
    "bid", "ask", "last", "close", "volume",
    "delta", "gamma", "theta", "vega", "impliedVol",
    "bidSize", "askSize", "high", "low", "openPrice"
]


def connect_ib(client_id=1):
    """Connect to TWS/Gateway."""
    ib = IB()
    ib.connect('127.0.0.1', 7496, clientId=client_id, timeout=15, readonly=True)
    # Paper account: use delayed-frozen data (type 4)
    ib.reqMarketDataType(4)
    return ib


def get_stock_and_chain(ib, symbol, month_index=0, exchange='SMART'):
    """Get stock data and option chain for specific expiration."""
    stock = Stock(symbol, exchange, 'USD')
    ib.qualifyContracts(stock)
    
    # Get option chain parameters
    chains = ib.reqSecDefOptParams(stock.symbol, '', stock.secType, stock.conId)
    chain = [c for c in chains if c.exchange == exchange]
    if not chain:
        raise ValueError(f"No chain found for exchange {exchange}")
    chain = chain[0]
    
    if month_index >= len(chain.expirations):
        raise ValueError(f"Month index {month_index} out of range (max {len(chain.expirations)-1})")
    
    expiration = chain.expirations[month_index]
    logger.info(f"Chain: {chain.tradingClass}, Expiration: {expiration}, Strikes: {len(chain.strikes)}")
    
    return stock, chain, expiration


def get_stock_data(ib, stock):
    """Get underlying stock price."""
    ticker = ib.reqMktData(stock, '', False, False)
    ib.sleep(2)
    
    data = {
        'conid': stock.conId,
        'symbol': stock.symbol,
        'bid': ticker.bid,
        'ask': ticker.ask,
        'last': ticker.last,
        'close': ticker.close,
        'volume': ticker.volume,
        'high': ticker.high,
        'low': ticker.low,
    }
    ib.cancelMktData(stock)
    return data


def get_valid_put_options(ib, symbol, expiration, chain, exchange='SMART'):
    """Create put options and filter to only valid (qualified) ones."""
    options = []
    for strike in chain.strikes:
        opt = Option(symbol, expiration, strike, 'P', exchange, tradingClass=chain.tradingClass, multiplier=chain.multiplier)
        options.append(opt)
    
    ib.qualifyContracts(*options)
    # Filter out contracts that failed to qualify (conId=0 or no contract)
    valid = [o for o in options if o.conId and o.conId > 0]
    logger.info(f"Qualified {len(valid)} of {len(options)} put options for {expiration}")
    return valid


def fetch_option_greeks(ib, options):
    """Fetch market data and Greeks for all options."""
    results = []
    for opt in options:
        ticker = ib.reqMktData(opt, '', False, False)
        ib.sleep(0.3)  # Small delay between requests
        
        greeks = ticker.modelGreeks
        row = {
            'conid': opt.conId,
            'symbol': opt.symbol,
            'right': opt.right,
            'expiration': opt.lastTradeDateOrContractMonth,
            'strike': opt.strike,
            'multiplier': opt.multiplier,
            'bid': ticker.bid,
            'ask': ticker.ask,
            'last': ticker.last,
            'close': ticker.close,
            'volume': ticker.volume,
            'bidSize': ticker.bidSize,
            'askSize': ticker.askSize,
            'high': ticker.high,
            'low': ticker.low,
            'openPrice': ticker.open,
        }
        
        if greeks:
            row['delta'] = greeks.delta
            row['gamma'] = greeks.gamma
            row['theta'] = greeks.theta
            row['vega'] = greeks.vega
            row['impliedVol'] = greeks.impliedVol
        else:
            row['delta'] = row['gamma'] = row['theta'] = row['vega'] = row['impliedVol'] = None
        
        results.append(row)
        ib.cancelMktData(opt)
    
    return results


def filter_by_delta(rows, min_delta=-0.50, max_delta=-0.10):
    """Filter puts by delta range."""
    filtered = []
    for r in rows:
        if r['delta'] is not None:
            if min_delta <= r['delta'] <= max_delta:
                filtered.append(r)
    return filtered


def write_csv(rows, filepath):
    """Write results to CSV."""
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writeheader()
        for r in rows:
            out_row = {}
            for h in HEADERS:
                val = r.get(h)
                if isinstance(val, float):
                    out_row[h] = f'{val:.6f}' if val != 0 else '0'
                else:
                    out_row[h] = val if val is not None else ''
            writer.writerow(out_row)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 tws_pipeline.py <SYMBOL> [MONTH_INDEX] [EXCHANGE]")
        sys.exit(1)
    
    symbol = sys.argv[1].upper()
    month_index = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    exchange = sys.argv[3] if len(sys.argv) > 3 else 'SMART'
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"/home/hermes/docker-script-runner/src/tws_option_contracts_{symbol}_{timestamp}.csv"
    
    logger.info(f"Starting pipeline for {symbol} (month_index={month_index}, exchange={exchange})")
    
    ib = None
    try:
        # 1. Connect to TWS
        ib = connect_ib()
        logger.info(f"Connected to TWS, server version: {ib.client.serverVersion()}")
        
        # 2. Get stock and option chain
        stock, chain, expiration = get_stock_and_chain(ib, symbol, month_index, exchange)
        
        # 3. Get stock price
        stock_data = get_stock_data(ib, stock)
        logger.info(f"Stock: {stock.symbol} @ {stock_data['last'] or stock_data['close']}")
        
        # 4. Get valid PUT options
        options = get_valid_put_options(ib, symbol, expiration, chain, exchange)
        
        # 5. Fetch Greeks via TWS
        logger.info(f"Fetching market data and Greeks for {len(options)} options...")
        rows = fetch_option_greeks(ib, options)
        
        # 6. Filter by delta
        filtered = filter_by_delta(rows)
        logger.info(f"Delta filter (-0.50 to -0.10): {len(filtered)} of {len(rows)} contracts")
        
        # 7. Write CSV
        write_csv(filtered, csv_file)
        logger.info(f"CSV written: {csv_file}")
        
        # Print summary
        print(f"\n=== RESULT: {len(filtered)} PUT options with delta -0.50 to -0.10 ===")
        print(f"File: {csv_file}")
        print(f"Underlying: {symbol} @ {stock_data['last'] or stock_data['close']}")
        print(f"Expiration: {expiration}")
        print()
        for r in filtered:
            print(f"  Strike {r['strike']}: delta={r['delta']:.4f}, bid={r['bid']}, ask={r['ask']}, vol={r['volume']}, iv={r['impliedVol']:.4f}")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        sys.exit(1)
    finally:
        if ib and ib.isConnected():
            ib.disconnect()


if __name__ == '__main__':
    main()