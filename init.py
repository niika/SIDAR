
import subprocess
import sys
import os
 
# path to python.exe
python_exe = os.listdir(os.path.join(sys.prefix, "bin"))[0]
print("Python:",python_exe)
python_exe = os.path.join(sys.prefix, 'bin', python_exe)
print(python_exe)
# upgrade pip
subprocess.call([python_exe, "-m", "ensurepip"])
subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
 
# install required packages
subprocess.call([python_exe, "-m", "pip", "install", "numpy"])
subprocess.call([python_exe, "-m", "pip", "install", "pyyaml"])

print("required libraries installed")