import os
import subprocess
import re

# Focused keywords for Critical Impact
KEYWORDS = [
    "admin", "root", "backdoor", "superuser", # Server impact
    "refund", "chargeback", "withdraw", # Negative value logic
    "Math.abs", "< 0", "<= 0", "negative", # Validation checks
    "costCoin", "addCoin", "updateBalance", # Currency methods
    "unsigned", "int32", "int64", # Data types (overflow potential)
    "api_key", "secret_key", "access_token" # Credentials
]

# Regex for integer/value handling patterns
NEGATIVE_CHECK_PATTERN = re.compile(r'(if|while)\s*\(.*[<>=!]+\s*0.*\)')
SIGNED_INT_PATTERN = re.compile(r'(int|long)\s+[a-zA-Z0-9_]+')

def analyze_critical_file(filepath):
    print(f"\n{'='*20} Critical Analysis: {filepath} {'='*20}")

    try:
        # Run strings command
        result = subprocess.run(['strings', filepath], capture_output=True, text=True, errors='ignore')
        if result.returncode != 0:
            print(f"Error running strings: {result.stderr}")
            return

        lines = result.stdout.split('\n')

        print("\n--- Potential Negative Value / Overflow Logic ---")
        for i, line in enumerate(lines):
            # Check for currency methods near validation logic
            if any(k in line for k in ["costCoin", "addCoin", "balance", "price", "amount"]):
                # Look at context for validation
                context_range = lines[max(0, i-5):min(len(lines), i+5)]

                # Check if "abs" or "< 0" is MISSING in the context of a money operation
                has_validation = False
                for c_line in context_range:
                    if "abs" in c_line.lower() or "< 0" in c_line or "negative" in c_line.lower():
                        has_validation = True
                        break

                if not has_validation:
                     print(f"Potential UNVALIDATED money op: {line.strip()}")
                     # Print context for manual verification
                     for c_line in context_range:
                         print(f"  > {c_line.strip()}")
                     print("-" * 20)

        print("\n--- Server Impact Indicators (Admin/Backdoor) ---")
        for line in lines:
            if any(k in line.lower() for k in ["admin", "root", "backdoor", "superuser"]):
                print(f"Risk: {line.strip()}")

        print("\n--- Credential Leaks (100% Impact) ---")
        for line in lines:
             if any(k in line.lower() for k in ["api_key", "secret_key", "access_token"]):
                 print(f"Leak Candidate: {line.strip()}")


    except Exception as e:
        print(f"Exception analyzing {filepath}: {e}")

def main():
    # Targeted files for critical analysis
    target_files = [
        "./base/classes9.dex", # Currency logic
        "./base/classes.dex",  # Core logic
        "./split_config.arm64_v8a/lib/arm64-v8a/libmo-im-core.so", # Network/Crypto
         "./split_config.arm64_v8a/lib/arm64-v8a/libsud.so" # Payment
    ]

    for filepath in target_files:
        if os.path.exists(filepath):
            analyze_critical_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()
