#!/usr/bin/env python3
"""Score reading level of all markdown files in the project."""

import os
from pathlib import Path
import textstat

def get_md_files(root_dir):
    """Get all markdown files, excluding venv."""
    root = Path(root_dir)
    md_files = []

    for md_file in root.rglob("*.md"):
        # Skip venv and hidden directories
        if 'venv' in md_file.parts or any(part.startswith('.') for part in md_file.parts):
            continue
        md_files.append(md_file)

    return sorted(md_files)

def score_file(filepath):
    """Calculate readability scores for a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Remove markdown syntax for better scoring
        # Simple cleanup - remove headers, links, code blocks
        lines = text.split('\n')
        clean_lines = []
        in_code_block = False

        for line in lines:
            if line.startswith('```'):
                in_code_block = not in_code_block
                continue
            if in_code_block:
                continue
            if line.startswith('#'):
                # Keep header text without the #
                line = line.lstrip('#').strip()
            # Remove markdown links [text](url) -> text
            while '[' in line and '](' in line:
                start = line.find('[')
                mid = line.find('](', start)
                end = line.find(')', mid)
                if start != -1 and mid != -1 and end != -1:
                    link_text = line[start+1:mid]
                    line = line[:start] + link_text + line[end+1:]
                else:
                    break
            clean_lines.append(line)

        clean_text = '\n'.join(clean_lines).strip()

        if not clean_text or len(clean_text) < 100:
            return None

        # Calculate various scores
        flesch_reading = textstat.flesch_reading_ease(clean_text)
        flesch_kincaid = textstat.flesch_kincaid_grade(clean_text)
        smog = textstat.smog_index(clean_text)

        return {
            'flesch_reading_ease': round(flesch_reading, 1),
            'flesch_kincaid_grade': round(flesch_kincaid, 1),
            'smog_index': round(smog, 1),
            'word_count': len(clean_text.split())
        }
    except Exception as e:
        return None

def main():
    """Main function."""
    project_root = Path(__file__).parent
    md_files = get_md_files(project_root)

    print(f"\n{'File':<60} {'Grade':<8} {'SMOG':<8} {'Flesch':<8} {'Words':<8}")
    print("=" * 92)

    results = []

    for md_file in md_files:
        rel_path = md_file.relative_to(project_root)
        scores = score_file(md_file)

        if scores:
            results.append({
                'file': str(rel_path),
                'grade': scores['flesch_kincaid_grade'],
                'smog': scores['smog_index'],
                'flesch': scores['flesch_reading_ease'],
                'words': scores['word_count']
            })

            print(f"{str(rel_path):<60} {scores['flesch_kincaid_grade']:<8} "
                  f"{scores['smog_index']:<8} {scores['flesch_reading_ease']:<8} "
                  f"{scores['word_count']:<8}")

    print("\n" + "=" * 92)

    # Calculate averages
    if results:
        avg_grade = sum(r['grade'] for r in results) / len(results)
        avg_smog = sum(r['smog'] for r in results) / len(results)
        avg_flesch = sum(r['flesch'] for r in results) / len(results)
        total_words = sum(r['words'] for r in results)

        print(f"\n{'AVERAGES':<60} {avg_grade:<8.1f} {avg_smog:<8.1f} {avg_flesch:<8.1f} {total_words:<8}")

        # Show files above grade 6.0
        print("\n\nFiles ABOVE Grade 6.0 (need simplification):")
        print("-" * 92)
        above_target = [r for r in results if r['grade'] > 6.0]
        if above_target:
            for r in sorted(above_target, key=lambda x: x['grade'], reverse=True):
                print(f"{r['file']:<60} Grade {r['grade']}")
        else:
            print("✓ All files at or below Grade 6.0!")

        # Show files at or below 5.0
        print("\n\nFiles at or BELOW Grade 5.0 (excellent!):")
        print("-" * 92)
        at_target = [r for r in results if r['grade'] <= 5.0]
        if at_target:
            for r in sorted(at_target, key=lambda x: x['grade']):
                print(f"{r['file']:<60} Grade {r['grade']}")
        else:
            print("No files at Grade 5.0 or below yet.")

    print(f"\n\nTotal files analyzed: {len(results)}")
    print("\nReading Level Guide:")
    print("  Grade 5.0 or less = Elementary (target for user docs)")
    print("  Grade 6.0 or less = Middle school (acceptable)")
    print("  Grade 7.0-9.0     = High school (technical docs only)")
    print("  Grade 10.0+       = College (too complex)")

if __name__ == '__main__':
    main()
