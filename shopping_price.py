import os
import csv
import tkinter as tk
from tkinter import filedialog
from datetime import datetime

def select_input_folder():
    """Use GUI to select input folder"""
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select Folder Containing Price Files")
    return folder_path


def read_price_files(folder_path):
    """
    Reads all .txt and .csv files inside folder_path.
    Returns a list of (item, price, source_file)
    """
    all_items = []

    for filename in os.listdir(folder_path):
        if filename.endswith(".txt") or filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    reader = csv.reader(f)

                    for row in reader:
                        if len(row) >= 2:
                            item = row[0].strip()
                            price = row[1].strip().replace(",", "")

                            if price.isdigit():
                                price = int(price)
                                all_items.append((item, price, filename))

            except Exception as e:
                print(f"Error reading {filename}: {e}")

    return all_items


def save_result(data):
    """
    Saves sorted data to a CSV file
    """
    output_filename = f"price_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Item", "Price", "Source File"])

        for row in data:
            writer.writerow(row)

    print(f"\n✔ 결과 저장됨: {output_filename}\n")


def main():
    print("📂 가격 파일이 들어있는 폴더를 선택하세요.")
    folder_path = select_input_folder()

    if not folder_path:
        print("❌ 폴더가 선택되지 않았습니다. 프로그램 종료.")
        return

    print("\n📄 파일 읽는 중...")
    data = read_price_files(folder_path)

    if not data:
        print("❌ 불러온 데이터가 없습니다.")
        return

    # 가격 기준 오름차순 정렬
    data.sort(key=lambda x: x[1])

    save_result(data)

    print("🎉 작업 완료!")


if __name__ == "__main__":
    main()
