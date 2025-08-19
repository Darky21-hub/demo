#!/usr/bin/env node
// verify_pi_operation.js
// Usage: node verify_pi_operation.js <operation_id> [api_base]
// Requires Node.js 18+ (global fetch). If using older Node, install node-fetch and adjust.

const [,, opId, apiBaseArg] = process.argv;
if (!opId) { console.error("Usage: node verify_pi_operation.js <operation_id> [api_base]"); process.exit(2); }
const API_BASE = apiBaseArg || process.env.API_BASE || "https://api.mainnet.minepi.com";

async function getJson(url){
  const res = await fetch(url, { method: 'GET' });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} ${url}`);
  return res.json();
}

(async()=>{
  try {
    const op = await getJson(`${API_BASE}/operations/${opId}`);
    const summary = {
      id: op.id,
      type: op.type,
      created_at: op.created_at,
      transaction_successful: op.transaction_successful,
      transaction_hash: op.transaction_hash,
      funder: op.funder || op.source_account,
      account: op.account,
      starting_balance: op.starting_balance
    };
    console.log("Operation summary:", summary);

    if (summary.transaction_hash) {
      const tx = await getJson(`${API_BASE}/transactions/${summary.transaction_hash}`);
      console.log("Transaction summary:", { hash: tx.hash, successful: tx.successful, ledger: tx.ledger, created_at: tx.created_at });
      console.log("Hash match:", tx.hash === summary.transaction_hash);
    } else {
      console.log("No transaction_hash found on operation.");
    }

    const effects = await getJson(`${API_BASE}/operations/${opId}/effects`);
    const effectsCount = (effects._embedded && effects._embedded.records || []).length;
    console.log("Effects count:", effectsCount);

    if (summary.account) {
      const acct = await getJson(`${API_BASE}/accounts/${summary.account}`);
      const nativeBal = (acct.balances||[]).find(b=>b.asset_type==="native")?.balance || null;
      console.log("Account summary:", { account: acct.account_id || acct.id, sequence: acct.sequence, native_balance: nativeBal, num_signers: (acct.signers||[]).length });
      console.log("Starting balance (operation):", summary.starting_balance);
      console.log("Current native balance:", nativeBal);
    } else {
      console.log("No account id available in operation to fetch account details.");
    }
  } catch (err) {
    console.error("Error:", err.message);
    process.exit(1);
  }
})();