# Genshin Artifact Salvaging Helper

This repository contains the scripts used to populate the build data used by the
[Genshin Artifact Salvaging Helper sheet](https://docs.google.com/spreadsheets/d/1CnuhbPHdxMnmn9aGdeedj4wBqZfJzr_kEEAdlPr1iog/edit).
Build data is scraped from the [Genshin Helper Team Builds Sheet](https://docs.google.com/spreadsheets/d/e/2PACX-1vRq-sQxkvdbvaJtQAGG6iVz2q2UN9FCKZ8Mkyis87QHFptcOU3ViLh0_PJyMxFSgwJZrd10kbYpQFl1/pubhtml#gid=2001372201).

## Updating the sheet
1. Use `uv sync` to install any required dependencies
2. Run all the cells in the `gi_helper_webscraping.ipynb` notebook
3. Import the generated `gi_rsh_output_full_{version}.csv` into the GI Helper Team builds tab of the spreadsheet
4. If new sets have been added to the game since the sheet was last updated, add appropriate rows to all tabs with an 
artifact list