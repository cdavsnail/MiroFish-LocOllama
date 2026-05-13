import sys

def extract(filepath, start, end, outpath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    with open(outpath, 'w') as f:
        f.writelines(lines[start-1:end])

extract('backend/app/services/report_agent.py', 1880, 1920, 'report_agent_small.txt')
