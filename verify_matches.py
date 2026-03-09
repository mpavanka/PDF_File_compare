#!/usr/bin/env python3
"""
File Match Verification Tool

Preview which files will be matched before running the full comparison.
Use this to verify the matching is correct when you have different numbers of files.
"""

import sys
from pathlib import Path
from file_matcher import FileMatcher


def main():
    if len(sys.argv) < 3:
        print("📋 File Match Verification Tool")
        print("=" * 80)
        print("\nUsage:")
        print("  python verify_matches.py folder1 folder2 [match_mode]")
        print("\nMatch Modes:")
        print("  exact      - 100% identical names (case-sensitive)")
        print("  strict     - Case-insensitive only (RECOMMENDED)")
        print("               'File.pdf' = 'file.pdf' ✅")
        print("               'File.pdf' ≠ 'File_.pdf' ❌")
        print("  smart      - Fuzzy 95%+ + normalization (removes spaces/underscores)")
        print("  positional - Match by position (1st with 1st, etc.)")
        print("\nExamples:")
        print("  python verify_matches.py ./expected ./actual strict")
        print("  python verify_matches.py ./expected ./actual exact")
        print("\n⚠️  For different file counts (e.g., 5000 vs 91):")
        print("   Use 'strict' for case differences or 'exact' for identical names")
        sys.exit(1)
    
    folder1 = Path(sys.argv[1])
    folder2 = Path(sys.argv[2])
    match_mode = sys.argv[3] if len(sys.argv) > 3 else "exact"
    
    if not folder1.exists():
        print(f"❌ Error: Folder 1 does not exist: {folder1}")
        sys.exit(1)
    
    if not folder2.exists():
        print(f"❌ Error: Folder 2 does not exist: {folder2}")
        sys.exit(1)
    
    print(f"\n{'='*80}")
    print(f"📋 FILE MATCH VERIFICATION")
    print(f"{'='*80}")
    print(f"Folder 1: {folder1}")
    print(f"Folder 2: {folder2}")
    print(f"Mode: {match_mode}")
    print(f"{'='*80}\n")
    
    # Create matcher and get matches
    matcher = FileMatcher()
    
    try:
        matches = matcher.match_files(folder1, folder2, "*.pdf", match_mode)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    
    if not matches:
        print("\n❌ No matching files found!")
        print("\nPossible reasons:")
        print("  • Files have different names in the two folders")
        print("  • No PDF files found")
        print("  • Wrong match mode selected")
        print("\n💡 Try using 'exact' mode and ensure files have identical names")
        sys.exit(1)
    
    # Show detailed match list
    print(f"\n📝 DETAILED MATCH LIST:")
    print(f"{'='*80}\n")
    
    for idx, (file1, file2) in enumerate(matches, 1):
        if file1.name == file2.name:
            status = "✅ EXACT"
            marker = ""
        else:
            status = "⚠️  FUZZY"
            marker = " ← CHECK THIS!"
        
        print(f"{idx:3}. {status}")
        print(f"     Folder 1: {file1.name}")
        print(f"     Folder 2: {file2.name}{marker}")
        print()
    
    # Summary
    exact_count = sum(1 for f1, f2 in matches if f1.name == f2.name)
    fuzzy_count = len(matches) - exact_count
    
    print(f"{'='*80}")
    print(f"📊 VERIFICATION SUMMARY")
    print(f"{'='*80}")
    print(f"Total matches:  {len(matches)}")
    print(f"Exact matches:  {exact_count}")
    print(f"Fuzzy matches:  {fuzzy_count}")
    
    if fuzzy_count > 0:
        print(f"\n⚠️  WARNING: {fuzzy_count} fuzzy matches detected!")
        print(f"   These files have similar but NOT identical names.")
        print(f"   Review the list above carefully!")
        print(f"\n💡 Recommendation: Use 'exact' mode to avoid wrong matches:")
        print(f"   python verify_matches.py {folder1} {folder2} exact")
    else:
        print(f"\n✅ All matches are EXACT (identical file names)")
        print(f"   Safe to proceed with comparison!")
    
    print(f"{'='*80}\n")
    
    # Ask if user wants to proceed
    print("Ready to compare these files?")
    print(f"\nTo compare, run:")
    print(f"  python pdf_compare.py {folder1} {folder2} {match_mode} summary.html")
    print()


if __name__ == "__main__":
    main()
