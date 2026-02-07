import os
import subprocess
import re

# Keywords to search for
KEYWORDS = [
    "pay", "coin", "diamond", "bypass", "verify", "mock",
    "debug", "cheat", "coupon", "vip", "purchase", "gem", "gold", "token", "sign"
]

# Function to run strings command
def search_strings(filepath, keywords):
    print(f"Analyzing strings in: {filepath}")
    try:
        # Use subprocess to run strings command
        result = subprocess.run(['strings', filepath], capture_output=True, text=True, errors='ignore')
        if result.returncode != 0:
            print(f"Error running strings on {filepath}: {result.stderr}")
            return

        lines = result.stdout.split('\n')
        matches = []
        for line in lines:
            for keyword in keywords:
                if keyword.lower() in line.lower():
                    matches.append((keyword, line.strip()))

        if matches:
            print(f"Found {len(matches)} matches in {filepath}:")
            # Limit output to avoid huge logs
            unique_matches = sorted(list(set(matches)))
            for keyword, match in unique_matches[:50]:  # Show top 50 matches per file
                print(f"  [{keyword}]: {match}")
            if len(unique_matches) > 50:
                print(f"  ... and {len(unique_matches) - 50} more.")
        else:
            print(f"No matches found in {filepath}")

    except Exception as e:
        print(f"Exception while analyzing strings in {filepath}: {e}")

# Function to run objdump -T
def dump_symbols(filepath):
    print(f"Dumping symbols for: {filepath}")
    try:
        result = subprocess.run(['objdump', '-T', filepath], capture_output=True, text=True, errors='ignore')
        if result.returncode != 0:
            print(f"Error running objdump on {filepath}: {result.stderr}")
            return

        lines = result.stdout.split('\n')
        symbols = []
        for line in lines:
            if "DF .text" in line or "DF *UND*" in line: # Filter for function definitions
                symbols.append(line.strip())

        if symbols:
            print(f"Found {len(symbols)} symbols in {filepath}:")
            # Filter for interesting symbols
            interesting_symbols = []
            for symbol in symbols:
                for keyword in KEYWORDS:
                    if keyword.lower() in symbol.lower():
                        interesting_symbols.append(symbol)

            if interesting_symbols:
                for symbol in interesting_symbols[:50]:
                    print(f"  {symbol}")
                if len(interesting_symbols) > 50:
                    print(f"  ... and {len(interesting_symbols) - 50} more interesting symbols.")
            else:
                print("  No interesting symbols found based on keywords.")
        else:
            print(f"No symbols found in {filepath}")

    except Exception as e:
        print(f"Exception while dumping symbols in {filepath}: {e}")

def main():
    print("Starting static analysis...")

    # Walk through the directory
    for root, dirs, files in os.walk("."):
        for file in files:
            filepath = os.path.join(root, file)

            # Skip git directory
            if ".git" in filepath:
                continue

            if file.endswith(".so"):
                print(f"\n--- Processing .so file: {filepath} ---")
                search_strings(filepath, KEYWORDS)
                dump_symbols(filepath)

            elif file.endswith(".dex"):
                print(f"\n--- Processing .dex file: {filepath} ---")
                search_strings(filepath, KEYWORDS)
                # Dex files don't have symbols in the same way as ELF, so skip objdump

            elif file.endswith(".js") or file.endswith(".html"):
                print(f"\n--- Processing web asset: {filepath} ---")
                search_strings(filepath, KEYWORDS)

if __name__ == "__main__":
    main()
