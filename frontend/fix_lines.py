#!/usr/bin/env python3

import re


def fix_long_lines(file_path):
    """Fix long lines in Python file by breaking them at logical points."""

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    fixed_lines = []

    for line_num, line in enumerate(lines, 1):
        if len(line) <= 79:
            fixed_lines.append(line)
            continue

        # Check if it's a long f-string that can be broken
        if 'f"' in line and len(line) > 79:
            # Find positions where we can break the line
            # Look for + operations, | operations, or natural break points
            if " | " in line:
                # Break at pipe operator
                parts = line.split(" | ")
                if len(parts) == 2:
                    indent = len(line) - len(line.lstrip())
                    new_line = f"{parts[0]} |\"\n{' ' * (indent + 4)}f\"| {parts[1]}"
                    if '")' in new_line:
                        new_line = new_line.replace(
                            '")f"| ', '") +\n' + " " * (indent + 4) + 'f"'
                        )
                    fixed_lines.append(new_line)
                    continue

            # Try to break at natural word boundaries in f-strings
            if line.strip().startswith('f"') and line.strip().endswith('"'):
                # For simple f-strings, try to break in the middle
                content_start = line.find('f"') + 2
                content_end = line.rfind('"')
                prefix = line[:content_start]
                suffix = line[content_end:]
                content = line[content_start:content_end]

                # Find a good break point (space, colon, etc.)
                mid_point = len(content) // 2
                break_point = mid_point

                # Look for good break points around the middle
                for offset in range(10):
                    for pos in [mid_point - offset, mid_point + offset]:
                        if 0 < pos < len(content) and content[pos] in [
                            " ",
                            ":",
                            "-",
                            "|",
                        ]:
                            break_point = pos + 1
                            break
                    if break_point != mid_point:
                        break

                if break_point != mid_point:
                    indent = len(line) - len(line.lstrip())
                    part1 = content[:break_point].rstrip()
                    part2 = content[break_point:].lstrip()

                    new_line = f'{prefix}{part1}"\n{" " * indent}f"{part2}{suffix}'
                    fixed_lines.append(new_line)
                    continue

        # For other long lines, try different strategies
        if "(" in line and ")" in line and "," in line:
            # Break function calls at commas
            indent = len(line) - len(line.lstrip())
            if line.count("(") == line.count(")") == 1:  # Simple function call
                paren_start = line.find("(")
                paren_end = line.rfind(")")
                before_paren = line[: paren_start + 1]
                inside_paren = line[paren_start + 1 : paren_end]
                after_paren = line[paren_end:]

                # Try to break at commas
                parts = [p.strip() for p in inside_paren.split(",")]
                if len(parts) > 1:
                    new_line = before_paren + "\n"
                    for i, part in enumerate(parts):
                        if i == 0:
                            new_line += f"{' ' * (indent + 4)}{part},"
                        elif i == len(parts) - 1:
                            new_line += f"\n{' ' * (indent + 4)}{part}"
                        else:
                            new_line += f"\n{' ' * (indent + 4)}{part},"
                    new_line += after_paren

                    # Check if this actually made it shorter
                    if all(len(l) <= 79 for l in new_line.split("\n")):
                        fixed_lines.append(new_line)
                        continue

        # If no fix worked, just add the original line
        fixed_lines.append(line)

    # Write back the fixed content
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("\n".join(fixed_lines))

    print(f"Fixed long lines in {file_path}")


if __name__ == "__main__":
    fix_long_lines(
        "/home/yan/A101/HR/frontend/components/core/profile_viewer_component.py"
    )
