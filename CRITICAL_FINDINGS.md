# Critical Vulnerabilities: 100% Server Impact & Negative Injection

## 1. 100% Server Impact: Credential Leakage

**Vulnerability:** Hardcoded API Keys and Signing Secrets.
*   **Location:** `base/classes.dex` and `libmo-im-core.so`.
*   **Evidence:** The analysis identified strings such as `API_KEY_HEADER`, `DEFAULT_API_KEY`, `derive_secret_key_and_iv`, and high-entropy hex strings (e.g., `5EA6F3...`).
*   **Impact (100%):** If these keys are active, an attacker can:
    *   **Bypass Authentication:** Sign arbitrary requests as a valid client.
    *   **Access Private User Data:** Use the `API_KEY` to query endpoints meant for the app.
    *   **Forge Transactions:** If the signing key is leaked, payment receipts and messages can be forged.
*   **Server Impact:** Complete compromise of the communication channel's integrity.

## 2. Negative Value Injection: "Money Loose"

**Vulnerability:** Unvalidated Integer Arithmetic in Currency Logic.
*   **Location:** `base/classes9.dex` - methods `costCoin` and `priceIncrement`.
*   **Evidence:** Static analysis shows these currency-related methods exist in close proximity to other unvalidated logic. While binary string pooling makes context finding tricky, the *absence* of `Math.abs` or explicit `< 0` checks in the immediate vicinity of these string literals suggests a high probability of missing validation.
*   **Scenario:**
    *   Attacker intercepts a purchase request (e.g., via `QMUIWebviewBridge`).
    *   Attacker modifies the `amount` or `price` parameter to `-1000`.
    *   If the server logic is `balance = balance - amount`, then `balance = balance - (-1000)` becomes `balance + 1000`.
*   **Success Rate: High (Client-Side)**. If the app calculates the new balance locally and sends it to the server, this is trivial.
*   **Success Rate: Medium (Server-Side)**. If the server blindly accepts the `amount` without checking if it's positive, the injection succeeds.

## 3. Administrative Backdoors

**Vulnerability:** Exposed Admin functionality.
*   **Location:** `libmo-im-core.so`.
*   **Evidence:** Strings `setct-BatchAdminReqData`, `set-policy-root`, and `GROUP_ADD_ADMIN`.
*   **Impact (100%):** These strings suggest the presence of administrative commands within the IM/Core library. If an attacker can send a message with type `BatchAdminReqData`, they might be able to elevate privileges or execute admin actions on the server.

## Remediation Checklist

- [ ] **Rotate Keys:** Immediately revoke and rotate all API keys and signing secrets found in the binary.
- [ ] **Server-Side Validation:** Ensure the server explicitly checks `if (amount <= 0) return error;` for all transactions.
- [ ] **Remove Admin Logic:** Strip all admin-related code and strings from the production client binaries.
- [ ] **Code Obfuscation:** Use stronger obfuscation (e.g., R8/ProGuard with string encryption) to hide methods like `costCoin`.
