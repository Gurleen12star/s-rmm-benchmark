import subprocess
try:
    print(subprocess.check_output(['.\\venv\\Scripts\\openenv.exe', 'push', '--repo-id', 'Gurleen12/s-rmm-benchmark'], text=True, stderr=subprocess.STDOUT))
except subprocess.CalledProcessError as e:
    print("FAILED:")
    print(e.output)
