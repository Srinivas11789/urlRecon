# Main file execution
import sys

if sys.path[0]:
   sys.path.insert(0,sys.path[0]+"/../urlrecon/")
else:
   sys.path.insert(0,"/../urlrecon/")

import subprocess

def test_work_flow():
    assert "Successfully" in (subprocess.check_output(["python", sys.path[0]+"main.py", "f", sys.path[0]+"/examples/url_to_test.txt"]))
