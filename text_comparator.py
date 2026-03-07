"""
Text Comparison Module

Handles line-by-line and block-level text comparison
✅ OPTIMIZED: Memory-efficient mode for large files
"""

import difflib
from typing import List, Dict, Tuple


class TextComparator:
    """Compare text content between two sources"""
    
    def __init__(self, store_equal_lines=False):
        """
        Initialize comparator
        
        Args:
            store_equal_lines: If False, skips storing equal lines (saves 70%+ memory)
        """
        self.stats = {
            'lines_added': 0,
            'lines_removed': 0,
            'lines_changed': 0,
            'total_differences': 0
        }
        self.store_equal_lines = store_equal_lines
    
    def compare_lines(self, lines1: List[str], lines2: List[str]) -> List[Dict]:
        """
        Compare two lists of text lines
        
        Args:
            lines1: Lines from first document
            lines2: Lines from second document
            
        Returns:
            List of diff data dictionaries with type, line numbers, and text
        """
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        diff_data = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Skip storing equal lines in memory-efficient mode
                if self.store_equal_lines:
                    # Both sides have same content
                    for i in range(i1, i2):
                        diff_data.append({
                            'type': 'equal',
                            'left_line': i + 1,
                            'left_text': lines1[i],
                            'right_line': j1 + (i - i1) + 1,
                            'right_text': lines2[j1 + (i - i1)]
                        })
                    
            elif tag == 'replace':
                # Content changed
                max_lines = max(i2 - i1, j2 - j1)
                for i in range(max_lines):
                    left_idx = i1 + i
                    right_idx = j1 + i
                    
                    diff_data.append({
                        'type': 'changed',
                        'left_line': left_idx + 1 if left_idx < i2 else None,
                        'left_text': lines1[left_idx] if left_idx < i2 else '',
                        'right_line': right_idx + 1 if right_idx < j2 else None,
                        'right_text': lines2[right_idx] if right_idx < j2 else ''
                    })
                    self.stats['lines_changed'] += 1
                    
            elif tag == 'delete':
                # Lines removed from left
                for i in range(i1, i2):
                    diff_data.append({
                        'type': 'deleted',
                        'left_line': i + 1,
                        'left_text': lines1[i],
                        'right_line': None,
                        'right_text': ''
                    })
                    self.stats['lines_removed'] += 1
                    
            elif tag == 'insert':
                # Lines added to right
                for i in range(j1, j2):
                    diff_data.append({
                        'type': 'added',
                        'left_line': None,
                        'left_text': '',
                        'right_line': i + 1,
                        'right_text': lines2[i]
                    })
                    self.stats['lines_added'] += 1
        
        # Count total differences
        self.stats['total_differences'] = sum([
            self.stats['lines_added'],
            self.stats['lines_removed'],
            self.stats['lines_changed']
        ])
        
        return diff_data
    
    def quick_compare_count(self, lines1: List[str], lines2: List[str]) -> int:
        """
        Ultra-fast comparison that only counts differences
        No storage, minimal memory - perfect for large batches
        
        Args:
            lines1: Lines from first document
            lines2: Lines from second document
            
        Returns:
            Number of differences
        """
        if lines1 == lines2:
            return 0
        
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        diff_count = 0
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag != 'equal':
                diff_count += max(i2 - i1, j2 - j1)
        
        return diff_count
    
    def has_differences(self, lines1: List[str], lines2: List[str]) -> bool:
        """
        Quick check if two text lists are different
        
        Args:
            lines1: Lines from first document
            lines2: Lines from second document
            
        Returns:
            True if there are differences, False if identical
        """
        return lines1 != lines2
    
    def find_similar_text(self, target: str, candidates: List[str], cutoff: float = 0.6) -> str:
        """
        Find the most similar text from a list of candidates
        
        Args:
            target: Text to match
            candidates: List of candidate texts
            cutoff: Similarity threshold (0.0 to 1.0)
            
        Returns:
            Most similar candidate or None
        """
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
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get comparison statistics
        
        Returns:
            Dictionary with lines added, removed, changed, total differences
        """
        return self.stats.copy()
    
    def reset_statistics(self):
        """Reset statistics counters"""
        self.stats = {
            'lines_added': 0,
            'lines_removed': 0,
            'lines_changed': 0,
            'total_differences': 0
        }
