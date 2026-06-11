import csv
import os
import re
from datetime import datetime

FILE_NAME = "records.csv"
BACK_COMMAND = "0"

records = []


def get_current_datetime():
    """現在日時をYYYY-MM-DD HH:MM:SS形式で取得する"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def input_with_back(prompt):
    """0が入力された場合はメニューに戻る"""
    value = input(f"{prompt}（{BACK_COMMAND}でメニューに戻る）: ")

    if value == BACK_COMMAND:
        print("メニューに戻ります。")
        return None

    return value


def input_date():
    """YYYY-MM-DD形式の日付を入力する"""
    while True:
        date = input_with_back("日付を入力してください 例: 2026-05-04")

        if date is None:
            return None

        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                raise ValueError
            datetime.strptime(date, "%Y-%m-%d")
            return date
        except ValueError:
            print("日付はYYYY-MM-DD形式で入力してください。")


def input_month():
    """YYYY-MM形式の年月を入力する"""
    while True:
        month = input_with_back("集計したい年月を入力してください 例: 2026-05")

        if month is None:
            return None

        try:
            if not re.fullmatch(r"\d{4}-\d{2}", month):
                raise ValueError
            datetime.strptime(month, "%Y-%m")
            return month
        except ValueError:
            print("年月はYYYY-MM形式で入力してください。")


def input_amount():
    """1以上の金額を入力する"""
    while True:
        try:
            amount_text = input_with_back("金額を入力してください")

            if amount_text is None:
                return None

            amount = int(amount_text)

            if amount <= 0:
                print("金額は1円以上で入力してください。")
                continue

            return amount
        except ValueError:
            print("金額は数字で入力してください。")


def input_optional_date(current_date):
    """編集用の日付を入力する。空欄の場合は現在値を使う"""
    while True:
        date = input_with_back(
            f"日付を入力してください 例: 2026-05-04（現在: {current_date}、空欄で変更なし）"
        )

        if date is None:
            return None
        if date == "":
            return current_date

        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                raise ValueError
            datetime.strptime(date, "%Y-%m-%d")
            return date
        except ValueError:
            print("日付はYYYY-MM-DD形式で入力してください。")


def input_optional_amount(current_amount):
    """編集用の金額を入力する。空欄の場合は現在値を使う"""
    while True:
        try:
            amount_text = input_with_back(
                f"金額を入力してください（現在: {current_amount}円、空欄で変更なし）"
            )

            if amount_text is None:
                return None
            if amount_text == "":
                return current_amount

            amount = int(amount_text)

            if amount <= 0:
                print("金額は1円以上で入力してください。")
                continue

            return amount
        except ValueError:
            print("金額は数字で入力してください。")


def load_records():
    """CSVファイルからデータを読み込む"""
    if not os.path.exists(FILE_NAME):
        return

    with open(FILE_NAME, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["amount"] = int(row["amount"])
            row.setdefault("created_at", "")
            records.append(row)


def save_records():
    """CSVファイルにデータを日付順で保存する"""
    sorted_records = sorted(records, key=lambda record: record["date"])

    with open(FILE_NAME, "w", encoding="utf-8", newline="") as file:
        fieldnames = ["date", "type", "category", "amount", "memo", "created_at"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        writer.writerows(sorted_records)


def add_record(record_type):
    """収入または支出を登録する"""
    date = input_date()

    if date is None:
        return

    category = input_with_back("カテゴリを入力してください 例: 食費, 給料, 交通費")

    if category is None:
        return

    amount = input_amount()

    if amount is None:
        return

    memo = input_with_back("メモを入力してください")

    if memo is None:
        return

    record = {
        "date": date,
        "type": record_type,
        "category": category,
        "amount": amount,
        "memo": memo,
        "created_at": get_current_datetime()
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
            f"{record['memo']} | "
            f"登録日時: {record.get('created_at', '')}"
        )


def show_monthly_summary():
    """指定した月の収入・支出・収支を表示する"""
    if not records:
        print("データがありません。")
        return

    target_month = input_month()

    if target_month is None:
        return

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


def show_category_summary():
    """指定した月のカテゴリ別集計を表示する"""
    if not records:
        print("データがありません。")
        return

    target_month = input_month()

    if target_month is None:
        return

    income_by_category = {}
    expense_by_category = {}

    for record in records:
        if not record["date"].startswith(target_month):
            continue

        category = record["category"]

        if record["type"] == "income":
            income_by_category[category] = (
                income_by_category.get(category, 0) + record["amount"]
            )
        elif record["type"] == "expense":
            expense_by_category[category] = (
                expense_by_category.get(category, 0) + record["amount"]
            )

    print(f"\n--- {target_month} のカテゴリ別集計 ---")

    if income_by_category:
        print("\n収入")
        for category, amount in sorted(income_by_category.items()):
            print(f"{category}: {amount:,}円")
    else:
        print("\n収入データはありません。")

    if expense_by_category:
        print("\n支出")
        for category, amount in sorted(expense_by_category.items()):
            print(f"{category}: {amount:,}円")
    else:
        print("\n支出データはありません。")


def edit_record():
    """登録データを編集する"""
    if not records:
        print("データがありません。")
        return

    show_records()

    while True:
        try:
            edit_text = input_with_back("編集したい番号を入力してください")

            if edit_text is None:
                return

            edit_number = int(edit_text)

            if 1 <= edit_number <= len(records):
                break

            print("存在する番号を入力してください。")
        except ValueError:
            print("数字で入力してください。")

    record = records[edit_number - 1]

    date = input_optional_date(record["date"])

    if date is None:
        return

    category = input_with_back(
        f"カテゴリを入力してください（現在: {record['category']}、空欄で変更なし）"
    )

    if category is None:
        return
    if category == "":
        category = record["category"]

    amount = input_optional_amount(record["amount"])

    if amount is None:
        return

    memo = input_with_back(f"メモを入力してください（現在: {record['memo']}、空欄で変更なし）")

    if memo is None:
        return
    if memo == "":
        memo = record["memo"]

    record["date"] = date
    record["category"] = category
    record["amount"] = amount
    record["memo"] = memo

    print("更新しました。")


def delete_record():
    """登録データを削除する"""
    if not records:
        print("データがありません。")
        return

    show_records()

    while True:
        try:
            delete_text = input_with_back("削除したい番号を入力してください")

            if delete_text is None:
                return

            delete_number = int(delete_text)

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
    print("5. カテゴリ別の合計を表示")
    print("6. 登録データを編集")
    print("7. 登録データを削除")
    print("8. 保存して終了")


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
            show_category_summary()
        elif choice == "6":
            edit_record()
        elif choice == "7":
            delete_record()
        elif choice == "8":
            save_records()
            print("保存しました。終了します。")
            break
        else:
            print("1〜8の番号を入力してください。")


main()
