import os
import json
import urllib.request
from concurrent.futures import ThreadPoolExecutor

# Mendeley Data 직접 다운로드 (Kaggle API 계정/토큰 불필요)
DATASET_ID = "rwh8kjzdch"
VERSION = 3
DATA_DIR = os.path.join(os.getcwd(), "Data", "Resistance Spot Welding Insights")
IMG_DIR = os.path.join(DATA_DIR, "ir_images")
os.makedirs(IMG_DIR, exist_ok=True)

FILES_API = f"https://data.mendeley.com/api/datasets/{DATASET_ID}/files?version={VERSION}"


def fetch_file_list():
    with urllib.request.urlopen(FILES_API) as resp:
        return json.load(resp)


def download(filename, url, dest_dir):
    dest_path = os.path.join(dest_dir, filename)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        return
    urllib.request.urlretrieve(url, dest_path)


def main():
    files = fetch_file_list()
    print(f"[알림] 총 {len(files)}개 파일 확인 (CSV 1개 + IR 이미지 {len(files) - 1}개)")

    csv_jobs, img_jobs = [], []
    for f in files:
        url = f["content_details"]["download_url"]
        if f["filename"].lower().endswith(".csv"):
            csv_jobs.append((f["filename"], url, DATA_DIR))
        else:
            img_jobs.append((f["filename"], url, IMG_DIR))

    for name, url, dest in csv_jobs:
        download(name, url, dest)
        print(f"[완료] {name} -> {dest}")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(download, name, url, dest) for name, url, dest in img_jobs]
        for fut in futures:
            fut.result()
    print(f"[완료] IR 이미지 {len(img_jobs)}개 -> {IMG_DIR}")


if __name__ == "__main__":
    main()
