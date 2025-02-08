# Databricks notebook source
!pip install pytest -q
dbutils.library.restartPython()

# COMMAND ----------

dbutils.library.restartPython()  # Restart python also resets notebook state

import pytest
import os
import sys

# Skip writing pyc files on a readonly filesystem.
sys.dont_write_bytecode = True

# Run pytest.
retcode = pytest.main(["tests", "-p", "no:cacheprovider"])

# Fail the cell execution if there are any test failures.
assert retcode == 0, "The pytest invocation failed. See the log for details."

# COMMAND ----------


