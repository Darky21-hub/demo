#!/usr/bin/env python3
# verify_pi_operation.py
# Usage: python verify_pi_operation.py <operation_id> [api_base]

import sys, os, requests, json


def get(url, timeout=15):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.json()


def main():
    if len(sys.argv) < 2:
        print("Usage: python verify_pi_operation.py <operation_id> [api_base]")
        sys.exit(2)

    op_id = sys.argv[1]
    api_base = sys.argv[2] if len(sys.argv) > 2 else os.getenv("API_BASE", "https://api.mainnet.minepi.com")

    op_url = f"{api_base}/operations/{op_id}"
    print(f"Fetching operation: {op_url}")
    op = get(op_url)

    print("\nOperation summary:")
    summary = {
        "id": op.get("id"),
        "type": op.get("type"),
        "created_at": op.get("created_at"),
        "transaction_successful": op.get("transaction_successful"),
        "transaction_hash": op.get("transaction_hash"),
        "funder": op.get("funder") or op.get("source_account"),
        "account": op.get("account"),
        "starting_balance": op.get("starting_balance")
    }
    print(json.dumps(summary, indent=2))

    tx_hash = op.get("transaction_hash")
    if tx_hash:
        tx = get(f"{api_base}/transactions/{tx_hash}")
        print("\nTransaction summary:")
        print(json.dumps({
            "hash": tx.get("hash"),
            "successful": tx.get("successful"),
            "ledger": tx.get("ledger"),
            "created_at": tx.get("created_at"),
            "operations": tx.get("operations")
        }, indent=2))
        print("\nHash match:", tx.get("hash") == tx_hash)
    else:
        print("\nNo transaction_hash found on operation.")

    effects = get(f"{api_base}/operations/{op_id}/effects")
    records = effects.get("_embedded", {}).get("records", [])
    print("\nEffects count:", len(records))

    account = summary.get("account")
    if account:
        acct = get(f"{api_base}/accounts/{account}")
        native_balance = None
        for b in acct.get("balances", []):
            if b.get("asset_type") == "native":
                native_balance = b.get("balance")
        print("\nAccount summary:")
        print(json.dumps({
            "account": acct.get("account_id") or acct.get("id"),
            "sequence": acct.get("sequence"),
            "native_balance": native_balance,
            "num_signers": len(acct.get("signers", []))
        }, indent=2))
        print("\nStarting balance (operation):", summary.get("starting_balance"))
        print("Current native balance:", native_balance)
    else:
        print("\nNo account id available in operation to fetch account details.")


if __name__ == "__main__":
    main()
