"""
e-Stat API 人口推計スクリプト
- データ: 人口推計 都道府県別 各年10月1日現在（年次）
- 期間:   最新から10年分（データがない場合はできるだけ過去まで遡る）
- 出力:   population.csv（都道府県コード,日付,人口（万人））
- 備考:   月次×都道府県別データはe-Stat APIで提供されていないため年次データを使用

使い方:
  1. e-Stat にユーザー登録してアプリケーションIDを取得する
     https://www.e-stat.go.jp/api/
  2. APP_ID に取得したIDをセットする
  3. python fetch_population.py を実行する
"""

import urllib.request
import urllib.parse
import json
import csv
import time
from datetime import date
from env import APP_ID

# ─────────────────────────────────────────────
# 設定
# ─────────────────────────────────────────────
OUTPUT_FILE = "population.csv"
BASE_URL = "https://api.e-stat.go.jp/rest/3.0/app/json/getStatsData"

# 都道府県別 各年10月1日現在人口 の統計表IDリスト（新しい順）
# 国勢調査の改定ごとに統計表IDが変わるため複数指定する
# ※ 令和2年国勢調査基準 (2015年〜現在)
STATS_DATA_IDS = [
    "0003448234",   # 令和2年国勢調査基準：都道府県、男女別人口（2015年〜）
    "0003412313",   # 平成27年国勢調査基準：都道府県、男女別人口（2010年〜2015年）
]

# 都道府県コード（国土数値情報準拠 01〜47）
PREF_CODES = {
    "01000": "01", "02000": "02", "03000": "03", "04000": "04", "05000": "05",
    "06000": "06", "07000": "07", "08000": "08", "09000": "09", "10000": "10",
    "11000": "11", "12000": "12", "13000": "13", "14000": "14", "15000": "15",
    "16000": "16", "17000": "17", "18000": "18", "19000": "19", "20000": "20",
    "21000": "21", "22000": "22", "23000": "23", "24000": "24", "25000": "25",
    "26000": "26", "27000": "27", "28000": "28", "29000": "29", "30000": "30",
    "31000": "31", "32000": "32", "33000": "33", "34000": "34", "35000": "35",
    "36000": "36", "37000": "37", "38000": "38", "39000": "39", "40000": "40",
    "41000": "41", "42000": "42", "43000": "43", "44000": "44", "45000": "45",
    "46000": "46", "47000": "47",
}


# ─────────────────────────────────────────────
# API呼び出し
# ─────────────────────────────────────────────
def fetch_stats(stats_data_id: str, year_from: int, year_to: int) -> dict:
    """e-Stat getStatsData API を呼び出してJSONを返す"""
    params = {
        "appId":       APP_ID,
        "statsDataId": stats_data_id,
        "cdTimeFrom":  f"{year_from}000000",   # 例: 2015000000
        "cdTimeTo":    f"{year_to}000000",     # 例: 2025000000
        "metaGetFlg":  "N",
        "limit":       "100000",
    }
    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    print(f"  GET {url[:80]}...")

    with urllib.request.urlopen(url, timeout=30) as res:
        return json.loads(res.read().decode("utf-8"))


# ─────────────────────────────────────────────
# レスポンスのパース
# ─────────────────────────────────────────────
def parse_values(data: dict) -> list[tuple[str, str, float]]:
    """
    VALUE ノードを解析して (都道府県コード, YYYYMMDD, 万人) のリストを返す。
    都道府県コードはe-Statの地域コード（例:01000）を国土数値情報コード（01）に変換する。
    """
    rows = []

    try:
        values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
    except KeyError:
        print("  → データなし（KeyError）")
        return rows

    # VALUE が1件のときはリストでなく辞書になる場合があるので統一する
    if isinstance(values, dict):
        values = [values]

    for v in values:
        area_code = v.get("@area", "")
        time_code = v.get("@time", "")    # 例: "2021000000"
        raw_value = v.get("$", "")
        cat01 = v.get("@cat01", "")

        # 総人口（男女計）のみ抽出: cat01が"000"または"0000"または存在しない場合
        if cat01 not in ("", "000", "0000"):
            continue

        # 都道府県コード変換
        pref_code = PREF_CODES.get(area_code)
        if pref_code is None:
            continue   # 全国など都道府県以外はスキップ

        # 年を YYYYMMDD（10月1日）に変換
        year = time_code[:4]
        if not year.isdigit():
            continue
        date_str = f"{year}1001"

        # 人口値（千人 or 万人はデータによって異なるため後で処理）
        try:
            population_raw = float(raw_value.replace(",", ""))
        except ValueError:
            continue   # "-" や "X" など数値でないものはスキップ

        rows.append((pref_code, date_str, population_raw))

    return rows


# ─────────────────────────────────────────────
# 単位の確認と万人への変換
# ─────────────────────────────────────────────
def get_unit(data: dict) -> str:
    """メタ情報からunitを取得する（取得できない場合は空文字）"""
    try:
        values = data["GET_STATS_DATA"]["STATISTICAL_DATA"]["DATA_INF"]["VALUE"]
        if isinstance(values, list) and values:
            return values[0].get("@unit", "")
        elif isinstance(values, dict):
            return values.get("@unit", "")
    except (KeyError, IndexError):
        pass
    return ""


def to_man_nin(value: float, unit: str) -> float:
    """人口値を万人単位に変換する"""
    unit_lower = unit.lower()
    if "千人" in unit or unit_lower in ("thousand", "1000"):
        return round(value / 10, 1)
    elif "万人" in unit or unit_lower in ("10000",):
        return round(value, 1)
    else:
        # unitが不明またはそのままの場合（千人単位が多い）
        # 値が 10000 以上なら「人」単位と判断
        if value >= 10000:
            return round(value / 10000, 1)
        # 値が 100〜9999 なら「千人」単位と判断
        elif value >= 100:
            return round(value / 10, 1)
        else:
            return round(value, 1)


# ─────────────────────────────────────────────
# メイン処理
# ─────────────────────────────────────────────
def main():
    if APP_ID == "YOUR_APP_ID_HERE":
        print("エラー: APP_ID を設定してください。")
        print("e-Stat ユーザー登録: https://www.e-stat.go.jp/api/")
        return

    today = date.today()
    year_to   = today.year
    year_from = year_to - 10   # 最新から10年分

    print(f"取得期間: {year_from}年〜{year_to}年（各年10月1日現在）")
    print()

    all_rows: list[tuple[str, str, float]] = []
    seen: set[tuple[str, str]] = set()   # 重複除去用

    for stats_id in STATS_DATA_IDS:
        print(f"統計表ID: {stats_id}")
        try:
            data = fetch_stats(stats_id, year_from, year_to)
            status = data["GET_STATS_DATA"]["RESULT"]["STATUS"]
            if status != 0:
                msg = data["GET_STATS_DATA"]["RESULT"]["ERROR_MSG"]
                print(f"  → APIエラー STATUS={status}: {msg}")
                continue

            unit = get_unit(data)
            rows = parse_values(data)
            print(f"  → {len(rows)} 件取得 (unit='{unit}')")

            for pref_code, date_str, pop_raw in rows:
                key = (pref_code, date_str)
                if key in seen:
                    continue   # 統計表IDが重複する期間は新しいほうを優先
                seen.add(key)
                pop_man = to_man_nin(pop_raw, unit)
                all_rows.append((pref_code, date_str, pop_man))

        except Exception as e:
            print(f"  → 取得失敗: {e}")

        time.sleep(1)   # APIサーバへの負荷を避けるため1秒待機

    if not all_rows:
        print("\nデータが取得できませんでした。APP_IDと統計表IDを確認してください。")
        return

    # 都道府県コード → 日付 の順でソート
    all_rows.sort(key=lambda r: (r[0], r[1]))

    # CSV書き出し
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        for pref_code, date_str, pop_man in all_rows:
            writer.writerow([pref_code, date_str, pop_man])

    print(f"\n完了: {len(all_rows)} 行を {OUTPUT_FILE} に書き出しました。")
    print("\n出力サンプル（先頭5行）:")
    for row in all_rows[:5]:
        print(f"  {row[0]},{row[1]},{row[2]}")


if __name__ == "__main__":
    main()