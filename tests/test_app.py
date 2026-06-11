import csv
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_DIR = Path(__file__).resolve().parents[1]
MAIN_PY = PROJECT_DIR / "main.py"


class HouseholdAccountsAppTest(unittest.TestCase):
    def run_app(self, user_input, workdir):
        return subprocess.run(
            [sys.executable, str(MAIN_PY)],
            cwd=workdir,
            input=user_input,
            text=True,
            capture_output=True,
            check=True,
        )

    def write_records(self, workdir, rows):
        records_file = Path(workdir) / "records.csv"

        with records_file.open("w", encoding="utf-8", newline="") as file:
            fieldnames = ["date", "type", "category", "amount", "memo", "created_at"]
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def read_records(self, workdir):
        records_file = Path(workdir) / "records.csv"

        with records_file.open("r", encoding="utf-8", newline="") as file:
            return list(csv.DictReader(file))

    def test_amount_must_be_positive_number(self):
        with tempfile.TemporaryDirectory() as workdir:
            result = self.run_app(
                "1\n2026-06-11\n給料\n-100\nabc\n100\nメモ\n3\n8\n",
                workdir,
            )

        self.assertIn("金額は1円以上で入力してください。", result.stdout)
        self.assertIn("金額は数字で入力してください。", result.stdout)
        self.assertIn("100円", result.stdout)

    def test_show_category_summary(self):
        with tempfile.TemporaryDirectory() as workdir:
            self.write_records(
                workdir,
                [
                    {
                        "date": "2026-06-01",
                        "type": "income",
                        "category": "給料",
                        "amount": "200000",
                        "memo": "6月分",
                        "created_at": "2026-06-11 10:00:00",
                    },
                    {
                        "date": "2026-06-02",
                        "type": "expense",
                        "category": "食費",
                        "amount": "1200",
                        "memo": "昼食",
                        "created_at": "2026-06-11 10:00:00",
                    },
                    {
                        "date": "2026-06-03",
                        "type": "expense",
                        "category": "食費",
                        "amount": "800",
                        "memo": "夕食",
                        "created_at": "2026-06-11 10:00:00",
                    },
                ],
            )

            result = self.run_app("5\n2026-06\n8\n", workdir)

        self.assertIn("--- 2026-06 のカテゴリ別集計 ---", result.stdout)
        self.assertIn("給料: 200,000円", result.stdout)
        self.assertIn("食費: 2,000円", result.stdout)

    def test_edit_record(self):
        with tempfile.TemporaryDirectory() as workdir:
            self.write_records(
                workdir,
                [
                    {
                        "date": "2026-06-01",
                        "type": "expense",
                        "category": "食費",
                        "amount": "1200",
                        "memo": "昼食",
                        "created_at": "2026-06-11 10:00:00",
                    }
                ],
            )

            result = self.run_app(
                "6\n1\n2026-06-02\n交通費\n1500\n電車\n3\n8\n",
                workdir,
            )
            records = self.read_records(workdir)

        self.assertIn("更新しました。", result.stdout)
        self.assertIn("2026-06-02 | 支出 | 交通費 | 1500円 | 電車", result.stdout)
        self.assertEqual(records[0]["date"], "2026-06-02")
        self.assertEqual(records[0]["category"], "交通費")
        self.assertEqual(records[0]["amount"], "1500")
        self.assertEqual(records[0]["memo"], "電車")
        self.assertEqual(records[0]["created_at"], "2026-06-11 10:00:00")


if __name__ == "__main__":
    unittest.main()
