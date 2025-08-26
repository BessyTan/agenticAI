#!/usr/bin/env python3

import json

# Read the notebook file
with open('tan_project2_customerServiceAssistant_3agents_rag.ipynb', 'r', encoding='utf-8') as f:
    notebook = json.load(f)

# Fix the problematic print statement
for cell in notebook['cells']:
    if 'source' in cell:
        for i, line in enumerate(cell['source']):
            if 'print("Customer assistant: Thank you! Have a great day!")' in line:
                # Replace the problematic line with the correct one
                cell['source'][i] = '            print("Customer assistant: Thank you! Have a great day!")\n'
                print(f"Fixed line: {cell['source'][i]}")

# Write the corrected notebook
with open('tan_project2_customerServiceAssistant_3agents_rag.ipynb', 'w', encoding='utf-8') as f:
    json.dump(notebook, f, indent=1, ensure_ascii=False)

print("Notebook fixed successfully!") 