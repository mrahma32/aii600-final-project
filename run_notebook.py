"""Execute the project notebook using this interpreter's kernel."""
from pathlib import Path
import sys
import os
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

root = Path(__file__).resolve().parent
runtime = root / '.venv' / 'notebook-runtime'
runtime.mkdir(exist_ok=True)
for key, subdir in [('IPYTHONDIR', 'ipython'), ('JUPYTER_CONFIG_DIR', 'config'), ('JUPYTER_DATA_DIR', 'data'), ('JUPYTER_RUNTIME_DIR', 'runtime'), ('MPLCONFIGDIR', 'matplotlib')]:
    location = runtime / subdir
    location.mkdir(exist_ok=True)
    os.environ[key] = str(location)
nb = nbformat.read(root/'analysis.ipynb', as_version=4)
km = KernelManager(kernel_name='python3')
km.kernel_spec.argv = [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}']
client = NotebookClient(nb, km=km, timeout=300, resources={'metadata': {'path':str(root)}})
try:
    client.execute()
finally:
    nbformat.write(nb, root/'analysis.ipynb')
print('Executed', sum(c.cell_type == 'code' for c in nb.cells), 'code cells; outputs saved.')
