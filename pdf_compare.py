"""
PDF Comparison Tool - Main Orchestrator

Uses modular components to perform PDF comparisons
✅ OPTIMIZED FOR LARGE BATCHES (1000+ files, 30+ pages)
"""

import sys
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import multiprocessing as mp
import time

# Import our modular components
from pdf_extractor import PDFExtractor
from text_comparator import TextComparator
from html_generator import HTMLReportGenerator
from file_matcher import FileMatcher

# Try to import tqdm for progress bar
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    print("💡 Tip: Install tqdm for progress bars: pip install tqdm")


class PDFComparisonOrchestrator:
    """Main class that orchestrates PDF comparisons with performance optimizations"""
    
    def __init__(self, max_workers=None, use_parallel=True, memory_efficient=True):
        """
        Initialize orchestrator
        
        Args:
            max_workers: Number of parallel workers (default: CPU count - 1)
            use_parallel: Enable parallel processing for batches > 3 files
            memory_efficient: Don't store equal lines (saves memory)
        """
        self.html_generator = HTMLReportGenerator()
        self.file_matcher = FileMatcher()
        self.stats = {
            'files_compared': 0,
            'files_with_differences': 0,
            'total_differences': 0,
            'processing_time': 0
        }
        # Use CPU count - 1 for parallel processing, minimum 1
        self.max_workers = max_workers or max(1, mp.cpu_count() - 1)
        self.use_parallel = use_parallel
        self.memory_efficient = memory_efficient
    def compare_two_files(self, file1: Path, file2: Path, for_batch=False) -> Dict:
        """
        Compare two PDF files (memory-efficient version)
        
        Args:
            file1: Path to first PDF
            file2: Path to second PDF
            for_batch: If True, stores all lines for detailed batch report view
            
        Returns:
            Dictionary with comparison results
        """
        # Extract content from both files
        extractor1 = PDFExtractor(file1)
        extractor2 = PDFExtractor(file2)
        
        lines1 = extractor1.extract_text_lines()
        lines2 = extractor2.extract_text_lines()
        
        # Compare page by page
        max_pages = max(len(lines1), len(lines2))
        all_page_comparisons = []
        
        # For batch reports, always store all lines so user can toggle "Show All"
        # For single file reports, use memory-efficient mode
        store_all = for_batch or not self.memory_efficient
        comparator = TextComparator(store_equal_lines=store_all)
        
        for page_num in range(1, max_pages + 1):
            page_lines1 = lines1.get(page_num, [])
            page_lines2 = lines2.get(page_num, [])
            
            # Compare this page
            diff_data = comparator.compare_lines(page_lines1, page_lines2)
            
            has_diff = any(d['type'] != 'equal' for d in diff_data)
            
            all_page_comparisons.append({
                'page_num': page_num,
                'diff_data': diff_data,
                'has_differences': has_diff
            })
        
        # Get statistics
        stats = comparator.get_statistics()
        stats['total_pages'] = max_pages
        stats['pages_with_diffs'] = sum(1 for p in all_page_comparisons if p['has_differences'])
        stats['total_diffs'] = stats['total_differences']
        
        return {
            'file1': file1,
            'file2': file2,
            'page_comparisons': all_page_comparisons,
            'stats': stats,
            'has_differences': stats['total_differences'] > 0
        }
    
    def compare_folders(
        self,
        folder1: Path,
        folder2: Path,
        match_mode: str = "exact",
        pattern: str = "*.pdf"
    ) -> List[Dict]:
        """
        Compare all matching files between two folders
        ⚡ Uses parallel processing for large batches
        
        Args:
            folder1: First folder path
            folder2: Second folder path
            match_mode: How to match files (exact, smart, positional, all)
            pattern: File pattern to match
            
        Returns:
            List of comparison results
        """
        start_time = time.time()
        
        print(f"\n{'='*80}")
        print(f"🚀 HIGH-PERFORMANCE PDF COMPARISON")
        print(f"{'='*80}")
        print(f"Folder 1: {folder1}")
        print(f"Folder 2: {folder2}")
        print(f"Match mode: {match_mode}")
        print(f"Memory efficient: {self.memory_efficient}")
        if self.use_parallel:
            print(f"Parallel workers: {self.max_workers}")
        print(f"{'='*80}\n")
        
        # Match files
        file_pairs = self.file_matcher.match_files(folder1, folder2, pattern, match_mode)
        
        if not file_pairs:
            print("❌ No matching files found!")
            return []
        
        print(f"✅ Found {len(file_pairs)} file pairs to compare\n")
        
        # Choose processing mode based on batch size
        if self.use_parallel and len(file_pairs) > 3:
            print(f"⚡ Using parallel processing...")
            results = self._compare_parallel(file_pairs)
        else:
            print(f"🔄 Using sequential processing...")
            results = self._compare_sequential(file_pairs)
        
        # Calculate processing time
        self.stats['processing_time'] = time.time() - start_time
        
        return results
    
    def _compare_sequential(self, file_pairs: List[Tuple[Path, Path]]) -> List[Dict]:
        """Compare files sequentially with progress bar"""
        results = []
        
        if HAS_TQDM:
            iterator = tqdm(file_pairs, desc="Comparing", unit="files", ncols=100)
        else:
            iterator = file_pairs
            total = len(file_pairs)
        
        for idx, (file1, file2) in enumerate(iterator, 1):
            result = self.compare_two_files(file1, file2, for_batch=True)
            results.append(result)
            
            self.stats['files_compared'] += 1
            if result['has_differences']:
                self.stats['files_with_differences'] += 1
                self.stats['total_differences'] += result['stats']['total_diffs']
            
            if not HAS_TQDM:
                print(f"  Progress: {idx}/{total} files", end='\r')
        
        if not HAS_TQDM:
            print()  # New line after progress
        
        return results
    
    def _compare_parallel(self, file_pairs: List[Tuple[Path, Path]]) -> List[Dict]:
        """Compare files in parallel using ThreadPoolExecutor"""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all comparison tasks with for_batch=True
            future_to_pair = {
                executor.submit(self.compare_two_files, f1, f2, True): (f1, f2)
                for f1, f2 in file_pairs
            }
            
            # Process completed tasks with progress bar
            if HAS_TQDM:
                with tqdm(total=len(file_pairs), desc="Comparing", unit="files", ncols=100) as pbar:
                    for future in as_completed(future_to_pair):
                        try:
                            result = future.result()
                            results.append(result)
                            
                            self.stats['files_compared'] += 1
                            if result['has_differences']:
                                self.stats['files_with_differences'] += 1
                                self.stats['total_differences'] += result['stats']['total_diffs']
                            
                            pbar.update(1)
                        except Exception as e:
                            file1, file2 = future_to_pair[future]
                            print(f"\n⚠️  Error: {file1.name} vs {file2.name}: {str(e)[:50]}")
                            pbar.update(1)
            else:
                # Without tqdm, just process with manual progress
                total = len(file_pairs)
                for idx, future in enumerate(as_completed(future_to_pair), 1):
                    try:
                        result = future.result()
                        results.append(result)
                        
                        self.stats['files_compared'] += 1
                        if result['has_differences']:
                            self.stats['files_with_differences'] += 1
                            self.stats['total_differences'] += result['stats']['total_diffs']
                        
                        print(f"  Progress: {idx}/{total} files", end='\r')
                    except Exception as e:
                        file1, file2 = future_to_pair[future]
                        print(f"\n⚠️  Error: {file1.name} vs {file2.name}: {str(e)[:50]}")
                print()  # New line after progress
        
        return results
    
    def generate_detailed_report(
        self,
        comparison_result: Dict,
        output_path: str
    ) -> Path:
        """
        Generate a detailed comparison report for a single file pair
        
        Args:
            comparison_result: Result from compare_two_files
            output_path: Where to save the report
            
        Returns:
            Path to generated report
        """
        return self.html_generator.generate_detailed_comparison(
            file1_name=comparison_result['file1'].name,
            file2_name=comparison_result['file2'].name,
            page_comparisons=comparison_result['page_comparisons'],
            stats=comparison_result['stats'],
            output_path=output_path
        )
    
    def generate_batch_summary(
        self,
        results: List[Dict],
        output_path: str
    ) -> Path:
        """
        Generate a summary report for batch comparisons
        
        Args:
            results: List of comparison results
            output_path: Where to save the summary
            
        Returns:
            Path to generated report
        """
        # Generate individual detailed reports
        output_dir = Path(output_path).parent
        details_dir = output_dir / "details"
        details_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, result in enumerate(results):
            if result['has_differences']:
                detail_filename = (
                    f"detail_{idx+1}_{result['file1'].stem}_vs_{result['file2'].stem}.html"
                )
                detail_path = details_dir / detail_filename
                self.generate_detailed_report(result, str(detail_path))
                result['detail_report'] = f"details/{detail_filename}"
                print(f"  Generated: {detail_filename}")
        
        # Generate summary
        return self.html_generator.generate_batch_summary(
            results=results,
            overall_stats=self.stats,
            output_path=output_path
        )
    
    def print_summary(self):
        """Print comparison statistics with performance metrics"""
        print("\n" + "=" * 80)
        print("✅ COMPARISON COMPLETE")
        print("=" * 80)
        print(f"Files compared: {self.stats['files_compared']}")
        print(f"Files with differences: {self.stats['files_with_differences']}")
        print(f"Identical files: {self.stats['files_compared'] - self.stats['files_with_differences']}")
        print(f"Total differences: {self.stats['total_differences']}")
        print(f"⏱️  Processing time: {self.stats['processing_time']:.2f}s")
        
        if self.stats['files_compared'] > 0:
            avg_time = self.stats['processing_time'] / self.stats['files_compared']
            print(f"⚡ Average per file: {avg_time:.2f}s")
            
            # Estimate for larger batches
            if self.stats['files_compared'] < 100:
                est_1000 = (avg_time * 1000) / 60
                print(f"📊 Estimated for 1000 files: ~{est_1000:.1f} minutes")
        
        print("=" * 80)


def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("PDF Comparison Tool - Modular Version")
        print("=" * 80)
        print("\nUsage:")
        print("  Compare two PDFs:")
        print("    python pdf_compare.py file1.pdf file2.pdf [output.html]")
        print("\n  Compare two folders:")
        print("    python pdf_compare.py folder1 folder2 [match_mode] [output.html]")
        print("\nMatch Modes:")
        print("  exact      - Only files with exact matching names")
        print("  smart      - Fuzzy matching of similar names (default)")
        print("  positional - Match by position (1st with 1st, etc.)")
        print("  all        - Compare every file with every other file")
        print("\nExamples:")
        print("  python pdf_compare.py report1.pdf report2.pdf comparison.html")
        print("  python pdf_compare.py ./old ./new smart summary.html")
        sys.exit(1)
    
    orchestrator = PDFComparisonOrchestrator()
    
    path1 = Path(sys.argv[1])
    path2 = Path(sys.argv[2])
    
    if not path1.exists() or not path2.exists():
        print("Error: One or both paths do not exist")
        sys.exit(1)
    
    # Determine if comparing files or folders
    if path1.is_file() and path2.is_file():
        # Compare two files
        output = sys.argv[3] if len(sys.argv) > 3 else "comparison.html"

        # If the output is a directory path (or ends with a separator), save report inside it
        output_path = Path(output)
        if output_path.suffix == "" and (output_path.exists() and output_path.is_dir() or str(output).endswith(('/', '\\'))):
            output_path.mkdir(parents=True, exist_ok=True)
            output = str(output_path / f"{path1.stem}_vs_{path2.stem}.html")

        print(f"Comparing files:")
        print(f"  {path1}")
        print(f"  {path2}\n")

        result = orchestrator.compare_two_files(path1, path2)
        report_path = orchestrator.generate_detailed_report(result, output)

        print(f"\n✅ Comparison complete!")
        print(f"📊 Report saved to: {report_path}")

    elif path1.is_dir() and path2.is_dir():
        # Compare two folders
        match_mode = "smart"
        output = "batch_summary.html"

        if len(sys.argv) >= 4:
            if sys.argv[3].lower() in ['exact', 'smart', 'positional', 'all']:
                match_mode = sys.argv[3].lower()
                if len(sys.argv) >= 5:
                    output = sys.argv[4]
            else:
                output = sys.argv[3]

        # If output is a directory (or ends with a separator), save summary + details inside it
        output_path = Path(output)
        if output_path.suffix == "" and (output_path.exists() and output_path.is_dir() or str(output).endswith(('/', '\\'))):
            output_path.mkdir(parents=True, exist_ok=True)
            output = str(output_path / "summary.html")

        results = orchestrator.compare_folders(path1, path2, match_mode)

        if results:
            report_path = orchestrator.generate_batch_summary(results, output)
            orchestrator.print_summary()
            print(f"\n✅ Summary report: {report_path}")
            print(f"📂 Open in browser to view all comparisons")
        else:
            print("\n⚠️  No matching files found to compare")
    else:
        print("Error: Both paths must be either files or folders")
        sys.exit(1)


if __name__ == "__main__":
    main()
