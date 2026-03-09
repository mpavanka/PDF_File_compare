"""
File Matcher Module

Handles intelligent matching of files between folders
"""

import difflib
from pathlib import Path
from typing import List, Dict, Tuple


class FileMatcher:
    """Match files between folders using different strategies"""
    
    def __init__(self):
        self.match_strategies = {
            'exact': self._match_exact,
            'strict': self._match_strict,
            'smart': self._match_smart,
            'positional': self._match_positional,
            'all': self._match_all
        }
    
    def match_files(
        self,
        folder1: Path,
        folder2: Path,
        pattern: str = "*.pdf",
        mode: str = "exact"
    ) -> List[Tuple[Path, Path]]:
        """
        Match files between two folders
        
        Args:
            folder1: First folder path
            folder2: Second folder path
            pattern: File pattern to match (default: *.pdf)
            mode: Matching mode (exact, smart, positional, all)
            
        Returns:
            List of (file1, file2) tuples
        """
        if mode not in self.match_strategies:
            raise ValueError(f"Unknown matching mode: {mode}. Use: {list(self.match_strategies.keys())}")
        
        files1 = sorted(folder1.glob(pattern))
        files2 = sorted(folder2.glob(pattern))
        
        return self.match_strategies[mode](files1, files2)
    
    def _match_exact(
        self,
        files1: List[Path],
        files2: List[Path]
    ) -> List[Tuple[Path, Path]]:
        """
        Match files with exact same names
        
        Args:
            files1: List of files from folder 1
            files2: List of files from folder 2
            
        Returns:
            List of matching file pairs
        """
        files1_dict = {f.name: f for f in files1}
        files2_dict = {f.name: f for f in files2}
        
        common_names = set(files1_dict.keys()) & set(files2_dict.keys())
        
        print(f"\n📁 Folder 1: {len(files1)} files")
        print(f"📁 Folder 2: {len(files2)} files")
        print(f"\n🔍 Exact name matching...\n")
        
        matches = []
        for name in sorted(common_names):
            print(f"  ✅ {name}")
            matches.append((files1_dict[name], files2_dict[name]))
        
        # Show unmatched files
        unmatched1 = set(files1_dict.keys()) - common_names
        unmatched2 = set(files2_dict.keys()) - common_names
        
        if unmatched1:
            print(f"\n⚠️  Files in Folder 1 with no match in Folder 2: {len(unmatched1)}")
            for name in sorted(list(unmatched1)[:5]):
                print(f"     ❌ {name}")
            if len(unmatched1) > 5:
                print(f"     ... and {len(unmatched1) - 5} more")
        
        if unmatched2:
            print(f"\n⚠️  Files in Folder 2 with no match in Folder 1: {len(unmatched2)}")
            for name in sorted(list(unmatched2)[:5]):
                print(f"     ❌ {name}")
            if len(unmatched2) > 5:
                print(f"     ... and {len(unmatched2) - 5} more")
        
        print(f"\n{'='*80}")
        print(f"📌 Found {len(matches)} matching file pairs")
        print(f"{'='*80}\n")
        
        return matches
    
    def _match_strict(
        self,
        files1: List[Path],
        files2: List[Path]
    ) -> List[Tuple[Path, Path]]:
        """
        Match files ignoring ONLY case differences (keeps spaces, underscores, hyphens)
        
        Examples that match:
        - "Client Report.pdf" ↔ "client report.pdf" ✅
        - "File Name.pdf" ↔ "file name.pdf" ✅
        - "Annual_Review.pdf" ↔ "annual_review.pdf" ✅
        
        Examples that DON'T match:
        - "Client Report.pdf" ↔ "Client_Report.pdf" ❌ (different structure)
        - "File Name.pdf" ↔ "FileName.pdf" ❌ (space vs no space)
        
        Args:
            files1: List of files from folder 1
            files2: List of files from folder 2
            
        Returns:
            List of matching file pairs
        """
        files2_dict = {f.name: f for f in files2}
        files2_lower_dict = {f.name.lower(): f.name for f in files2}
        matched_files2 = set()
        matches = []
        exact_matches = 0
        case_matches = 0
        
        print(f"\n📁 Folder 1: {len(files1)} files")
        print(f"📁 Folder 2: {len(files2)} files")
        print(f"\n🔍 Strict matching (case-insensitive only)...\n")
        
        for file1 in files1:
            match_name = None
            
            # Try exact match first
            if file1.name in files2_dict and file1.name not in matched_files2:
                match_name = file1.name
                print(f"  ✅ EXACT: {file1.name}")
                exact_matches += 1
            else:
                # Try case-insensitive match
                file1_lower = file1.name.lower()
                if file1_lower in files2_lower_dict:
                    match_name = files2_lower_dict[file1_lower]
                    if match_name not in matched_files2:
                        print(f"  🔄 CASE-INSENSITIVE: {file1.name}")
                        if file1.name != match_name:
                            print(f"                    ↔ {match_name}")
                        case_matches += 1
                    else:
                        match_name = None
            
            if match_name:
                matches.append((file1, files2_dict[match_name]))
                matched_files2.add(match_name)
            else:
                print(f"  ❌ NO MATCH: {file1.name}")
        
        # Show unmatched files
        unmatched1 = set(f.name for f in files1) - set(m[0].name for m in matches)
        unmatched2 = set(files2_dict.keys()) - matched_files2
        
        if unmatched1 and len(unmatched1) <= 10:
            print(f"\n⚠️  Unmatched in Folder 1: {len(unmatched1)}")
            for name in sorted(unmatched1):
                print(f"     ❌ {name}")
        elif unmatched1:
            print(f"\n⚠️  Unmatched in Folder 1: {len(unmatched1)} files")
        
        if unmatched2 and len(unmatched2) <= 10:
            print(f"\n⚠️  Unmatched in Folder 2: {len(unmatched2)}")
            for name in sorted(unmatched2):
                print(f"     ❌ {name}")
        elif unmatched2:
            print(f"\n⚠️  Unmatched in Folder 2: {len(unmatched2)} files")
        
        print(f"\n{'='*80}")
        print(f"📊 MATCHING SUMMARY:")
        print(f"{'='*80}")
        print(f"✅ Exact matches:            {exact_matches}")
        print(f"🔄 Case-insensitive matches: {case_matches}")
        print(f"📌 Total matched:            {len(matches)}")
        print(f"{'='*80}\n")
        
        if case_matches > 0:
            print(f"ℹ️  {case_matches} files matched with different case")
            print(f"   (e.g., 'File.pdf' = 'file.pdf')\n")
        
        return matches
    
    def _normalize_filename(self, filename: str) -> str:
        """
        Normalize filename for comparison by removing spaces, underscores, hyphens
        and converting to lowercase
        
        Args:
            filename: Original filename
            
        Returns:
            Normalized filename for comparison
        """
        # Remove extension for comparison
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Convert to lowercase and remove spaces, underscores, hyphens
        normalized = name_without_ext.lower()
        normalized = normalized.replace(' ', '')
        normalized = normalized.replace('_', '')
        normalized = normalized.replace('-', '')
        
        # Add back extension
        ext = filename.rsplit('.', 1)[1] if '.' in filename else ''
        if ext:
            normalized = normalized + '.' + ext.lower()
        
        return normalized
    
    def _match_smart(
        self,
        files1: List[Path],
        files2: List[Path]
    ) -> List[Tuple[Path, Path]]:
        """
        Match files using fuzzy name matching with very high accuracy (95%+)
        Also tries normalized matching (ignoring spaces, case, underscores)
        
        Args:
            files1: List of files from folder 1
            files2: List of files from folder 2
            
        Returns:
            List of matching file pairs
        """
        files2_dict = {f.name: f for f in files2}
        matched_files2 = set()
        matches = []
        exact_matches = 0
        normalized_matches = 0
        fuzzy_matches = 0
        no_matches = 0
        
        print(f"\n📁 Folder 1: {len(files1)} files")
        print(f"📁 Folder 2: {len(files2)} files")
        print(f"\n🔍 Matching files (95%+ similarity required)...\n")
        
        for file1 in files1:
            match_name = None
            match_type = None
            
            # Try 1: Exact match
            if file1.name in files2_dict:
                match_name = file1.name
                match_type = "EXACT"
                exact_matches += 1
            
            # Try 2: Normalized match (ignore spaces, case, underscores, hyphens)
            elif not match_name:
                normalized1 = self._normalize_filename(file1.name)
                for name2 in files2_dict.keys():
                    if name2 not in matched_files2:
                        normalized2 = self._normalize_filename(name2)
                        if normalized1 == normalized2:
                            match_name = name2
                            match_type = "NORMALIZED"
                            normalized_matches += 1
                            break
            
            # Try 3: High similarity fuzzy match (95%+)
            if not match_name:
                available = [name for name in files2_dict.keys() if name not in matched_files2]
                match_name = self._find_similar_filename(file1.name, available, cutoff=0.95)
                if match_name:
                    match_type = "FUZZY"
                    fuzzy_matches += 1
            
            # Record the match
            if match_name:
                if match_type == "EXACT":
                    print(f"  ✅ EXACT: {file1.name}")
                elif match_type == "NORMALIZED":
                    print(f"  🔄 NORMALIZED: {file1.name}")
                    print(f"              ↔ {match_name}")
                elif match_type == "FUZZY":
                    print(f"  ⚠️  FUZZY (95%+): {file1.name}")
                    print(f"                  ↔ {match_name}")
                
                matches.append((file1, files2_dict[match_name]))
                matched_files2.add(match_name)
            else:
                print(f"  ❌ NO MATCH: {file1.name}")
                no_matches += 1
        
        print(f"\n{'='*80}")
        print(f"📊 MATCHING SUMMARY:")
        print(f"{'='*80}")
        print(f"✅ Exact matches:       {exact_matches}")
        print(f"🔄 Normalized matches:  {normalized_matches} (spaces/case differences)")
        print(f"⚠️  Fuzzy matches:       {fuzzy_matches} (95%+ similar)")
        print(f"❌ No matches:          {no_matches}")
        print(f"📌 Total matched:       {len(matches)}")
        print(f"{'='*80}\n")
        
        if normalized_matches > 0:
            print(f"ℹ️  INFO: {normalized_matches} files matched after normalizing spaces/case/underscores")
            print(f"   Example: 'File Name.pdf' matches 'File_Name.pdf' or 'filename.pdf'\n")
        
        if fuzzy_matches > 0:
            print(f"⚠️  WARNING: {fuzzy_matches} files matched by high similarity (95%+)")
            print(f"   Review the fuzzy matches above to verify they're correct!\n")
        
        return matches
    
    def _match_positional(
        self,
        files1: List[Path],
        files2: List[Path]
    ) -> List[Tuple[Path, Path]]:
        """
        Match files by position (1st with 1st, 2nd with 2nd, etc.)
        
        Args:
            files1: List of files from folder 1
            files2: List of files from folder 2
            
        Returns:
            List of matching file pairs
        """
        matches = []
        min_count = min(len(files1), len(files2))
        
        for i in range(min_count):
            print(f"  Position {i+1}: {files1[i].name} ↔ {files2[i].name}")
            matches.append((files1[i], files2[i]))
        
        print(f"Positional matching: Found {len(matches)} matching file pairs")
        
        return matches
    
    def _match_all(
        self,
        files1: List[Path],
        files2: List[Path]
    ) -> List[Tuple[Path, Path]]:
        """
        Match every file in folder1 with every file in folder2
        
        Args:
            files1: List of files from folder 1
            files2: List of files from folder 2
            
        Returns:
            List of all possible file pairs
        """
        matches = []
        
        for file1 in files1:
            for file2 in files2:
                matches.append((file1, file2))
        
        print(f"All-pairs matching: Created {len(matches)} file pairs")
        
        return matches
    
    def _find_similar_filename(
        self,
        target: str,
        candidates: List[str],
        cutoff: float = 0.6
    ) -> str:
        """
        Find the most similar filename from candidates
        
        Args:
            target: Filename to match
            candidates: List of candidate filenames
            cutoff: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Most similar filename or None
        """
        if not candidates:
            return None
        
        matches = difflib.get_close_matches(
            target.lower(),
            [c.lower() for c in candidates],
            n=1,
            cutoff=cutoff
        )
        
        if matches:
            # Return the original case version
            for candidate in candidates:
                if candidate.lower() == matches[0]:
                    return candidate
        
        return None
    
    def get_unmatched_files(
        self,
        folder1: Path,
        folder2: Path,
        matches: List[Tuple[Path, Path]],
        pattern: str = "*.pdf"
    ) -> Tuple[List[Path], List[Path]]:
        """
        Get files that were not matched
        
        Args:
            folder1: First folder path
            folder2: Second folder path
            matches: List of matched file pairs
            pattern: File pattern
            
        Returns:
            Tuple of (unmatched_from_folder1, unmatched_from_folder2)
        """
        all_files1 = set(folder1.glob(pattern))
        all_files2 = set(folder2.glob(pattern))
        
        matched_files1 = {f1 for f1, _ in matches}
        matched_files2 = {f2 for _, f2 in matches}
        
        unmatched1 = list(all_files1 - matched_files1)
        unmatched2 = list(all_files2 - matched_files2)
        
        return unmatched1, unmatched2
