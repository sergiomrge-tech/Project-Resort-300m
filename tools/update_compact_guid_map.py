"""Extend existing Unity asset GUID inventory for the new compact scene."""
import re
from pathlib import Path
root=Path(__file__).resolve().parents[1]
assets=root/"UnityProject/Assets"
dest=root/"evidence/guid_resolution.tsv"
lines=dest.read_text(encoding="utf8").splitlines()
known={line.split("\t",1)[0] for line in lines if "\t" in line}
new=0
for meta in sorted(assets.rglob("*.meta")):
 asset=Path(str(meta)[:-5])
 if not asset.is_file():continue
 m=re.search(r"^guid: ([a-f0-9]{32})$",meta.read_text(encoding="utf-8-sig"),re.M)
 if not m:raise ValueError("NO_GUID "+str(meta))
 guid=m.group(1)
 if guid in known:continue
 lines.append(guid+"\t"+asset.relative_to(root/"UnityProject").as_posix())
 known.add(guid);new+=1
dest.write_text("\n".join(lines)+"\n",encoding="utf-8",newline="\n")
print("R15_COMPACT_GUID_MAP_UPDATED",new)
