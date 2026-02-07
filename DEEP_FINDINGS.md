# Deep Analysis Findings: "Money Loose" & Vulnerabilities

## Executive Summary
This report identifies critical areas in the codebase that could lead to financial loss ("money loose"), security bypasses, and server-side impact. The analysis focused on native libraries (`.so`) and Java bytecode (`.dex`), specifically looking for payment verification logic, internal currency handling, and debug features.

## 1. "Money Loose" Scenarios (Financial Loss)

**Root Cause:** Client-side trust and potential bypass of receipt verification.

*   **Mechanism:** The application appears to handle "costCoin" deduction and payment success callbacks (`onSuccess`) within the client-side code (`classes9.dex` and `libsud.so`).
*   **Vulnerability:**
    *   **Logic:** The presence of `shouldVerifyChecksum` and `VerifyChecksum` in `libsud.so` (V8 context) alongside `payment gateway capabilities` suggests that verification might be implemented in JavaScript or native code that can be manipulated.
    *   **Attack Vector:** An attacker could hook the `onSuccess` callback or `verifyReceipt` function to return `true` without actually contacting the server or validating a purchase.
*   **Estimated Success Rate: Medium-High**. If the server relies on the client to report "I successfully paid," bypassing the client-side check results in free items (money loss for the developer).

## 2. Face Verification Bypass

**Root Cause:** Leftover debug features in production code.

*   **Mechanism:** `libCNamaSDK.so` (FaceUnity) contains symbols like `fuCheckDebugItem`, `fuEnableDofDebug`, and `duk_debugger_attach`.
*   **Vulnerability:**
    *   **Logic:** The code checks for debug items. If a specific "debug item" is loaded or if `debugMode` is enabled via `classes9.dex` (`nativeSetDebugMode`), the strict liveness checks (face verification) might be skipped or relaxed.
    *   **Attack Vector:** Enabling `debugMode` in the app (e.g., via modifying shared preferences or hooking `isDebugMode`) could allow an attacker to bypass face verification using static images or video injection.
*   **Estimated Success Rate: High**. Debug features are often designed specifically to bypass checks for testing.

## 3. Server Impact & API Risks

**Root Cause:** Exposed endpoints and potential key leakage.

*   **Mechanism:** `libmo-im-core.so` and `libsud.so` contain logic for signing requests (`CMS_SignerInfo_sign`, `EVP_DigestSignInit`).
*   **Vulnerability:**
    *   **Hardcoded Keys:** The analysis found several long hexadecimal strings and "potential secrets" in the binary. If any of these are private keys used for signing API requests, an attacker could forge requests to the server.
    *   **API Abuse:** Extracted URLs (though standard ones were found in the sample) and the `QMUIWebviewBridge` implementation suggest an API surface that can be fuzz-tested. The `getSupportedCmdList` function in `classes9.dex` reveals that the native app exposes a list of commands to the WebView. Enumerating these could reveal administrative or debug commands.
*   **Estimated Success Rate: Low-Medium**. Depends on whether the extracted strings are actual private keys or just public keys/offsets.

## 4. Internal Currency manipulation

**Root Cause:** Client-side currency logic.

*   **Mechanism:** `classes9.dex` explicitly mentions `costCoin` and `EXT_COSTCOIN`.
*   **Vulnerability:**
    *   **Logic:** If `costCoin` is a method that calculates the price or deducts balance locally before syncing, it can be manipulated.
    *   **Attack Vector:** Hooking `costCoin` to always return `0` or hooking the balance check to always return a high value.
*   **Estimated Success Rate: Medium**. Most modern apps verify balance on the server, but the presence of extensive client-side logic suggests some level of trust or offline capability.

## Recommendations for Developer
1.  **Move Verification Server-Side:** Ensure *all* payment receipts and currency deductions are verified strictly on the server. The client should only receive the new balance, not calculate it.
2.  **Strip Debug Symbols:** Recompile native libraries (`libCNamaSDK.so`, etc.) with all debug symbols and features (`fuCheckDebugItem`) stripped/disabled.
3.  **Obfuscate Logic:** Use stronger obfuscation for `classes.dex` to hide `costCoin` and payment callback methods.
4.  **Key Rotation:** If any of the found hex strings are active keys, rotate them immediately and move signing logic to a secure backend or Trusted Execution Environment (TEE).

## Tooling Used
A custom Python script `analyze.py` was used to perform deep static analysis, context extraction, and secret hunting on the provided binaries.
