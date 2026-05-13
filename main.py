import csv
import os

FILE_NAME = "records.csv"

records = []


def load_records():
    """CSVファイルからデータを読み込む"""
    if not os.path.exists(FILE_NAME):
        return

    with open(FILE_NAME, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["amount"] = int(row["amount"])
            records.append(row)


def save_records():
    """CSVファイルにデータを日付順で保存する"""
    sorted_records = sorted(records, key=lambda record: record["date"])

    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["date", "type", "category", "amount", "memo"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(sorted_records)


def add_record(record_type):
    """収入または支出を登録する"""
    date = input("日付を入力してください 例: 2026-05-04: ")
    category = input("カテゴリを入力してください 例: 食費, 給料, 交通費: ")

    while True:
        try:
            amount = int(input("金額を入力してください: "))
            break
        except ValueError:
            print("金額は数字で入力してください。")

    memo = input("メモを入力してください: ")

    record = {
        "date": date,
        "type": record_type,
        "category": category,
        "amount": amount,
        "memo": memo
    }

    records.append(record)
    print("登録しました。")


def show_records():
    """登録データの一覧を表示する"""
    if not records:
        print("データがありません。")
        return

    print("\n--- 登録データ一覧 ---")

    for i, record in enumerate(records, start=1):
        if record["type"] == "income":
            record_type = "収入"
        else:
            record_type = "支出"

        print(
            f"{i}. {record['date']} | "
            f"{record_type} | "
            f"{record['category']} | "
            f"{record['amount']}円 | "
            f"{record['memo']}"
        )
def show_monthly_summary():
    """指定した月の収入・支出・収支を表示する"""
    if not records:
        print("データがありません。")
        return

    target_month = input("集計したい年月を入力してください 例: 2026-05: ")

    income_total = 0
    expense_total = 0

    for record in records:
        # 日付が target_month で始まるデータだけ集計する
        if record["date"].startswith(target_month):
            if record["type"] == "income":
                income_total += record["amount"]
            elif record["type"] == "expense":
                expense_total += record["amount"]

    balance = income_total - expense_total

    print(f"\n--- {target_month} の集計 ---")
    print(f"収入合計: {income_total:,}円")
    print(f"支出合計: {expense_total:,}円")
    print(f"収支: {balance:,}円")

def delete_record():
    """登録データを削除する"""
    if not records:
        print("データがありません。")
        return

    show_records()

    while True:
        try:
            delete_number = int(input("削除したい番号を入力してください: "))

            if 1 <= delete_number <= len(records):
                deleted_record = records.pop(delete_number - 1)
                print(
                    f"削除しました: {deleted_record['date']} | "
                    f"{deleted_record['category']} | "
                    f"{deleted_record['amount']}円"
                )
                break
            else:
                print("存在する番号を入力してください。")

        except ValueError:
            print("数字で入力してください。")


def show_menu():
    """メニューを表示する"""
    print("\n家計簿アプリ")
    print("1. 収入を登録")
    print("2. 支出を登録")
    print("3. 一覧を表示")
    print("4. 月ごとの合計を表示")
    print("5. 登録データを削除")
    print("6. 保存して終了")


def main():
    load_records()

    while True:
        show_menu()
        choice = input("番号を選んでください: ")

        if choice == "1":
            add_record("income")
        elif choice == "2":
            add_record("expense")
        elif choice == "3":
            show_records()
        elif choice == "4":
            show_monthly_summary()
        elif choice == "5":
            delete_record()
        elif choice == "6":
            save_records()
            print("保存しました。終了します。")
            break
        else:
            print("1〜6の番号を入力してください。")


main()