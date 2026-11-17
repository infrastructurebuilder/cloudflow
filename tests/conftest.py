import os
import tempfile

# Importing the workflow modules loads matplotlib and Prefect. Tests have no
# display, and must not write Prefect's settings into the user's home.
os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("PREFECT_HOME", tempfile.mkdtemp(prefix="cloudflow-tests-prefect-"))
