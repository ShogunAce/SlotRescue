"""Package only Git-tracked deliverables. Excludes .private and local databases."""
import subprocess
from pathlib import Path
root = Path(__file__).resolve().parents[1]
out = root / 'dist'
out.mkdir(exist_ok=True)
subprocess.run(['git', 'archive', '--format=zip', '--prefix=slotrescue/', '-o', str(out / 'slotrescue-source.zip'), 'HEAD'], cwd=root, check=True)
print(out / 'slotrescue-source.zip')
