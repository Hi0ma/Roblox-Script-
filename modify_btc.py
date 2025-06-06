import sys

def run_modifications():
    try:
        with open('btc.txt', 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print("btc.txt not found.")
        return

    # Correct imports
    modified_lines = []
    if lines:
        first_line = lines[0].strip()
        if first_line.startswith("import sysimport asyncio"):
            modified_lines.append("import sys\n")
            modified_lines.append("import json\n")
            # Add the rest of the original first line, assuming it was 'import sys' + 'import asyncio...'
            original_imports_after_sys = first_line[len("import sys"):]
            modified_lines.append(original_imports_after_sys + "\n")
            # Skip the original problematic first line
            lines = lines[1:]
        else:
            # If the first line isn't the problematic one, check if it's just 'import sys'
            # or if json is already imported
            if "import json" not in first_line and "import sys" in first_line:
                 modified_lines.append("import sys\n")
                 modified_lines.append("import json\n")
                 if "import sys" != first_line: # if import sys was part of a larger line
                    modified_lines.append(first_line[len("import sys"):].strip() + "\n")
                 lines = lines[1:] # Handled first line
            elif "import json" not in first_line : # if no import sys but also no import json
                modified_lines.append("import json\n")
                # keep original first line
            else: # json is already there or some other case
                pass # keep original first line by not consuming it from `lines` yet


    modified_lines.extend(lines) # Add remaining original lines or all if first line was fine
    lines = modified_lines # work with the potentially import-corrected lines

    new_lines = []
    config_block_found = False
    config_block_ended = False
    in_old_config_block = False

    # New CONFIG loading block
    config_loader_block = [
        "try:\n",
        "    with open('config.json', 'r') as f:\n",
        "        CONFIG = json.load(f)\n",
        "except FileNotFoundError:\n",
        "    print(\"FATAL ERROR: config.json not found. Please ensure the configuration file exists.\")\n",
        "    sys.exit(1)\n",
        "except json.JSONDecodeError:\n",
        "    print(\"FATAL ERROR: config.json is not valid JSON. Please check the file content.\")\n",
        "    sys.exit(1)\n"
    ]

    for line in lines:
        if "CONFIG = {" in line: # Start of old CONFIG block
            if not config_block_found: # Only add the new block once
                new_lines.extend(config_loader_block)
                config_block_found = True
            in_old_config_block = True
            continue # Skip this line

        if in_old_config_block:
            if line.strip() == "}": # End of old CONFIG block
                in_old_config_block = False
                config_block_ended = True
            continue # Skip lines within the old CONFIG block

        new_lines.append(line)
        # If old config block was never found, and we are past logging, insert it.
        if not config_block_found and "event_logger.setLevel(logging.INFO)" in line:
            new_lines.extend(config_loader_block)
            config_block_found = True


    # If CONFIG block was found and removed, or added, write changes
    if config_block_found :
        try:
            with open('btc.txt', 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("btc.txt modified successfully.")
        except Exception as e:
            print(f"Error writing to btc.txt: {e}")
    else:
        print("Old CONFIG block not found or other issue; file not modified by config part.")

if __name__ == '__main__':
    run_modifications()
