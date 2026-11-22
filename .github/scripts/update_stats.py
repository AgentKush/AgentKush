"""Refresh the Icarus mod numbers in the profile README from a checkout of AgentKush/Icarus-mods.

usage: python update_stats.py <Icarus-mods checkout> <README.md>
mods    = entries in modinfo.json
entries = rows across every <Mod>/<Mod>.EXMOD
recipes = Crafting-D_ProcessorRecipes rows across those EXMODs
"""
import glob
import json
import os
import re
import sys

src, readme = sys.argv[1], sys.argv[2]
mods = len(json.load(open(os.path.join(src, "modinfo.json"), encoding="utf-8-sig"))["mods"])
entries = recipes = 0
for path in glob.glob(os.path.join(src, "*", "*.EXMOD")):
    for block in json.load(open(path, encoding="utf-8-sig")).get("Rows", []):
        n = len(block.get("File_Items", []))
        entries += n
        if block.get("CurrentFile", "").endswith("D_ProcessorRecipes.json"):
            recipes += n


def comma(n):
    return f"{n:,}"


def url(n):
    return comma(n).replace(",", "%2C")


subs = [
    (r"%3E\+[0-9%C]+\+MODS\+DEPLOYED", f"%3E+{mods}+MODS+DEPLOYED"),
    (r"%3E\+[0-9%C]+\+DATA\+ENTRIES", f"%3E+{url(entries)}+DATA+ENTRIES"),
    (r"%3E\+[0-9%C]+\+CRAFTING\+RECIPES", f"%3E+{url(recipes)}+CRAFTING+RECIPES"),
    (r"(mods_deployed:\s*)\d+", rf"\g<1>{mods}"),
    (r'(data_entries_modified:\s*)"[\d,]+"', rf'\g<1>"{comma(entries)}"'),
    (r'(crafting_recipes:\s*)"[\d,]+"', rf'\g<1>"{comma(recipes)}"'),
    (r"<!--mods-->[\d,]+<!--/mods-->", f"<!--mods-->{mods}<!--/mods-->"),
    (r"<!--entries-->[\d,]+<!--/entries-->", f"<!--entries-->{comma(entries)}<!--/entries-->"),
    (r"<!--recipes-->[\d,]+<!--/recipes-->", f"<!--recipes-->{comma(recipes)}<!--/recipes-->"),
]
text = open(readme, encoding="utf-8").read()
new = text
for pattern, repl in subs:
    new, count = re.subn(pattern, repl, new)
    if count == 0:
        sys.exit(f"pattern not found in README: {pattern}")
if new != text:
    open(readme, "w", encoding="utf-8", newline="\n").write(new)
print(f"{mods} mods, {comma(entries)} entries, {comma(recipes)} recipes; README {'updated' if new != text else 'unchanged'}")
