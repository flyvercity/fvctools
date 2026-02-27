import os
import re
import sys

def verify_install_script(filepath):
    """
    Verifies that the script does not use Invoke-Expression and uses proper argument passing.
    """
    print(f"Checking {filepath}...")
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Check for Invoke-Expression (case insensitive)
        if re.search(r"Invoke-Expression", content, re.IGNORECASE):
            print(f"FAIL: {filepath} contains 'Invoke-Expression'.")
            return False

        # Check for safe usage of call operator with array
        # We expect $pipArgs definition and usage
        has_array_def = "$pipArgs = @(" in content
        has_call_op = "& $Pip $pipArgs" in content

        if has_array_def and has_call_op:
            print(f"PASS: {filepath} uses explicit argument array and call operator.")
            return True
        else:
            print(f"FAIL: {filepath} does not use explicit argument array (found: array={has_array_def}, call={has_call_op}).")
            return False

    except FileNotFoundError:
        print(f"ERROR: {filepath} not found.")
        return False

def main():
    filepath = "scripts/Install-FvcTools.ps1"
    if verify_install_script(filepath):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
