import os
import subprocess
import re

# Extended keywords for deeper analysis
KEYWORDS = [
    "pay", "coin", "diamond", "bypass", "verify", "mock",
    "debug", "cheat", "coupon", "vip", "purchase", "gem", "gold",
    "token", "sign", "secret", "key", "auth", "admin", "test",
    "onSuccess", "onFailure", "callback", "order", "receipt"
]

# Regex patterns
URL_PATTERN = re.compile(r'https?://[^\s"\']+')
KEY_PATTERN = re.compile(r'(?<![A-Za-z0-9])[A-Za-z0-9]{32,}(?![A-Za-z0-9])') # 32+ char alphanumeric
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def analyze_file(filepath):
    print(f"\n{'='*20} Analyzing: {filepath} {'='*20}")

    try:
        # Run strings command
        result = subprocess.run(['strings', filepath], capture_output=True, text=True, errors='ignore')
        if result.returncode != 0:
            print(f"Error running strings: {result.stderr}")
            return

        lines = result.stdout.split('\n')

        # 1. Search for Keywords with Context
        print("\n--- Keyword Matches (with context) ---")
        for i, line in enumerate(lines):
            for keyword in KEYWORDS:
                if keyword.lower() in line.lower():
                    # Print context: 2 lines before and 2 lines after
                    start = max(0, i - 2)
                    end = min(len(lines), i + 3)
                    context = lines[start:end]

                    print(f"Match: [{keyword}]")
                    for c_line in context:
                        if c_line == line:
                            print(f"  > {c_line.strip()}")
                        else:
                            print(f"    {c_line.strip()}")
                    print("-" * 20)
                    break # Move to next line after first keyword match to avoid duplicate prints

        # 2. Extract URLs
        print("\n--- Extracted URLs ---")
        urls = set()
        for line in lines:
            matches = URL_PATTERN.findall(line)
            for url in matches:
                urls.add(url)
        for url in sorted(list(urls)):
            print(f"  {url}")

        # 3. Extract Potential Keys/Secrets
        print("\n--- Potential Secrets/Keys ---")
        secrets = set()
        for line in lines:
            matches = KEY_PATTERN.findall(line)
            for secret in matches:
                # Filter out likely non-secrets (e.g., long strings of same char)
                if len(set(secret)) > 5:
                    secrets.add(secret)

        # Limit output for secrets
        sorted_secrets = sorted(list(secrets))
        for secret in sorted_secrets[:20]:
            print(f"  {secret}")
        if len(sorted_secrets) > 20:
            print(f"  ... and {len(sorted_secrets) - 20} more.")

    except Exception as e:
        print(f"Exception analyzing {filepath}: {e}")

def main():
    # Focus on the most interesting files identified previously
    target_files = [
        "./split_config.arm64_v8a/lib/arm64-v8a/libsud.so",
        "./split_config.arm64_v8a/lib/arm64-v8a/libCNamaSDK.so",
        "./split_config.arm64_v8a/lib/arm64-v8a/libmo-im-core.so",
        "./base/classes9.dex",
        "./base/classes.dex" # Adding classes.dex as it often has core logic
    ]

    # Also scan any .js files found
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".js"):
                target_files.append(os.path.join(root, file))

    for filepath in target_files:
        if os.path.exists(filepath):
            analyze_file(filepath)
        else:
            print(f"File not found: {filepath}")

if __name__ == "__main__":
    main()
