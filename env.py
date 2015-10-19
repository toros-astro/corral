import os
os.environ.setdefault("CORRAL_SETTINGS_MODULE", "toritos.settings")
from corral.core import setup_environment
setup_environment()

