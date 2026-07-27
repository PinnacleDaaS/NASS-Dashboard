import subprocess
import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIPELINE_DIR = os.path.join(PROJECT_ROOT, "pipeline")

def run_step(name, command):
    print(f"\n==================================================")
    print(f"▶ Step: {name}")
    print(f"==================================================")
    try:
        res = subprocess.run(command, cwd=PROJECT_ROOT, check=True)
        print(f"[OK] {name} completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"[Warning] {name} encountered an error or non-zero exit code ({e.returncode}). Continuing pipeline execution...")

def main():
    print("🚀 Starting Master NASS Data Pipeline Orchestrator...")
    
    # 1. Scrape PLAC Bills API (resumable / refresh mode)
    run_step("1. Live Scrape PLAC API", [sys.executable, os.path.join(PIPELINE_DIR, "scrape_plac_bills.py"), "--refresh"])

    # 2. Clean Scraped Bills Cache
    run_step("2. Clean Bills Cache", [sys.executable, os.path.join(PIPELINE_DIR, "clean_plac_bills.py")])

    # 3. Export Data to Frontend JSON
    run_step("3. Export Frontend JSON", [sys.executable, os.path.join(PIPELINE_DIR, "export_data.py")])

    # 4. Validate Pipeline Data Integrity
    run_step("4. Validate Pipeline Integrity", [sys.executable, os.path.join(PIPELINE_DIR, "validate_pipeline.py")])

    print("\n🎉 Master Data Pipeline Orchestration Finished!")

if __name__ == "__main__":
    main()
