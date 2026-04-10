"""
HTML Report Generator Module

Generates HTML comparison reports with various styles
"""

from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class HTMLReportGenerator:
    """Generate HTML comparison reports"""
    
    def __init__(self):
        self.output_dir = Path.cwd()
    
    def generate_detailed_comparison(
        self, 
        file1_name: str,
        file2_name: str,
        page_comparisons: List[Dict],
        stats: Dict[str, int],
        output_path: str
    ) -> Path:
        """
        Generate a detailed side-by-side comparison report
        
        Args:
            file1_name: Name of first file
            file2_name: Name of second file
            page_comparisons: List of page comparison data
            stats: Statistics dictionary
            output_path: Where to save the report
            
        Returns:
            Path to generated report
        """
        html_content = self._build_header(file1_name, file2_name, stats)
        html_content += self._build_side_by_side_content(file1_name, file2_name, page_comparisons)
        html_content += self._build_footer_script()
        
        output_path = Path(output_path)
        output_path.write_text(html_content, encoding='utf-8')
        
        return output_path
    
    def generate_batch_summary(
        self,
        results: List[Dict],
        overall_stats: Dict[str, int],
        output_path: str
    ) -> Path:
        """
        Generate a summary report for batch comparisons
        
        Args:
            results: List of comparison results
            overall_stats: Overall statistics
            output_path: Where to save the report
            
        Returns:
            Path to generated report
        """
        html_content = self._build_summary_header(overall_stats)
        html_content += self._build_results_table(results)
        html_content += self._build_summary_footer()
        
        output_path = Path(output_path)
        output_path.write_text(html_content, encoding='utf-8')
        
        return output_path
    
    def _build_header(self, file1: str, file2: str, stats: Dict) -> str:
        """Build HTML header for detailed comparison"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Comparison: {file1} vs {file2}</title>
    {self._get_styles()}
</head>
<body>
    <div class="header">
        <h1>📊 PDF Comparison Report</h1>
        <div style="font-size: 13px; opacity: 0.9;">{file1} ↔ {file2}</div>
    </div>
    <div class="stats-bar">
        <div class="stat-item">
            <span class="stat-label">Pages:</span>
            <span class="stat-value">{stats.get('total_pages', 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Differences:</span>
            <span class="stat-value changed">{stats.get('total_diffs', 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Added:</span>
            <span class="stat-value added">+{stats.get('lines_added', 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Removed:</span>
            <span class="stat-value removed">-{stats.get('lines_removed', 0)}</span>
        </div>
        <div class="stat-item">
            <span class="stat-label">Changed:</span>
            <span class="stat-value changed">~{stats.get('lines_changed', 0)}</span>
        </div>
        <div style="flex: 1;"></div>
        <button class="btn btn-secondary" onclick="toggleDifferences()" id="toggleBtn">
            Show Only Differences
        </button>
        <button class="btn btn-primary" onclick="window.print()" style="margin-left: 10px;">
            Print
        </button>
    </div>
"""
    
    def _build_side_by_side_content(
        self, 
        file1: str, 
        file2: str, 
        page_comparisons: List[Dict]
    ) -> str:
        """Build side-by-side comparison content"""
        html = """
    <div class="comparison-container">
        <div class="side">
            <div class="side-header">📄 """ + file1 + """</div>
            <div class="side-content">
"""
        
        # Left side
        for page_data in page_comparisons:
            html += f'<div class="page-separator">Page {page_data["page_num"]}</div>\n'
            for diff in page_data.get('diff_data', []):
                line_type = diff['type']
                left_num = diff['left_line'] if diff.get('left_line') else ''
                left_text = self._escape_html(diff.get('left_text', ''))
                html += f'''<div class="line {line_type}">
                    <div class="line-number">{left_num}</div>
                    <div class="line-content">{left_text if left_text else "&nbsp;"}</div>
                </div>\n'''
        
        html += """
            </div>
        </div>
        <div class="side">
            <div class="side-header">📄 """ + file2 + """</div>
            <div class="side-content">
"""
        
        # Right side
        for page_data in page_comparisons:
            html += f'<div class="page-separator">Page {page_data["page_num"]}</div>\n'
            for diff in page_data.get('diff_data', []):
                line_type = diff['type']
                right_num = diff['right_line'] if diff.get('right_line') else ''
                right_text = self._escape_html(diff.get('right_text', ''))
                html += f'''<div class="line {line_type}">
                    <div class="line-number">{right_num}</div>
                    <div class="line-content">{right_text if right_text else "&nbsp;"}</div>
                </div>\n'''
        
        html += """
            </div>
        </div>
    </div>
"""
        return html
    
    def _build_footer_script(self) -> str:
        """Build footer with JavaScript"""
        return """
    <script>
        // Synchronized scrolling
        const leftContent = document.querySelector('.side:first-child .side-content');
        const rightContent = document.querySelector('.side:last-child .side-content');
        let isLeftScrolling = false, isRightScrolling = false;
        
        leftContent.addEventListener('scroll', function() {
            if (!isRightScrolling) {
                isLeftScrolling = true;
                rightContent.scrollTop = leftContent.scrollTop;
                setTimeout(() => { isLeftScrolling = false; }, 100);
            }
        });
        
        rightContent.addEventListener('scroll', function() {
            if (!isLeftScrolling) {
                isRightScrolling = true;
                leftContent.scrollTop = rightContent.scrollTop;
                setTimeout(() => { isRightScrolling = false; }, 100);
            }
        });
        
        // Toggle differences
        let showingOnlyDiffs = false;
        function toggleDifferences() {
            const btn = document.getElementById('toggleBtn');
            const lines = document.querySelectorAll('.line');
            
            showingOnlyDiffs = !showingOnlyDiffs;
            
            if (showingOnlyDiffs) {
                lines.forEach(line => {
                    if (line.classList.contains('equal')) {
                        line.style.display = 'none';
                    }
                });
                btn.textContent = 'Show All Lines';
                btn.classList.add('active');
            } else {
                lines.forEach(line => {
                    line.style.display = 'flex';
                });
                btn.textContent = 'Show Only Differences';
                btn.classList.remove('active');
            }
        }
    </script>
</body>
</html>
"""
    
    def _build_summary_header(self, stats: Dict) -> str:
        """Build summary report header"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Batch Comparison Summary</title>
    {self._get_summary_styles()}
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 SI REPORT VALIDATIONS</h1>
            <div class="header-info">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
        </div>
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Comparisons</div>
                <div class="stat-value info">{stats.get('files_compared', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Files with Differences</div>
                <div class="stat-value danger">{stats.get('files_with_differences', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Identical Files</div>
                <div class="stat-value success">{stats.get('files_compared', 0) - stats.get('files_with_differences', 0)}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Differences</div>
                <div class="stat-value warning">{stats.get('total_differences', 0)}</div>
            </div>
        </div>
        <div class="results-section">
            <h2 class="section-title">Comparison Results</h2>
            <div class="filter-buttons">
                <button class="btn btn-secondary active" onclick="filterResults('all')">Show All</button>
                <button class="btn btn-secondary" onclick="filterResults('different')">Show Only Differences</button>
                <button class="btn btn-secondary" onclick="filterResults('identical')">Show Only Identical</button>
            </div>
"""
    
    def _build_results_table(self, results: List[Dict]) -> str:
        """Build results table with expandable detailed differences"""
        html = """
            <table class="results-table" id="resultsTable">
                <thead>
                    <tr>
                        <th style="width:40px;">#</th>
                        <th>File 1</th>
                        <th>File 2</th>
                        <th style="width:100px;">Status</th>
                        <th style="width:80px;">Pages</th>
                        <th style="width:100px;">Differences</th>
                        <th style="width:80px;">+Lines</th>
                        <th style="width:80px;">-Lines</th>
                        <th style="width:80px;">~Lines</th>
                        <th style="width:120px;">Actions</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for idx, result in enumerate(results, 1):
            # Prepare data
            file1_name = result['file1'].name
            file2_name = result['file2'].name
            
            # Determine row class and status
            if result['has_differences']:
                status = '<span class="status-badge different">Different</span>'
                row_class = "different"
            else:
                status = '<span class="status-badge identical">Identical</span>'
                row_class = "identical"
            
            stats = result['stats']
            pages = stats.get('total_pages', 0)
            total_diffs = stats.get('total_diffs', 0)
            
            # Color code differences
            if total_diffs == 0:
                diff_class = "zero"
            elif total_diffs < 10:
                diff_class = "low"
            else:
                diff_class = "high"
            
            diffs = f'<span class="diff-count {diff_class}">{total_diffs}</span>'
            added = f'<span class="diff-count low">+{stats.get("lines_added", 0)}</span>' if stats.get("lines_added", 0) > 0 else "0"
            removed = f'<span class="diff-count low">-{stats.get("lines_removed", 0)}</span>' if stats.get("lines_removed", 0) > 0 else "0"
            changed = f'<span class="diff-count low">~{stats.get("lines_changed", 0)}</span>' if stats.get("lines_changed", 0) > 0 else "0"
            
            # Add show differences button
            if result['has_differences']:
                action_btn = f'<button class="btn btn-details" onclick="toggleDetails({idx})">Show All Changes</button>'
            else:
                action_btn = '<span style="color:#9ca3af;">—</span>'
            
            # Main row
            html += f"""
                    <tr class="result-row {row_class}">
                        <td>{idx}</td>
                        <td class="file-name">{file1_name}</td>
                        <td class="file-name">{file2_name}</td>
                        <td>{status}</td>
                        <td>{pages}</td>
                        <td>{diffs}</td>
                        <td>{added}</td>
                        <td>{removed}</td>
                        <td>{changed}</td>
                        <td>{action_btn}</td>
                    </tr>
"""
            
            # Expandable detailed differences row
            if result['has_differences']:
                detailed_html = self._build_detailed_differences(result, idx)
                html += f"""
                    <tr class="detail-row" id="detail-{idx}" style="display:none;">
                        <td colspan="10">
                            {detailed_html}
                        </td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
"""
        return html
    
    def _build_detailed_differences(self, result: Dict, idx: int) -> str:
        """Build detailed line-by-line differences with unified scrolling"""
        html = '<div class="detail-container">'
        
        # Header with simplified controls
        html += f'''
            <div class="detail-header">
                <h3>📄 {result['file1'].name} ↔ {result['file2'].name}</h3>
                <div>
                    <button class="btn btn-toggle" onclick="toggleAllLines({idx})" id="toggle-{idx}">Show All Lines</button>
                    <button class="btn btn-close" onclick="toggleDetails({idx})">Close</button>
                </div>
            </div>
        '''
        
        # Single unified comparison view
        html += f'<div class="unified-comparison" id="comparison-{idx}">'
        
        # Left side
        html += '<div class="comparison-side">'
        html += f'<div class="side-title">📄 Original: {result["file1"].name}</div>'
        html += '<div class="diff-content">'
        
        for page_data in result.get('page_comparisons', []):
            page_num = page_data['page_num']
            html += f'<div class="page-header">Page {page_num}</div>'
            
            for diff in page_data.get('diff_data', []):
                line_type = diff['type']
                left_num = diff.get('left_line', '')
                left_text = diff.get('left_text', '').strip()
                
                # Skip lines that are empty or just "None"
                if not left_text or left_text.lower() == 'none':
                    continue
                
                escaped_text = self._escape_html(left_text)
                
                # For changed lines, highlight character differences in red
                if line_type == 'changed':
                    right_text_raw = diff.get('right_text', '').strip()
                    if right_text_raw:
                        escaped_text = self._highlight_char_diff(left_text, right_text_raw)
                
                extra_class = 'equal-line' if line_type == 'equal' else ''
                display_style = 'display:none;' if line_type == 'equal' else ''
                
                html += f'<div class="diff-line {line_type} {extra_class}" style="{display_style}">'
                html += f'<span class="line-num">{left_num}</span>'
                html += f'<span class="line-text">{escaped_text}</span>'
                html += '</div>'
        
        html += '</div></div>'  # Close left side
        
        # Right side
        html += '<div class="comparison-side">'
        html += f'<div class="side-title">📄 Modified: {result["file2"].name}</div>'
        html += '<div class="diff-content">'
        
        for page_data in result.get('page_comparisons', []):
            page_num = page_data['page_num']
            html += f'<div class="page-header">Page {page_num}</div>'
            
            for diff in page_data.get('diff_data', []):
                line_type = diff['type']
                right_num = diff.get('right_line', '')
                right_text = diff.get('right_text', '').strip()
                
                # Skip lines that are empty or just "None"
                if not right_text or right_text.lower() == 'none':
                    continue
                
                escaped_text = self._escape_html(right_text)
                
                # For changed lines, highlight character differences in red
                if line_type == 'changed':
                    left_text_raw = diff.get('left_text', '').strip()
                    if left_text_raw:
                        escaped_text = self._highlight_char_diff(right_text, left_text_raw)
                
                extra_class = 'equal-line' if line_type == 'equal' else ''
                display_style = 'display:none;' if line_type == 'equal' else ''
                
                html += f'<div class="diff-line {line_type} {extra_class}" style="{display_style}">'
                html += f'<span class="line-num">{right_num}</span>'
                html += f'<span class="line-text">{escaped_text}</span>'
                html += '</div>'
        
        html += '</div></div>'  # Close right side
        html += '</div>'  # Close unified-comparison
        html += '</div>'  # Close detail-container
        
        return html
    
    def _build_summary_footer(self) -> str:
        """Build summary footer"""
        return """
        </div>
    </div>
    <script>
        function filterResults(filter) {
            const rows = document.querySelectorAll('.result-row');
            const detailRows = document.querySelectorAll('.detail-row');
            const buttons = document.querySelectorAll('.filter-buttons .btn-secondary');
            
            buttons.forEach(btn => btn.classList.remove('active'));
            event.target.classList.add('active');
            
            rows.forEach(row => {
                if (filter === 'all') {
                    row.style.display = '';
                } else if (filter === 'different' && row.classList.contains('different')) {
                    row.style.display = '';
                } else if (filter === 'identical' && row.classList.contains('identical')) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
            
            // Hide all detail rows when filtering
            detailRows.forEach(row => {
                row.style.display = 'none';
            });
        }
        
        function toggleDetails(idx) {
            const detailRow = document.getElementById('detail-' + idx);
            const isVisible = detailRow.style.display !== 'none';
            
            // Hide all other detail rows first
            document.querySelectorAll('.detail-row').forEach(row => {
                row.style.display = 'none';
            });
            
            // Toggle this one
            if (!isVisible) {
                detailRow.style.display = '';
                // Scroll to view
                setTimeout(() => {
                    detailRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 100);
            }
        }
        
        function toggleAllLines(idx) {
            const btn = document.getElementById('toggle-' + idx);
            const comparison = document.getElementById('comparison-' + idx);
            
            if (!comparison) return;
            
            const equalLines = comparison.querySelectorAll('.equal-line');
            const isShowingAll = btn.textContent === 'Show Only Differences';
            
            if (isShowingAll) {
                equalLines.forEach(line => line.style.display = 'none');
                btn.textContent = 'Show All Lines';
                btn.classList.remove('active');
            } else {
                equalLines.forEach(line => line.style.display = 'flex');
                btn.textContent = 'Show Only Differences';
                btn.classList.add('active');
            }
        }
        
        // Synchronized scrolling for side-by-side view
        document.addEventListener('DOMContentLoaded', function() {
            setupSyncScroll();
        });
        
        function setupSyncScroll() {
            const detailRows = document.querySelectorAll('.detail-row');
            detailRows.forEach((row, idx) => {
                const comparison = row.querySelector('.unified-comparison');
                if (!comparison) return;
                
                const sides = comparison.querySelectorAll('.diff-content');
                if (sides.length !== 2) return;
                
                const [left, right] = sides;
                let isLeftScrolling = false;
                let isRightScrolling = false;
                
                left.addEventListener('scroll', function() {
                    if (!isRightScrolling) {
                        isLeftScrolling = true;
                        right.scrollTop = left.scrollTop;
                        setTimeout(() => { isLeftScrolling = false; }, 100);
                    }
                });
                
                right.addEventListener('scroll', function() {
                    if (!isLeftScrolling) {
                        isRightScrolling = true;
                        left.scrollTop = right.scrollTop;
                        setTimeout(() => { isRightScrolling = false; }, 100);
                    }
                });
            });
        }
    </script>
</body>
</html>
"""
    
    def _highlight_char_diff(self, text1: str, text2: str) -> str:
        """
        Highlight character-level differences in red
        
        Args:
            text1: First text to compare
            text2: Second text to compare
            
        Returns:
            HTML with red highlighting on different characters
        """
        import difflib
        
        # Use difflib to find character differences
        matcher = difflib.SequenceMatcher(None, text1, text2)
        result = []
        
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # Characters are the same
                result.append(self._escape_html(text1[i1:i2]))
            elif tag == 'replace':
                # Characters changed - mark in red
                result.append(f'<mark class="char-diff">{self._escape_html(text1[i1:i2])}</mark>')
            elif tag == 'delete':
                # Characters deleted - mark in red with strikethrough
                result.append(f'<mark class="char-diff deleted">{self._escape_html(text1[i1:i2])}</mark>')
            elif tag == 'insert':
                # Characters added - show as green (only on right side)
                pass  # Don't show insertions on left side
        
        return ''.join(result)
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML special characters"""
        if not text:
            return ""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
    
    def _get_styles(self) -> str:
        """Get CSS styles for detailed comparison"""
        return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 30px; }
        .header h1 { font-size: 20px; margin-bottom: 8px; }
        .stats-bar { background: white; padding: 15px 30px; display: flex; gap: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); align-items: center; }
        .stat-item { display: flex; align-items: center; gap: 8px; }
        .stat-label { font-weight: 600; color: #666; font-size: 13px; }
        .stat-value { font-weight: bold; font-size: 16px; }
        .stat-value.added { color: #22c55e; }
        .stat-value.removed { color: #ef4444; }
        .stat-value.changed { color: #f59e0b; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-weight: 500; transition: all 0.2s; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .btn-secondary { background: #e5e7eb; color: #374151; }
        .btn-secondary:hover { background: #d1d5db; }
        .btn-secondary.active { background: #667eea; color: white; }
        .comparison-container { display: flex; height: calc(100vh - 150px); }
        .side { flex: 1; display: flex; flex-direction: column; background: white; border-right: 2px solid #e5e7eb; }
        .side:last-child { border-right: none; }
        .side-header { padding: 12px 15px; background: #f9fafb; border-bottom: 2px solid #e5e7eb; font-weight: 600; font-size: 13px; }
        .side-content { flex: 1; overflow-y: auto; font-family: 'Consolas', 'Monaco', monospace; font-size: 12px; line-height: 1.5; }
        .line { display: flex; padding: 2px 0; min-height: 20px; }
        .line-number { width: 50px; padding: 0 10px; text-align: right; color: #9ca3af; user-select: none; background: #f9fafb; border-right: 1px solid #e5e7eb; flex-shrink: 0; }
        .line-content { padding: 0 10px; flex: 1; white-space: pre-wrap; word-break: break-word; }
        .line.equal { background: white; }
        .line.added { background: #d1fae5; }
        .line.added .line-number { background: #a7f3d0; color: #065f46; font-weight: 600; }
        .line.deleted { background: #fee2e2; }
        .line.deleted .line-number { background: #fecaca; color: #991b1b; font-weight: 600; }
        .line.changed { background: #fef3c7; }
        .line.changed .line-number { background: #fde68a; color: #92400e; font-weight: 600; }
        .page-separator { background: #6366f1; color: white; padding: 8px 15px; font-weight: 600; font-size: 12px; position: sticky; top: 0; z-index: 10; }
    </style>
"""
    
    def _get_summary_styles(self) -> str:
        """Get CSS styles for summary report"""
        return """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; }
        .header h1 { font-size: 28px; margin-bottom: 10px; }
        .header-info { font-size: 14px; opacity: 0.9; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; padding: 30px; background: #f9fafb; }
        .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
        .stat-label { color: #6b7280; font-size: 14px; font-weight: 500; margin-bottom: 8px; }
        .stat-value { font-size: 32px; font-weight: bold; color: #1f2937; }
        .stat-value.success { color: #10b981; }
        .stat-value.warning { color: #f59e0b; }
        .stat-value.danger { color: #ef4444; }
        .stat-value.info { color: #3b82f6; }
        .results-section { padding: 30px; }
        .section-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; color: #1f2937; border-bottom: 2px solid #e5e7eb; padding-bottom: 10px; }
        .filter-buttons { margin: 20px 0; display: flex; gap: 10px; }
        .btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; }
        .btn-secondary { background: #e5e7eb; color: #374151; }
        .btn-secondary:hover { background: #d1d5db; }
        .btn-secondary.active { background: #667eea; color: white; }
        .btn-primary { background: #667eea; color: white; }
        .btn-primary:hover { background: #5568d3; }
        .results-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .results-table th { background: #f9fafb; padding: 12px; text-align: left; font-weight: 600; color: #374151; border-bottom: 2px solid #e5e7eb; font-size: 13px; }
        .results-table td { padding: 12px; border-bottom: 1px solid #e5e7eb; font-size: 13px; }
        .results-table tr:hover { background: #f9fafb; }
        .file-name { font-family: 'Consolas', monospace; font-size: 12px; color: #4b5563; }
        .status-badge { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 11px; font-weight: 600; }
        .status-badge.identical { background: #d1fae5; color: #065f46; }
        .status-badge.different { background: #fee2e2; color: #991b1b; }
        
        /* STRONG RED highlighting for rows with differences - very visible! */
        .result-row.different { 
            background-color: #fca5a5; 
            border-left: 5px solid #dc2626; 
            box-shadow: 0 0 0 1px #fca5a5;
        }
        .result-row.different:hover { 
            background-color: #f87171; 
            box-shadow: 0 0 8px rgba(220, 38, 38, 0.3);
        }
        .result-row.identical { 
            background-color: #d1fae5; 
            border-left: 5px solid #10b981; 
        }
        .result-row.identical:hover { 
            background-color: #a7f3d0; 
        }
        
        /* Make difference counts bold and red in mismatch rows */
        .result-row.different .diff-count { font-weight: 700; color: #991b1b; }
        
        /* Make "Different" badge more prominent */
        .result-row.different .status-badge { 
            background: #dc2626; 
            color: white; 
            font-weight: 700; 
            padding: 6px 12px;
            border-radius: 4px;
        }
        .status-badge.missing { background: #fef3c7; color: #92400e; }
        .diff-count { font-weight: 600; }
        .diff-count.zero { color: #10b981; }
        .diff-count.low { color: #f59e0b; }
        .diff-count.high { color: #ef4444; }
        .btn-details { padding: 6px 12px; font-size: 12px; background: #667eea; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
        .btn-details:hover { background: #5568d3; }
        .btn-toggle { padding: 6px 12px; font-size: 12px; background: #10b981; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; margin-right: 8px; }
        .btn-toggle:hover { background: #059669; }
        .btn-toggle.active { background: #f59e0b; }
        .btn-close { padding: 6px 12px; font-size: 12px; background: #ef4444; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: 500; }
        .btn-close:hover { background: #dc2626; }
        .detail-row td { padding: 0 !important; background: #f9fafb; }
        .detail-container { padding: 0; background: white; }
        .detail-header { display: flex; justify-content: space-between; align-items: center; padding: 15px 20px; margin-bottom: 0; border-bottom: 2px solid #e5e7eb; background: #f9fafb; }
        .detail-header h3 { margin: 0; color: #374151; font-size: 15px; font-weight: 600; }
        
        /* Unified comparison with single scrollbar */
        .unified-comparison { display: grid; grid-template-columns: 1fr 1fr; height: 70vh; max-height: 700px; overflow: hidden; border: 1px solid #e5e7eb; }
        .comparison-side { display: flex; flex-direction: column; overflow: hidden; border-right: 1px solid #e5e7eb; }
        .comparison-side:last-child { border-right: none; }
        .side-title { background: #374151; color: white; padding: 12px 15px; font-weight: 600; font-size: 13px; flex-shrink: 0; }
        .diff-content { flex: 1; overflow-y: auto; font-family: 'Consolas', 'Monaco', monospace; font-size: 13px; line-height: 1.6; background: #fefefe; }
        
        /* Synchronized scrolling */
        .unified-comparison .diff-content { scrollbar-width: thin; scrollbar-color: #9ca3af #f3f4f6; }
        .unified-comparison .diff-content::-webkit-scrollbar { width: 8px; }
        .unified-comparison .diff-content::-webkit-scrollbar-track { background: #f3f4f6; }
        .unified-comparison .diff-content::-webkit-scrollbar-thumb { background: #9ca3af; border-radius: 4px; }
        .unified-comparison .diff-content::-webkit-scrollbar-thumb:hover { background: #6b7280; }
        
        .page-header { background: #6366f1; color: white; padding: 8px 15px; font-weight: 600; font-size: 12px; position: sticky; top: 0; z-index: 10; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .diff-line { display: flex; padding: 6px 0; min-height: 28px; border-bottom: 1px solid #f3f4f6; }
        .diff-line.added { background: #d1fae5; border-left: 3px solid #10b981; }
        .diff-line.deleted { background: #fee2e2; border-left: 3px solid #ef4444; }
        .diff-line.changed { background: #fef3c7; border-left: 3px solid #f59e0b; }
        .diff-line.equal { background: white; border-left: 3px solid transparent; }
        .line-num { width: 50px; padding: 0 10px; text-align: right; color: #6b7280; font-weight: 600; flex-shrink: 0; background: rgba(249,250,251,0.8); font-size: 11px; }
        .line-text { padding: 0 15px; flex: 1; word-break: break-word; white-space: pre-wrap; }
        
        /* Red text highlighting for character differences */
        .char-diff {
            color: #dc2626;
            font-weight: 700;
        }
    </style>
"""