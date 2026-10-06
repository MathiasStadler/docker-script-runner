#!/usr/bin/env python3
# Führt 10_secdef_info_pipe.py für alle PUT-Strikes aus und schreibt CSV

import sys
import json
import subprocess
import csv
from datetime import datetime

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 script.py <underConid> <month> [exchange]")
        sys.exit(1)
    
    under_conid = sys.argv[1]
    month = sys.argv[2]
    exchange = sys.argv[3] if len(sys.argv) > 3 else "SMART"
    
    # 1. Strikes holen via 09_secdef_strikes_pipe.py
    strikes_input = f"{under_conid} {month} {exchange}"
    result = subprocess.run(
        ["python3", "/home/hermes/docker-script-runner/src/09_secdef_strikes_pipe.py"],
        input=strikes_input,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error getting strikes: {result.stderr}")
        sys.exit(1)
    
    try:
        strikes_data = json.loads(result.stdout.strip())
    except json.JSONDecodeError:
        print(f"Invalid JSON from strikes: {result.stdout}")
        sys.exit(1)
    
    if "error" in strikes_data:
        print(f"API error: {strikes_data['error']}")
        sys.exit(1)
    
    put_strikes = strikes_data.get("put", [])
    if not put_strikes:
        print("No PUT strikes found")
        sys.exit(1)
    
    print(f"Found {len(put_strikes)} PUT strikes, fetching contract info...")
    
    # 2. Für jeden PUT-Strike 10_secdef_info_pipe.py aufrufen
    all_contracts = []
    for strike in put_strikes:
        info_input = f"{under_conid} {month} {strike} P {exchange}"
        result = subprocess.run(
            ["python3", "/home/hermes/docker-script-runner/src/10_secdef_info_pipe.py"],
            input=info_input,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            try:
                contracts = json.loads(result.stdout.strip())
                if isinstance(contracts, list):
                    all_contracts.extend(contracts)
            except json.JSONDecodeError:
                pass
    
    # 3. CSV schreiben
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_file = f"/home/hermes/docker-script-runner/src/option_contracts_{under_conid}_{month}_{timestamp}.csv"
    
    headers = ["conid", "symbol", "strike", "maturityDate", "right"]
    
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for contract in all_contracts:
            if "error" not in contract:
                writer.writerow({h: contract.get(h, "") for h in headers})
    
    print(f"CSV written: {csv_file}")
    print(f"Total contracts: {len(all_contracts)}")
    print(csv_file)  # Pfad als letzte Zeile für einfache Weiterverarbeitung

if __name__ == "__main__":
    main()