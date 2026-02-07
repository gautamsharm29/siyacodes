# Analysis Findings

## Overview
This report summarizes the static analysis performed on the Android application's native libraries (`.so`) and Dalvik executables (`.dex`). The analysis focused on payment-related logic, internal currency, bypass mechanisms, and face verification.

## Key Findings

### 1. Payment & Currency Logic
- **`libsud.so`**: Contains the string "payment gateway capabilities", suggesting it handles payment processing. It also includes V8 (JavaScript engine) symbols, indicating that payment logic might be partially implemented in JavaScript or dynamically loaded.
- **`libmo-im-core.so`**: Also contains "payment gateway capabilities" and extensive SSL/TLS/Crypto verification logic. This library likely handles secure communication for payments and instant messaging.
- **`classes9.dex`**: Contains references to `costCoin`, `EXT_COSTCOIN`, and `debugMode`. This confirms that internal currency logic exists in the Java/Kotlin layer and interacts with native code.

### 2. Face Verification
- **`libCNamaSDK.so`**: This is the FaceUnity SDK. It contains symbols like `fuCheckDebugItem`, `duk_debugger_attach`, and `duk_debugger_pause`. The presence of Duktape debugger symbols suggests that the face verification logic might be debuggable or susceptible to tampering if debug features are enabled.

### 3. Debug & Bypass Mechanisms
- **Debug Symbols**: Multiple libraries (`libsud.so`, `libCNamaSDK.so`) contain debug-related symbols (`DebugBreak`, `debug_mode`, `isAppDebug`).
- **`classes9.dex`**: explicit references to `nativeSetDebugMode` and `isAppDebug`. If these flags can be manipulated (e.g., via a modified APK or runtime injection), it might be possible to bypass checks.
- **WebView Bridge**: `QMUIWebviewBridge.js` exposes a bridge for WebView communication. The `getSupportedCmdList` command in `classes9.dex` suggests that the native side exposes a list of supported commands, which could be enumerated to find hidden functionality.

### 4. V8 & Duktape Runtimes
- The application embeds two different JavaScript engines:
    - **V8** (in `libsud.so`): Likely for general app logic or payment processing.
    - **Duktape** (in `libCNamaSDK.so`): Likely for face effects or logic within the FaceUnity SDK.
- The presence of these engines increases the attack surface, as vulnerabilities in the JS engines or the bridge implementation could be exploited.

## Recommendations for Further Investigation
1.  **Dynamic Analysis**: Attempt to enable `debugMode` by hooking `nativeSetDebugMode` or modifying the APK manifest/smali.
2.  **Traffic Interception**: Monitor network traffic for "payment gateway" communications to understand the protocol.
3.  **Bridge Fuzzing**: Send various commands via `QMUIWebviewBridge` to identify undocumented or vulnerable handlers.
4.  **Face Verification Bypass**: Investigate `fuCheckDebugItem` in `libCNamaSDK.so` to see if it can be used to disable liveness checks.

## Tooling
A Python script `analyze.py` was created to perform this static analysis. It searches for keywords and dumps symbols from `.so` files. The full output is available in `analysis_report.txt`.
