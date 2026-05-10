with open("backend/app/api/simulation.py") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "send_from_directory(" in l:
        print("".join(lines[i-2:i+5]))
