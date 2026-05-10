import sys

def extract(filepath, search_str, context_lines=10):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        if search_str in line:
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            print(f"--- {filepath} (lines {start+1}-{end}) ---")
            print("".join(lines[start:end]))
            print("-" * 40)

extract('backend/app/services/report_agent.py', 'def _get_report_folder')
extract('backend/app/services/report_agent.py', 'def _get_report_markdown_path')
extract('backend/app/api/report.py', 'def download_report', context_lines=40)
extract('backend/app/services/simulation_manager.py', 'def _get_simulation_dir')
extract('backend/app/api/simulation.py', 'def download_simulation_config', context_lines=30)
extract('backend/app/api/simulation.py', 'def download_simulation_script', context_lines=30)
