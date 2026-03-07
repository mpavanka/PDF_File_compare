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
        
        matches = []
        for name in sorted(common_names):
            matches.append((files1_dict[name], files2_dict[name]))
        
        print(f"Exact matching: Found {len(matches)} matching file pairs")
        
        return matches
    
    def _match_smart(
        self,
        files1: List[Path],
        files2: List[Path]
    ) -> List[Tuple[Path, Path]]:
        """
        Match files using fuzzy name matching
        
        Args:
            files1: List of files from folder 1
            files2: List of files from folder 2
            
        Returns:
            List of matching file pairs
        """
        files2_dict = {f.name: f for f in files2}
        matched_files2 = set()
        matches = []
        
        for file1 in files1:
            # Try exact match first
            if file1.name in files2_dict:
                match_name = file1.name
            else:
                # Try fuzzy matching
                available = [name for name in files2_dict.keys() if name not in matched_files2]
                match_name = self._find_similar_filename(file1.name, available)
            
            if match_name:
                print(f"  Matched: {file1.name} ↔ {match_name}")
                matches.append((file1, files2_dict[match_name]))
                matched_files2.add(match_name)
            else:
                print(f"  No match found for: {file1.name}")
        
        print(f"Smart matching: Found {len(matches)} matching file pairs")
        
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
