"""
Hugging Face Space Deployment Script.
Automates code synchronization while excluding build artifacts and virtual environment binaries.
"""
from huggingface_hub import HfApi
api = HfApi()
print("Uploading codebase exclusively (skipping massive .venv binaries)...")
api.upload_folder(
    folder_path=".",
    repo_id="Gurleen12/s-rmm-benchmark",
    repo_type="space",
    ignore_patterns=["venv/*", "venv*", ".venv/*", ".venv*", "__pycache__/*", "*.pyc", "*.log", ".git/*", "dump*.txt", "dumppush.py"]
)
print("SUCCESS! File upload completed perfectly!")
