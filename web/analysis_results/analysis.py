import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io
from datetime import datetime

# --- 0. 設定 ---

# 分析対象の日付を指定 (この日付を変更するだけで他の日のデータも分析可能)
analysis_date = "2025-07-18"
print(f"--- 分析を開始します (対象日: {analysis_date}) ---")


# --- 1. 出力パスの設定 ---

# このスクリプト(analysis.py)の絶対パスを取得
script_path = os.path.abspath(__file__)
# このスクリプトがあるディレクトリ(analysis_results/)のパス
analysis_results_dir = os.path.dirname(script_path)
# プロジェクトのルートディレクトリ(yamadaudon/)のパス
project_root_dir = os.path.dirname(analysis_results_dir)

# 出力ディレクトリのパスを定義 (例: .../analysis_results/output/2025-07-18)
output_dir = os.path.join(analysis_results_dir, 'output', analysis_date)


# 出力ディレクトリが存在しない場合は作成
os.makedirs(output_dir, exist_ok=True)
print(f"結果は '{output_dir}' に保存されます。")


# --- 2. データの読み込み (ファイルではなく文字列から直接) ---

# analysis_result_2025-07-18.csv の内容をここに貼り付け
customer_csv_data = """image_path,table_id,seat_start_time,seat_end_time,selected_people,camera_total,people_diff,person_id,gender,estimated_age_range,age_category,confidence
dataset/photo_1752805809.jpg,3,2025-07-18_11-30-23,,1,1,0,1,male,20-30,young_adult,high
dataset/photo_1752805877.jpg,1,2025-07-18_11-31-59,2025-07-18_11-37-09,1,1,0,1,male,20-30,young_adult,high
dataset/photo_1752806139.jpg,1,2025-07-18_11-37-14,,1,1,0,1,unknown,unavailable,unknown,low
dataset/photo_1752806238.jpg,1,2025-07-18_11-39-58,2025-07-18_11-40-38,1,1,0,1,male,60+,senior,high
dataset/photo_1752806238.jpg,28,2025-07-18_11-40-21,,3,1,2,1,male,40-59,middle_aged,high
dataset/photo_1752806238.jpg,24,2025-07-18_11-45-39,,4,1,3,1,male,60-70,senior,high
dataset/photo_1752806883.jpg,6,2025-07-18_11-48-27,,1,1,0,1,male,60+,senior,high
dataset/photo_1752806925.jpg,28,2025-07-18_11-49-16,,3,3,0,1,male,20-39,young_adult,high
dataset/photo_1752806925.jpg,28,2025-07-18_11-49-16,,3,3,0,2,male,20-39,young_adult,high
dataset/photo_1752806925.jpg,28,2025-07-18_11-49-16,,3,3,0,3,male,20-39,young_adult,high
dataset/photo_1752806980.jpg,19,2025-07-18_11-50-16,,4,3,1,1,male,60-75,senior,high
dataset/photo_1752806980.jpg,19,2025-07-18_11-50-16,,4,3,1,2,male,60-70,senior,medium
dataset/photo_1752806980.jpg,19,2025-07-18_11-50-16,,4,3,1,3,female,40-50,middle_aged,medium
dataset/photo_1752806980.jpg,11,2025-07-18_11-53-04,,1,3,-2,1,male,60-70,senior,high
dataset/photo_1752806980.jpg,11,2025-07-18_11-53-04,,1,3,-2,2,male,40-50,middle_aged,high
dataset/photo_1752806980.jpg,11,2025-07-18_11-53-04,,1,3,-2,3,female,40-50,middle_aged,medium
dataset/photo_1752806980.jpg,25,2025-07-18_11-54-42,,2,3,-1,1,male,60-80,senior,high
dataset/photo_1752806980.jpg,25,2025-07-18_11-54-42,,2,3,-1,2,male,60-80,senior,high
dataset/photo_1752806980.jpg,25,2025-07-18_11-54-42,,2,3,-1,3,female,40-50,middle_aged,medium
dataset/photo_1752806980.jpg,1,2025-07-18_11-57-20,,1,3,-2,1,male,60-70,senior,high
dataset/photo_1752806980.jpg,1,2025-07-18_11-57-20,,1,3,-2,2,male,40-50,middle_aged,medium
dataset/photo_1752806980.jpg,1,2025-07-18_11-57-20,,1,3,-2,3,female,40-50,middle_aged,medium
dataset/photo_1752807469.jpg,26,2025-07-18_11-58-14,,2,2,0,1,male,20-39,young_adult,high
dataset/photo_1752807469.jpg,26,2025-07-18_11-58-14,,2,2,0,2,male,40-59,middle_aged,high
dataset/photo_1752807469.jpg,2,2025-07-18_12-00-43,,2,2,0,1,male,20-39,young_adult,high
dataset/photo_1752807469.jpg,2,2025-07-18_12-00-43,,2,2,0,2,male,40-59,middle_aged,high
dataset/photo_1752807469.jpg,13,2025-07-18_12-02-15,,2,2,0,1,male,40-59,middle_aged,high
dataset/photo_1752807469.jpg,13,2025-07-18_12-02-15,,2,2,0,2,male,40-59,middle_aged,medium
dataset/photo_1752808040.jpg,28,2025-07-18_12-11-04,,4,5,-1,1,male,20-39,young_adult,high
dataset/photo_1752808040.jpg,28,2025-07-18_12-11-04,,4,5,-1,2,female,20-39,young_adult,high
dataset/photo_1752808040.jpg,28,2025-07-18_12-11-04,,4,5,-1,3,female,20-39,young_adult,high
dataset/photo_1752808040.jpg,28,2025-07-18_12-11-04,,4,5,-1,4,male,20-39,young_adult,high
dataset/photo_1752808040.jpg,28,2025-07-18_12-11-04,,4,5,-1,5,male,20-39,young_adult,high
dataset/photo_1752808273.jpg,1,2025-07-18_12-11-28,2025-07-18_12-11-45,1,1,0,1,male,40-59,middle_aged,high
dataset/photo_1752808370.jpg,24,2025-07-18_12-13-42,,2,3,-1,1,male,20-39,young_adult,medium
dataset/photo_1752808370.jpg,24,2025-07-18_12-13-42,,2,3,-1,2,male,20-39,young_adult,medium
dataset/photo_1752808370.jpg,24,2025-07-18_12-13-42,,2,3,-1,3,male,40-59,middle_aged,medium
dataset/photo_1752808512.jpg,1,2025-07-18_12-15-23,2025-07-18_12-15-31,1,1,0,1,male,20-39,young_adult,medium
dataset/photo_1752808534.jpg,25,2025-07-18_12-15-54,,1,1,0,1,male,20-39,young_adult,high
dataset/photo_1752808557.jpg,17,2025-07-18_12-16-39,,2,3,-1,1,male,20-39,young_adult,medium
dataset/photo_1752808557.jpg,17,2025-07-18_12-16-39,,2,3,-1,2,male,20-39,young_adult,medium
dataset/photo_1752808557.jpg,17,2025-07-18_12-16-39,,2,3,-1,3,male,40-59,middle_aged,medium
"""

# POSデータ.csv の内容をここに貼り付け
pos_csv_data = """レシートNo,商品種別,商品名称,伝票No.,テーブルNo,オーダー時刻,単価,数量
2041,M,金得かつカレ,19862,2,1112,980,1
2042,M,ざるそば,19861,17,1110,390,1
2042,M,ざるうどん,19861,17,1110,390,1
2042,M,フライドポテト,19861,17,1110,230,1
2043,M,金得かつカレ,19863,8,1119,980,1
2044,M,ネバとろうど,19865,24,1123,770,1
2044,M,かき揚げ丼,19865,24,1123,590,1
2045,M,醤油ラーメン,19866,11,1126,620,1
2045,M,ミニ赤パンチ,19866,11,1126,480,1
2046,M,和風カレーう,19864,26,1121,770,1
2046,M,ざるそば,19864,26,1121,390,1
2047,M,冷天ぷらそば,19874,3,1139,640,1
2048,M,生姜焼きS,19869,14,1133,1280,1
2049,M,パンチ食比べ,19868,1,1130,890,1
2050,M,金得かつカレ,19871,9,1136,980,1
2051,M,金得かつカレ,19873,8,1139,980,1
2052,M,野菜うどん,19872,27,1137,770,1
2052,M,ミニ納豆オク,19872,27,1137,380,1
2053,M,たぬきうどん,19867,16,1127,390,1
2054,M,ざるそば,19876,7,1149,390,1
2055,M,タンメン,19870,21,1134,820,1
2056,M,金得かつカレ,19877,28,1151,980,2
2056,M,3種盛天そば,19877,28,1151,1020,1
2057,M,3種盛天そば,19875,24,1142,1020,1
2057,M,天ぷらそば,19875,24,1142,640,2
2058,M,かき揚げ丼S,19879,11,1154,890,1
2059,M,金得かつカレ,19880,25,1155,980,1
2060,M,冷やし五目ぶ,19880,25,1155,880,1
2061,M,かき揚げ丼S,19881,1,1157,890,1
2062,M,金得かつカレ,19878,17,1153,980,1
2064,M,かき揚げ丼S,19886,3,1204,890,1
2065,M,ネバとろうど,19882,26,1200,770,1
2065,M,チャーハンS,19882,26,1200,950,1
2066,M,金得かつカレ,19884,13,1203,980,2
2067,M,パンチ定食,19885,8,1204,870,1
2068,M,肉汁うどん,19883,27,1201,870,1
2068,M,ざるそば,19883,27,1201,390,1
2070,M,ネバとろうど,19887,24,1214,770,1
2071,M,金得かつカレ,19887,24,1214,980,1
2072,M,冷やし五目ぶ,19889,4,1218,880,1
2073,M,ミニかき揚げ,19892,1,1220,460,1
2074,M,ネバとろうど,19891,25,1219,770,1
2074,M,ネバとろそば,19891,25,1219,770,1
2074,M,ミニかき揚げ,19891,25,1219,460,1
2076,M,チャーハンS,19890,17,1218,950,1
2076,M,無料ミニメン,19890,17,1218,0,1
2077,M,冷やし中華,19890,17,1218,820,1
2078,M,天ざるそば,19893,19,1222,640,2
2079,M,天ぷらそば,19898,3,1233,640,1
2080,M,かき揚げ丼S,19896,12,1232,890,1
2081,M,金得かつカレ,19897,16,1232,980,1
2082,M,生姜焼きS,19901,14,1239,1280,1
2083,M,生姜焼きS,19894,26,1227,1280,1
2083,M,かき揚げ丼S,19894,26,1227,890,1
2083,M,餃子（6個）,19894,26,1227,290,1
2084,M,黒舞茸天ざる,19895,21,1230,920,1
2084,M,かつカレー,19895,21,1230,940,1
2084,M,かつ丼S,19895,21,1230,1140,1
2085,M,金得かつカレ,19900,27,1238,980,1
2086,M,金得かつカレ,19900,27,1238,980,1
2087,M,ざるラーメン,19904,1,1244,620,1
2088,M,金得かつカレ,19899,24,1235,980,1
2088,M,かつカレー,19899,24,1235,940,1
2089,M,かき揚げ丼S,19906,6,1250,890,1
2090,M,冷やし五目ぶ,19888,28,1217,880,1
2091,M,ざるそば,19902,25,1240,390,1
2097,M,金得かつカレ,19908,9,1300,980,1
2101,M,生姜焼き定食,19911,27,1308,980,1
2102,M,金得かつカレ,19911,27,1308,980,1
2103,M,かき揚げ丼S,19913,2,1316,890,1
2104,M,チャーハン,19915,11,1319,650,1
2105,M,スタミナ焼肉,19914,4,1317,990,1
2106,M,スタミナ焼肉,19903,8,1314,1290,1
2107,M,金得かつカレ,19912,28,1316,980,1
2108,M,野菜炒め定食,19920,11,1337,920,1
2109,M,生姜焼き定食,19916,25,1325,980,1
2110,M,金得かつカレ,19918,15,1329,980,1
"""

# 文字列データをDataFrameに変換
try:
    customer_df = pd.read_csv(io.StringIO(customer_csv_data))
    pos_df = pd.read_csv(io.StringIO(pos_csv_data))
    print("データ読み込みに成功しました。")
except Exception as e:
    print(f"エラー: データ読み込み中に問題が発生しました。データ形式を確認してください。")
    print(e)
    exit()


# --- 3. データの前処理 ---
print("データの前処理を開始します...")

# 顧客データ: 必要な列のみ抽出し、時刻をdatetime型に変換
customer_df = customer_df[['table_id', 'seat_start_time', 'gender', 'age_category']].copy()
# 【修正箇所】より柔軟な日時変換処理
import re

def convert_datetime_string(datetime_str):
    """日時文字列を標準的な形式に変換する関数"""
    if pd.isna(datetime_str):
        return datetime_str
    
    # アンダースコアをスペースに変換
    datetime_str = datetime_str.replace('_', ' ')
    
    # 時刻部分のハイフンをコロンに変換（末尾の HH-MM-SS パターンのみ）
    datetime_str = re.sub(r'(\d{2})-(\d{2})-(\d{2})$', r'\1:\2:\3', datetime_str)
    
    return datetime_str

# 変換前のサンプルデータを確認
print("変換前のseat_start_timeサンプル:")
print(customer_df['seat_start_time'].head())

customer_df['seat_start_time'] = customer_df['seat_start_time'].apply(convert_datetime_string)

# 変換後のサンプルデータを確認
print("変換後のseat_start_timeサンプル:")
print(customer_df['seat_start_time'].head())

# より柔軟な日時変換（errors='coerce'でエラーをNaTに変換）
customer_df['seat_start_time'] = pd.to_datetime(customer_df['seat_start_time'], errors='coerce')

# 変換に失敗したデータを確認
failed_conversions = customer_df[customer_df['seat_start_time'].isna()]
if not failed_conversions.empty:
    print(f"警告: {len(failed_conversions)}件の日時変換に失敗しました。")
    print("失敗したデータ:")
    print(failed_conversions[['table_id', 'seat_start_time', 'gender', 'age_category']])

# 日時変換に失敗したデータを除外
customer_df = customer_df.dropna(subset=['seat_start_time'])
print(f"処理対象の顧客データ件数: {len(customer_df)}件")

# --- 複数人グループのデータ処理説明 ---
print(f"\n=== 複数人グループのデータ処理について ===")

# 元データの複数人情報を確認
print("【元の顧客データの複数人情報】")
multi_person_tables = customer_df.groupby(['table_id', 'seat_start_time']).size()
multi_person_cases = multi_person_tables[multi_person_tables > 1]

if len(multi_person_cases) > 0:
    print(f"複数人が記録されているケース: {len(multi_person_cases)}件")
    for (table_id, seat_time), count in multi_person_cases.head(5).items():
        print(f"  テーブル{table_id} ({seat_time}): {count}人")
        
        # そのテーブル・時刻の詳細を表示
        group_data = customer_df[
            (customer_df['table_id'] == table_id) & 
            (customer_df['seat_start_time'] == seat_time)
        ]
        for _, person in group_data.iterrows():
            print(f"    - {person['gender']}, {person['age_category']}")
        print()
else:
    print("複数人が同時に記録されているケースはありません")

print("【複数人グループの処理方針】")
print("1. 同一テーブル・同一時刻に複数の人物が記録されている場合")
print("2. 最初の1件のみを採用（代表者として扱う）")
print("3. これにより、1つのテーブル・時刻につき1つの属性情報となる")
print("4. 注文データ（商品）はこの代表者の属性と紐づけられる")

# 同一テーブル、同一時刻に複数の人物が記録されている場合、最初の1件のみ採用（代表者とする）
before_dedup = len(customer_df)
customer_df = customer_df.drop_duplicates(subset=['table_id', 'seat_start_time'], keep='first')
after_dedup = len(customer_df)

print(f"\n【重複除去の結果】")
print(f"重複除去前: {before_dedup}件")
print(f"重複除去後: {after_dedup}件") 
print(f"除去された件数: {before_dedup - after_dedup}件")

# どの代表者が選ばれたかの例を表示
if len(multi_person_cases) > 0:
    print(f"\n【代表者選択の例】")
    for (table_id, seat_time), count in multi_person_cases.head(3).items():
        original_group = customer_df[
            (customer_df['table_id'] == table_id) & 
            (customer_df['seat_start_time'] == seat_time)
        ]
        
        if len(original_group) > 0:
            representative = original_group.iloc[0]
            print(f"テーブル{table_id} ({seat_time}):")
            print(f"  選択された代表者: {representative['gender']}, {representative['age_category']}")
            print(f"  → このテーブルの全注文がこの属性と紐づけられます")


# POSデータ: 列名を英語に変更し、時刻をdatetime型に変換
pos_df = pos_df.rename(columns={'テーブルNo': 'table_id', 'オーダー時刻': 'order_time', '商品名称': 'product_name', '単価': 'price', '数量': 'quantity'})
date_str = analysis_date
pos_df['order_time'] = pos_df['order_time'].apply(
    lambda x: pd.to_datetime(f"{date_str} {x // 100:02d}:{x % 100:02d}:00")
)


# --- 4. データの結合 ---
print("顧客データとPOSデータを結合します...")

# 結合のために各データフレームを時刻でソート（table_idの制約を外す）
customer_df = customer_df.sort_values(by=['seat_start_time']).reset_index(drop=True)
pos_df = pos_df.sort_values(by=['order_time']).reset_index(drop=True)

# デバッグ情報: ソート後のデータを確認
print("POSデータの最初の5件（時刻順ソート後）:")
print(pos_df[['table_id', 'order_time', 'product_name']].head())
print("顧客データの最初の5件（時刻順ソート後）:")
print(customer_df[['table_id', 'seat_start_time', 'gender', 'age_category']].head())

# 注文時刻を基準に、その直前の着席情報を結合
merged_df = pd.merge_asof(
    pos_df,
    customer_df,
    left_on='order_time',
    right_on='seat_start_time',
    by='table_id',
    direction='backward'
)

# 結合できなかったデータ('unknown'を含む)を削除
merged_df.dropna(subset=['gender', 'age_category'], inplace=True)
merged_df = merged_df[merged_df['age_category'] != 'unknown']
print("データの結合が完了しました。")

# --- データ結合の詳細情報を表示 ---
print(f"\n=== データ結合プロセスの詳細 ===")
print(f"元のPOSデータ件数: {len(pos_df)}件")
print(f"元の顧客データ件数: {len(customer_df)}件")
print(f"結合後のデータ件数: {len(merged_df)}件")
print(f"結合成功率: {len(merged_df)/len(pos_df)*100:.1f}%")

# 結合に使用されたテーブルIDの一覧
merged_tables = set(merged_df['table_id'].unique())
pos_tables = set(pos_df['table_id'].unique())
customer_tables = set(customer_df['table_id'].unique())

print(f"\nテーブルID情報:")
print(f"POSデータに含まれるテーブル: {sorted(pos_tables)}")
print(f"顧客データに含まれるテーブル: {sorted(customer_tables)}")
print(f"結合できたテーブル: {sorted(merged_tables)}")
print(f"結合できなかったテーブル: {sorted(pos_tables - merged_tables)}")

# 結合プロセスの例を表示
print(f"\n=== 結合プロセスの例 ===")
sample_table = merged_df['table_id'].iloc[0] if len(merged_df) > 0 else None
if sample_table:
    print(f"テーブル{sample_table}の結合例:")
    
    # このテーブルのPOSデータ
    table_pos = pos_df[pos_df['table_id'] == sample_table].sort_values('order_time')
    print(f"\n【POSデータ】")
    for _, row in table_pos.head(3).iterrows():
        print(f"  {row['order_time']}: {row['product_name']} ({row['price']}円)")
    
    # このテーブルの顧客データ
    table_customer = customer_df[customer_df['table_id'] == sample_table].sort_values('seat_start_time')
    print(f"\n【顧客データ】")
    for _, row in table_customer.head(3).iterrows():
        print(f"  {row['seat_start_time']}: {row['gender']}, {row['age_category']}")
    
    # 結合結果
    table_merged = merged_df[merged_df['table_id'] == sample_table].sort_values('order_time')
    print(f"\n【結合結果】")
    for _, row in table_merged.head(3).iterrows():
        print(f"  注文時刻: {row['order_time']} → 属性: {row['gender']}, {row['age_category']}")
        print(f"    商品: {row['product_name']} ({row['price']}円)")
        print(f"    使用された着席時刻: {row['seat_start_time']}")
        print("")

print(f"\n結合ロジック:")
print(f"• merge_asofを使用してテーブルIDごとに時系列結合")
print(f"• direction='backward': 注文時刻より前の最新の着席情報を使用")
print(f"• 同じテーブルで複数回着席がある場合、注文時刻直前の着席情報を採用")


# --- 5. 分析と可視化 ---
print("データの分析と可視化を開始します...")

# 日本語フォントの設定（macOS対応）
import matplotlib.font_manager as fm

def setup_japanese_font():
    """日本語フォントを設定する関数"""
    # macOSで利用可能な日本語フォントを試す
    japanese_fonts = [
        'Hiragino Sans',
        'Hiragino Kaku Gothic Pro', 
        'Yu Gothic',
        'Meiryo',
        'MS Gothic',
        'DejaVu Sans'
    ]
    
    for font_name in japanese_fonts:
        try:
            plt.rcParams['font.family'] = font_name
            # テスト用の簡単な描画
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, 'テスト', fontsize=10)
            plt.close(fig)  # テスト図を閉じる
            print(f"日本語フォント '{font_name}' を使用します。")
            return True
        except:
            continue
    
    # すべて失敗した場合は警告を出してデフォルトフォントを使用
    plt.rcParams['font.family'] = 'sans-serif'
    print("警告: 日本語フォントが見つかりません。文字化けする可能性があります。")
    return False

# フォント設定を実行
setup_japanese_font()

# 売上高のカラムを追加
merged_df['sales'] = merged_df['price'] * merged_df['quantity']


# 分析1: 年代・性別ごとの売上合計
age_gender_sales = merged_df.groupby(['age_category', 'gender'])['sales'].sum().unstack(fill_value=0)
age_gender_sales.to_csv(os.path.join(output_dir, 'age_gender_sales.csv'))

plt.figure(figsize=(10, 6))
age_gender_sales.plot(kind='bar', stacked=True, ax=plt.gca())
plt.title(f'年代・性別ごとの売上分析 ({analysis_date})', fontsize=14)
plt.xlabel('年代カテゴリ', fontsize=12)
plt.ylabel('総売上 (円)', fontsize=12)
plt.xticks(rotation=45)
plt.legend(title='性別')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'age_gender_sales.png'), dpi=300, bbox_inches='tight')
plt.close()
print("  - 年代・性別ごとの売上分析が完了しました。")


# 分析2: 年代別の人気商品
age_product_sales = merged_df.groupby(['age_category', 'product_name'])['sales'].sum().unstack(fill_value=0)
age_product_sales.to_csv(os.path.join(output_dir, 'age_product_sales.csv'))

top_products = age_product_sales.sum().nlargest(15).index
plt.figure(figsize=(12, 8))
sns.heatmap(age_product_sales[top_products].T, annot=True, fmt=".0f", cmap="viridis")
plt.title(f'年代別人気商品トップ15 ({analysis_date})', fontsize=14)
plt.xlabel('年代カテゴリ', fontsize=12)
plt.ylabel('商品名', fontsize=12)
plt.yticks(rotation=0)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'age_product_heatmap.png'), dpi=300, bbox_inches='tight')
plt.close()
print("  - 年代別の人気商品分析が完了しました。")


# 分析3: 全商品の売上ランキング
product_ranking = merged_df.groupby('product_name')['sales'].sum().sort_values(ascending=False)
product_ranking.to_csv(os.path.join(output_dir, 'product_ranking.csv'))

plt.figure(figsize=(10, 12))
product_ranking.nlargest(20).sort_values().plot(kind='barh')
plt.title(f'商品売上ランキング トップ20 ({analysis_date})', fontsize=14)
plt.xlabel('総売上 (円)', fontsize=12)
plt.ylabel('商品名', fontsize=12)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'product_ranking.png'), dpi=300, bbox_inches='tight')
plt.close()
print("  - 商品売上ランキングの分析が完了しました。")


# --- 6. 詳細分析: 年齢層別メニュー傾向 ---
print("\n=== 年齢層別メニュー分析結果 ===")

# 年齢層別の注文数と売上を詳細分析
age_analysis = merged_df.groupby('age_category').agg({
    'product_name': 'count',  # 注文数
    'sales': ['sum', 'mean']  # 売上合計と平均
}).round(0)

age_analysis.columns = ['注文数', '売上合計', '平均単価']
print("\n【年齢層別の基本統計】")
print(age_analysis)

# 年齢層別の人気メニューTop5を表示
print("\n【年齢層別人気メニューTop5】")
for age_group in merged_df['age_category'].unique():
    age_data = merged_df[merged_df['age_category'] == age_group]
    top_products = age_data.groupby('product_name')['sales'].sum().sort_values(ascending=False).head(5)
    
    print(f"\n◆ {age_group}層:")
    for i, (product, sales) in enumerate(top_products.items(), 1):
        order_count = age_data[age_data['product_name'] == product].shape[0]
        print(f"  {i}位: {product} (売上: {sales:,}円, 注文数: {order_count}件)")

# 年齢層別メニュー嗜好の特徴分析
print("\n【年齢層別メニュー傾向の特徴】")

# 各年齢層の特徴的なメニューを分析（その年齢層での売上比率が高いもの）
age_product_ratio = merged_df.groupby(['age_category', 'product_name'])['sales'].sum().unstack(fill_value=0)
age_product_percentage = age_product_ratio.div(age_product_ratio.sum(axis=1), axis=0) * 100

for age_group in age_product_percentage.index:
    top_ratio_products = age_product_percentage.loc[age_group].sort_values(ascending=False).head(3)
    print(f"\n◆ {age_group}層の特徴:")
    for product, ratio in top_ratio_products.items():
        if ratio > 0:
            total_sales = age_product_ratio.loc[age_group, product]
            print(f"  • {product}: {ratio:.1f}% (売上: {total_sales:,}円)")

# メニューカテゴリ別の分析（簡易的な分類）
print("\n【メニューカテゴリ別傾向】")

def categorize_menu(product_name):
    """メニューを簡易カテゴリに分類"""
    if 'カレー' in product_name:
        return 'カレー系'
    elif any(word in product_name for word in ['そば', 'うどん', 'ラーメン', 'タンメン']):
        return '麺類'
    elif any(word in product_name for word in ['丼', '定食', '焼肉', '生姜焼き']):
        return '丼・定食'
    elif any(word in product_name for word in ['天ぷら', 'かき揚げ', 'フライ']):
        return '揚げ物'
    else:
        return 'その他'

merged_df['menu_category'] = merged_df['product_name'].apply(categorize_menu)

category_analysis = merged_df.groupby(['age_category', 'menu_category'])['sales'].sum().unstack(fill_value=0)
category_percentage = category_analysis.div(category_analysis.sum(axis=1), axis=0) * 100

for age_group in category_percentage.index:
    print(f"\n◆ {age_group}層のカテゴリ別嗜好:")
    categories = category_percentage.loc[age_group].sort_values(ascending=False)
    for category, percentage in categories.items():
        if percentage > 0:
            sales = category_analysis.loc[age_group, category]
            print(f"  • {category}: {percentage:.1f}% (売上: {sales:,}円)")

# カテゴリ別分析結果をCSVで保存
category_analysis.to_csv(os.path.join(output_dir, 'age_category_menu_analysis.csv'))
age_analysis.to_csv(os.path.join(output_dir, 'age_basic_statistics.csv'))

# --- 7. データ結合プロセスの可視化 ---
print("\n=== データ結合プロセスの可視化 ===")

# タイムライン図を作成（サンプルテーブルの例）
if len(merged_df) > 0:
    # データが豊富なテーブルを選択
    table_counts = merged_df['table_id'].value_counts()
    sample_table = table_counts.index[0] if len(table_counts) > 0 else merged_df['table_id'].iloc[0]
    
    # サンプルテーブルのデータを取得
    sample_pos = pos_df[pos_df['table_id'] == sample_table].sort_values('order_time')
    sample_customer = customer_df[customer_df['table_id'] == sample_table].sort_values('seat_start_time')
    sample_merged = merged_df[merged_df['table_id'] == sample_table].sort_values('order_time')
    
    # タイムライン図を作成
    plt.figure(figsize=(15, 8))
    
    # 顧客の着席時刻をプロット
    for i, (_, row) in enumerate(sample_customer.iterrows()):
        plt.scatter(row['seat_start_time'], 1, s=100, c='blue', marker='o', alpha=0.7)
        plt.text(row['seat_start_time'], 1.1, f"{row['gender']}\n{row['age_category']}", 
                ha='center', va='bottom', fontsize=8, rotation=45)
    
    # 注文時刻をプロット
    for i, (_, row) in enumerate(sample_pos.iterrows()):
        plt.scatter(row['order_time'], 0, s=80, c='red', marker='s', alpha=0.7)
        plt.text(row['order_time'], -0.1, row['product_name'], 
                ha='center', va='top', fontsize=8, rotation=45)
    
    # 結合線を描画
    for _, row in sample_merged.iterrows():
        plt.plot([row['order_time'], row['seat_start_time']], [0, 1], 
                'g--', alpha=0.5, linewidth=1)
    
    plt.ylim(-0.5, 1.5)
    plt.xlabel('時間', fontsize=12)
    plt.title(f'データ結合プロセス - テーブル{sample_table}のタイムライン', fontsize=14)
    plt.yticks([0, 1], ['注文 (POS)', '顧客着席'])
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'data_linking_timeline.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"タイムライン図を作成しました（テーブル{sample_table}の例）")
    
    # 結合統計の詳細分析
    print(f"\n=== 結合統計の詳細 ===")
    
    # テーブル別の結合成功率
    table_merge_stats = []
    for table_id in pos_df['table_id'].unique():
        pos_count = len(pos_df[pos_df['table_id'] == table_id])
        merged_count = len(merged_df[merged_df['table_id'] == table_id])
        success_rate = (merged_count / pos_count * 100) if pos_count > 0 else 0
        
        table_merge_stats.append({
            'table_id': table_id,
            'pos_orders': pos_count,
            'merged_orders': merged_count,
            'success_rate': success_rate,
            'has_customer_data': table_id in customer_df['table_id'].values
        })
    
    merge_stats_df = pd.DataFrame(table_merge_stats)
    merge_stats_df = merge_stats_df.sort_values('success_rate', ascending=False)
    
    print(f"\n【テーブル別結合成功率】")
    print(merge_stats_df.to_string(index=False))
    
    # 結合成功率の分布
    plt.figure(figsize=(12, 6))
    plt.subplot(1, 2, 1)
    plt.hist(merge_stats_df['success_rate'], bins=10, alpha=0.7, edgecolor='black')
    plt.xlabel('結合成功率 (%)')
    plt.ylabel('テーブル数')
    plt.title('結合成功率の分布')
    
    plt.subplot(1, 2, 2)
    has_data = merge_stats_df['has_customer_data'].value_counts()
    plt.pie(has_data.values, labels=['顧客データあり', '顧客データなし'], autopct='%1.1f%%')
    plt.title('顧客データの有無別テーブル数')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'merge_statistics.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 統計をCSVで保存
    merge_stats_df.to_csv(os.path.join(output_dir, 'table_merge_statistics.csv'), index=False)
    
    print(f"結合統計を保存しました")

# --- 8. 複数人グループ分析の可視化 ---
print(f"\n=== 複数人グループ分析の詳細 ===")

# 元の顧客データを再読込して複数人情報を分析
customer_raw = pd.read_csv(io.StringIO(customer_csv_data))
customer_raw = customer_raw[['table_id', 'seat_start_time', 'gender', 'age_category']].copy()
customer_raw['seat_start_time'] = customer_raw['seat_start_time'].apply(convert_datetime_string)
customer_raw['seat_start_time'] = pd.to_datetime(customer_raw['seat_start_time'], errors='coerce')
customer_raw = customer_raw.dropna(subset=['seat_start_time'])

# グループサイズの分析
group_sizes = customer_raw.groupby(['table_id', 'seat_start_time']).size()
group_size_counts = group_sizes.value_counts().sort_index()

print(f"【グループサイズ別の分布】")
for size, count in group_size_counts.items():
    print(f"  {size}人グループ: {count}件")

# グループサイズの可視化
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
group_size_counts.plot(kind='bar', color='skyblue', edgecolor='black')
plt.title('グループサイズ分布')
plt.xlabel('グループ人数')
plt.ylabel('グループ数')
plt.xticks(rotation=0)

# 複数人グループの詳細分析
multi_groups = customer_raw.groupby(['table_id', 'seat_start_time']).filter(lambda x: len(x) > 1)
if len(multi_groups) > 0:
    # 複数人グループの性別・年齢構成
    group_compositions = []
    for (table_id, seat_time), group_data in multi_groups.groupby(['table_id', 'seat_start_time']):
        composition = {
            'table_id': table_id,
            'seat_time': seat_time,
            'group_size': len(group_data),
            'male_count': len(group_data[group_data['gender'] == 'male']),
            'female_count': len(group_data[group_data['gender'] == 'female']),
            'young_adult': len(group_data[group_data['age_category'] == 'young_adult']),
            'middle_aged': len(group_data[group_data['age_category'] == 'middle_aged']),
            'senior': len(group_data[group_data['age_category'] == 'senior']),
        }
        group_compositions.append(composition)
    
    comp_df = pd.DataFrame(group_compositions)
    
    plt.subplot(1, 2, 2)
    # 複数人グループの性別構成
    gender_mix = []
    for _, group in comp_df.iterrows():
        if group['male_count'] > 0 and group['female_count'] > 0:
            gender_mix.append('Mixed')
        elif group['male_count'] > 0:
            gender_mix.append('Male Only')
        else:
            gender_mix.append('Female Only')
    
    gender_counts = pd.Series(gender_mix).value_counts()
    if len(gender_counts) > 0:
        # 日本語ラベルに変換
        gender_labels = {'Mixed': '男女混合', 'Male Only': '男性のみ', 'Female Only': '女性のみ'}
        japanese_labels = [gender_labels.get(label, label) for label in gender_counts.index]
        gender_counts.index = japanese_labels
        gender_counts.plot(kind='pie', autopct='%1.1f%%')
        plt.title('複数人グループの性別構成')
        plt.ylabel('')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'group_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n【複数人グループの詳細】")
    for _, group in comp_df.head(5).iterrows():
        print(f"テーブル{group['table_id']} ({group['group_size']}人): "
              f"男性{group['male_count']}人, 女性{group['female_count']}人 | "
              f"若年{group['young_adult']}人, 中年{group['middle_aged']}人, 高齢{group['senior']}人")
    
    # 複数人グループでの代表者選択の影響分析
    print(f"\n【代表者選択の影響分析】")
    
    # 代表者として選ばれた属性の分布
    representative_attrs = customer_df[customer_df.duplicated(['table_id', 'seat_start_time'], keep=False) == False]
    
    # 複数人グループの実際の構成 vs 代表者の属性
    impact_analysis = []
    for (table_id, seat_time), group_data in multi_groups.groupby(['table_id', 'seat_start_time']):
        representative = customer_df[
            (customer_df['table_id'] == table_id) & 
            (customer_df['seat_start_time'] == seat_time)
        ]
        
        if len(representative) > 0:
            rep = representative.iloc[0]
            actual_genders = group_data['gender'].value_counts()
            actual_ages = group_data['age_category'].value_counts()
            
            impact_analysis.append({
                'table_id': table_id,
                'group_size': len(group_data),
                'rep_gender': rep['gender'],
                'rep_age': rep['age_category'],
                'actual_gender_diversity': len(actual_genders),
                'actual_age_diversity': len(actual_ages),
                'gender_representative': rep['gender'] in actual_genders.index,
                'age_representative': rep['age_category'] in actual_ages.index
            })
    
    if impact_analysis:
        impact_df = pd.DataFrame(impact_analysis)
        print(f"代表者の性別が実際の構成を反映: {impact_df['gender_representative'].mean()*100:.1f}%")
        print(f"代表者の年齢が実際の構成を反映: {impact_df['age_representative'].mean()*100:.1f}%")
        
        # 詳細をCSVで保存
        comp_df.to_csv(os.path.join(output_dir, 'multi_person_groups.csv'), index=False)
        impact_df.to_csv(os.path.join(output_dir, 'representative_impact.csv'), index=False)

else:
    print("複数人グループのデータがありません")
    
    # 単純な棒グラフを作成
    plt.subplot(1, 2, 2)
    plt.text(0.5, 0.5, '複数人グループが\n見つかりませんでした', 
             ha='center', va='center', transform=plt.gca().transAxes, fontsize=12)
    plt.title('複数人グループ分析')
    plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'group_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()

print(f"\n【複数人来店時の処理まとめ】")
print(f"1. 同一テーブル・同一時刻に複数人が検出された場合")
print(f"2. 最初の1人を「代表者」として選択")
print(f"3. そのテーブルの全ての注文を代表者の属性と紐づけ")
print(f"4. これにより分析の一貫性を保持（1注文→1属性）")
print(f"5. ただし、グループ内の多様性は失われる可能性あり")

# --- 9. 家族グループと女性客の詳細分析 ---
print(f"\n=== 家族グループと女性客の注文傾向分析 ===")

# 家族グループの推定ロジック
def identify_family_groups(customer_raw):
    """家族グループを推定する関数"""
    family_groups = []
    
    for (table_id, seat_time), group_data in customer_raw.groupby(['table_id', 'seat_start_time']):
        if len(group_data) >= 2:  # 2人以上のグループ
            ages = group_data['age_category'].value_counts()
            genders = group_data['gender'].value_counts()
            
            # 家族グループの判定条件
            is_family = False
            family_type = ""
            
            # 条件1: 異なる年代が混在している
            has_age_diversity = len(ages) >= 2
            
            # 条件2: 男女が混在している
            has_gender_diversity = len(genders) >= 2
            
            # 条件3: 高齢者+若年者または中年者の組み合わせ（親子パターン）
            has_generational_gap = ('senior' in ages.index and 
                                  ('young_adult' in ages.index or 'middle_aged' in ages.index))
            
            # 条件4: 中年者+若年者の組み合わせ（親子パターン）
            has_parent_child = ('middle_aged' in ages.index and 'young_adult' in ages.index)
            
            if has_age_diversity and has_gender_diversity:
                if has_generational_gap:
                    is_family = True
                    family_type = "多世代家族"
                elif has_parent_child:
                    is_family = True
                    family_type = "親子家族"
                else:
                    is_family = True
                    family_type = "家族（推定）"
            elif has_generational_gap:
                is_family = True
                family_type = "世代間グループ"
            
            if is_family:
                family_groups.append({
                    'table_id': table_id,
                    'seat_time': seat_time,
                    'group_size': len(group_data),
                    'family_type': family_type,
                    'age_composition': dict(ages),
                    'gender_composition': dict(genders),
                    'members': group_data.to_dict('records')
                })
    
    return family_groups

# 家族グループの特定
if len(customer_raw) > 0:
    family_groups = identify_family_groups(customer_raw)
    
    print(f"【家族グループの推定結果】")
    print(f"推定家族グループ数: {len(family_groups)}組")
    
    if family_groups:
        for i, family in enumerate(family_groups[:5], 1):  # 上位5組を表示
            print(f"\n{i}. テーブル{family['table_id']} - {family['family_type']} ({family['group_size']}人)")
            print(f"   年齢構成: {family['age_composition']}")
            print(f"   性別構成: {family['gender_composition']}")
        
        # 家族グループの注文傾向分析
        family_table_times = [(f['table_id'], f['seat_time']) for f in family_groups]
        
        # 家族グループの注文データを抽出
        family_orders = []
        for table_id, seat_time in family_table_times:
            # その家族グループに対応する注文を検索
            family_merged = merged_df[
                (merged_df['table_id'] == table_id) & 
                (merged_df['seat_start_time'] == seat_time)
            ]
            if len(family_merged) > 0:
                family_orders.extend(family_merged.to_dict('records'))
        
        if family_orders:
            family_df = pd.DataFrame(family_orders)
            
            print(f"\n【家族グループの注文分析】")
            print(f"家族グループの注文件数: {len(family_df)}件")
            print(f"家族グループの総売上: {family_df['sales'].sum():,}円")
            print(f"家族グループの平均注文単価: {family_df['sales'].mean():.0f}円")
            
            # 家族グループの人気メニューTop10
            family_popular = family_df.groupby('product_name')['sales'].sum().sort_values(ascending=False).head(10)
            print(f"\n【家族グループの人気メニューTop10】")
            for i, (product, sales) in enumerate(family_popular.items(), 1):
                order_count = len(family_df[family_df['product_name'] == product])
                print(f"  {i}位: {product} (売上: {sales:,}円, 注文数: {order_count}件)")
            
            # 家族グループのカテゴリ別嗜好
            family_df['menu_category'] = family_df['product_name'].apply(categorize_menu)
            family_category = family_df.groupby('menu_category')['sales'].sum().sort_values(ascending=False)
            print(f"\n【家族グループのカテゴリ別注文傾向】")
            total_family_sales = family_category.sum()
            for category, sales in family_category.items():
                percentage = (sales / total_family_sales * 100)
                print(f"  • {category}: {sales:,}円 ({percentage:.1f}%)")
            
            # 家族 vs 全体の比較
            all_category = merged_df.groupby('menu_category')['sales'].sum()
            comparison_data = []
            for category in all_category.index:
                family_pct = (family_category.get(category, 0) / total_family_sales * 100) if total_family_sales > 0 else 0
                all_pct = (all_category[category] / all_category.sum() * 100)
                comparison_data.append({
                    'category': category,
                    'family_percentage': family_pct,
                    'all_percentage': all_pct,
                    'difference': family_pct - all_pct
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df = comparison_df.sort_values('difference', ascending=False)
            
            print(f"\n【家族グループ vs 全体の嗜好比較】")
            for _, row in comparison_df.iterrows():
                diff_str = f"+{row['difference']:.1f}%" if row['difference'] >= 0 else f"{row['difference']:.1f}%"
                print(f"  • {row['category']}: 家族{row['family_percentage']:.1f}% vs 全体{row['all_percentage']:.1f}% ({diff_str})")

# 女性客の注文傾向分析
print(f"\n【女性客の注文傾向分析】")

female_orders = merged_df[merged_df['gender'] == 'female']
male_orders = merged_df[merged_df['gender'] == 'male']

if len(female_orders) > 0:
    print(f"女性客の注文件数: {len(female_orders)}件")
    print(f"女性客の総売上: {female_orders['sales'].sum():,}円")
    print(f"女性客の平均注文単価: {female_orders['sales'].mean():.0f}円")
    
    print(f"\n男性客の注文件数: {len(male_orders)}件")
    print(f"男性客の総売上: {male_orders['sales'].sum():,}円")
    print(f"男性客の平均注文単価: {male_orders['sales'].mean():.0f}円")
    
    # 女性客の人気メニューTop10
    female_popular = female_orders.groupby('product_name')['sales'].sum().sort_values(ascending=False).head(10)
    print(f"\n【女性客の人気メニューTop10】")
    for i, (product, sales) in enumerate(female_popular.items(), 1):
        order_count = len(female_orders[female_orders['product_name'] == product])
        print(f"  {i}位: {product} (売上: {sales:,}円, 注文数: {order_count}件)")
    
    # 女性客の年代別分析
    female_age_analysis = female_orders.groupby('age_category').agg({
        'product_name': 'count',
        'sales': ['sum', 'mean']
    }).round(0)
    female_age_analysis.columns = ['注文数', '売上合計', '平均単価']
    
    print(f"\n【女性客の年代別分析】")
    print(female_age_analysis)
    
    # 女性客のカテゴリ別嗜好
    female_category = female_orders.groupby('menu_category')['sales'].sum().sort_values(ascending=False)
    male_category = male_orders.groupby('menu_category')['sales'].sum()
    
    print(f"\n【女性客のカテゴリ別注文傾向】")
    total_female_sales = female_category.sum()
    for category, sales in female_category.items():
        percentage = (sales / total_female_sales * 100)
        print(f"  • {category}: {sales:,}円 ({percentage:.1f}%)")
    
    # 女性 vs 男性の比較
    gender_comparison = []
    all_categories = set(female_category.index) | set(male_category.index)
    
    for category in all_categories:
        female_pct = (female_category.get(category, 0) / total_female_sales * 100) if total_female_sales > 0 else 0
        male_pct = (male_category.get(category, 0) / male_category.sum() * 100) if male_category.sum() > 0 else 0
        gender_comparison.append({
            'category': category,
            'female_percentage': female_pct,
            'male_percentage': male_pct,
            'difference': female_pct - male_pct
        })
    
    gender_comp_df = pd.DataFrame(gender_comparison)
    gender_comp_df = gender_comp_df.sort_values('difference', ascending=False)
    
    print(f"\n【女性客 vs 男性客の嗜好比較】")
    for _, row in gender_comp_df.iterrows():
        diff_str = f"+{row['difference']:.1f}%" if row['difference'] >= 0 else f"{row['difference']:.1f}%"
        print(f"  • {row['category']}: 女性{row['female_percentage']:.1f}% vs 男性{row['male_percentage']:.1f}% ({diff_str})")
    
    # 可視化: 性別・家族グループ別分析
    plt.figure(figsize=(15, 10))
    
    # 1. 性別カテゴリ別売上比較
    plt.subplot(2, 3, 1)
    gender_category_comparison = pd.DataFrame({
        '女性': female_category / total_female_sales * 100,
        '男性': male_category / male_category.sum() * 100
    }).fillna(0)
    gender_category_comparison.plot(kind='bar', ax=plt.gca())
    plt.title('性別別メニューカテゴリ嗜好 (%)')
    plt.xlabel('メニューカテゴリ')
    plt.ylabel('割合')
    plt.xticks(rotation=45)
    plt.legend()
    
    # 2. 女性客の年代別平均単価
    plt.subplot(2, 3, 2)
    female_age_analysis['平均単価'].plot(kind='bar', color='pink', alpha=0.7, ax=plt.gca())
    plt.title('女性客の年代別平均支出')
    plt.xlabel('年代カテゴリ')
    plt.ylabel('平均金額 (円)')
    plt.xticks(rotation=45)
    
    # 3. 家族グループの特徴（もし存在する場合）
    plt.subplot(2, 3, 3)
    if family_groups:
        family_types = [f['family_type'] for f in family_groups]
        family_type_counts = pd.Series(family_types).value_counts()
        family_type_counts.plot(kind='pie', autopct='%1.1f%%', ax=plt.gca())
        plt.title('家族グループタイプの分布')
        plt.ylabel('')
    else:
        plt.text(0.5, 0.5, '家族グループが\n特定されませんでした', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('家族グループ分析')
        plt.axis('off')
    
    # 4. 性別別売上分布
    plt.subplot(2, 3, 4)
    gender_sales = merged_df.groupby('gender')['sales'].sum()
    # 性別ラベルを日本語に変換
    gender_labels = {'male': '男性', 'female': '女性'}
    gender_sales.index = [gender_labels.get(g, g) for g in gender_sales.index]
    gender_sales.plot(kind='bar', color=['lightblue', 'lightcoral'], ax=plt.gca())
    plt.title('性別別総売上')
    plt.xlabel('性別')
    plt.ylabel('総売上 (円)')
    plt.xticks(rotation=0)
    
    # 5. 人気商品Top5の性別比較
    plt.subplot(2, 3, 5)
    top5_products = merged_df.groupby('product_name')['sales'].sum().nlargest(5).index
    top5_gender_data = []
    for product in top5_products:
        female_sales = female_orders[female_orders['product_name'] == product]['sales'].sum()
        male_sales = male_orders[male_orders['product_name'] == product]['sales'].sum()
        top5_gender_data.append({'product': product, '女性': female_sales, '男性': male_sales})
    
    top5_df = pd.DataFrame(top5_gender_data).set_index('product')
    top5_df.plot(kind='bar', ax=plt.gca(), color=['lightcoral', 'lightblue'])
    plt.title('人気商品トップ5の性別売上')
    plt.xlabel('商品')
    plt.ylabel('売上 (円)')
    plt.xticks(rotation=45)
    plt.legend()
    
    # 6. 家族グループの注文パターン（もし存在する場合）
    plt.subplot(2, 3, 6)
    if family_orders:
        family_category_pct = family_df.groupby('menu_category')['sales'].sum() / family_df['sales'].sum() * 100
        family_category_pct.plot(kind='bar', color='lightgreen', ax=plt.gca())
        plt.title('家族グループのメニュー嗜好 (%)')
        plt.xlabel('メニューカテゴリ')
        plt.ylabel('割合')
        plt.xticks(rotation=45)
    else:
        plt.text(0.5, 0.5, '家族グループの\n注文が見つかりません', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('家族グループ注文')
        plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'family_gender_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # データをCSVで保存
    if family_orders:
        pd.DataFrame(family_orders).to_csv(os.path.join(output_dir, 'family_group_orders.csv'), index=False)
        pd.DataFrame(family_groups).to_csv(os.path.join(output_dir, 'identified_family_groups.csv'), index=False)
    
    female_orders.to_csv(os.path.join(output_dir, 'female_customer_orders.csv'), index=False)
    gender_comp_df.to_csv(os.path.join(output_dir, 'gender_comparison_analysis.csv'), index=False)
    
    print(f"\n家族グループと女性客の分析結果を保存しました")

else:
    print("女性客のデータがありません")

# --- 10. 複数人グループの詳細分析と統計 ---
print(f"\n=== 複数人グループの注文統計と顧客属性分析 ===")

# 元の顧客データから複数人グループを詳細分析
multi_person_detailed_analysis = []

for (table_id, seat_time), group_data in customer_raw.groupby(['table_id', 'seat_start_time']):
    group_size = len(group_data)
    
    if group_size > 1:  # 複数人グループのみ
        # グループの基本情報
        ages = group_data['age_category'].value_counts()
        genders = group_data['gender'].value_counts()
        
        # そのグループの注文データを取得
        group_orders = merged_df[
            (merged_df['table_id'] == table_id) & 
            (merged_df['seat_start_time'] == seat_time)
        ]
        
        # 注文統計
        total_orders = len(group_orders)
        total_sales = group_orders['sales'].sum() if len(group_orders) > 0 else 0
        avg_price = group_orders['sales'].mean() if len(group_orders) > 0 else 0
        
        # メニューカテゴリ分析
        if len(group_orders) > 0:
            group_orders_copy = group_orders.copy()
            group_orders_copy['menu_category'] = group_orders_copy['product_name'].apply(categorize_menu)
            category_orders = group_orders_copy['menu_category'].value_counts().to_dict()
            top_products = group_orders_copy.groupby('product_name')['sales'].sum().nlargest(3).to_dict()
        else:
            category_orders = {}
            top_products = {}
        
        # グループ特性の分析
        has_mixed_gender = len(genders) > 1
        has_mixed_age = len(ages) > 1
        age_span = 0
        
        # 年齢幅の計算（簡易版）
        age_weights = {'young_adult': 1, 'middle_aged': 2, 'senior': 3}
        age_values = [age_weights.get(age, 0) for age in group_data['age_category'] if age in age_weights]
        if age_values:
            age_span = max(age_values) - min(age_values)
        
        # 家族グループの判定
        is_likely_family = False
        family_indicators = []
        
        if has_mixed_gender and has_mixed_age:
            is_likely_family = True
            family_indicators.append("混合性別・年代")
        
        if age_span >= 2:  # 2世代以上の年齢差
            is_likely_family = True
            family_indicators.append("世代間年齢差")
        
        if 'senior' in ages.index and ('young_adult' in ages.index or 'middle_aged' in ages.index):
            is_likely_family = True
            family_indicators.append("親子世代構成")
        
        multi_person_detailed_analysis.append({
            'table_id': table_id,
            'seat_time': seat_time,
            'group_size': group_size,
            'male_count': genders.get('male', 0),
            'female_count': genders.get('female', 0),
            'young_adult_count': ages.get('young_adult', 0),
            'middle_aged_count': ages.get('middle_aged', 0),
            'senior_count': ages.get('senior', 0),
            'has_mixed_gender': has_mixed_gender,
            'has_mixed_age': has_mixed_age,
            'age_span': age_span,
            'is_likely_family': is_likely_family,
            'family_indicators': '; '.join(family_indicators) if family_indicators else 'なし',
            'total_orders': total_orders,
            'total_sales': total_sales,
            'avg_order_price': avg_price,
            'orders_per_person': total_orders / group_size if group_size > 0 else 0,
            'sales_per_person': total_sales / group_size if group_size > 0 else 0,
            'category_orders': category_orders,
            'top_products': top_products
        })

if multi_person_detailed_analysis:
    multi_df = pd.DataFrame(multi_person_detailed_analysis)
    
    print(f"【複数人グループの基本統計】")
    print(f"総グループ数: {len(multi_df)}組")
    print(f"平均グループサイズ: {multi_df['group_size'].mean():.1f}人")
    print(f"最大グループサイズ: {multi_df['group_size'].max()}人")
    print(f"混合性別グループ: {multi_df['has_mixed_gender'].sum()}組 ({multi_df['has_mixed_gender'].mean()*100:.1f}%)")
    print(f"混合年代グループ: {multi_df['has_mixed_age'].sum()}組 ({multi_df['has_mixed_age'].mean()*100:.1f}%)")
    print(f"家族と推定されるグループ: {multi_df['is_likely_family'].sum()}組 ({multi_df['is_likely_family'].mean()*100:.1f}%)")
    
    # グループサイズ別の詳細統計
    print(f"\n【グループサイズ別統計】")
    size_stats = multi_df.groupby('group_size').agg({
        'total_orders': ['count', 'mean', 'sum'],
        'total_sales': ['mean', 'sum'],
        'sales_per_person': 'mean',
        'orders_per_person': 'mean',
        'is_likely_family': 'mean'
    }).round(1)
    
    size_stats.columns = ['グループ数', '平均注文数', '総注文数', '平均売上', '総売上', '1人当たり売上', '1人当たり注文数', '家族率']
    print(size_stats)
    
    # 家族グループ vs 非家族グループの比較
    print(f"\n【家族グループ vs 非家族グループ比較】")
    family_groups = multi_df[multi_df['is_likely_family'] == True]
    non_family_groups = multi_df[multi_df['is_likely_family'] == False]
    
    if len(family_groups) > 0 and len(non_family_groups) > 0:
        comparison_stats = pd.DataFrame({
            '家族グループ': [
                len(family_groups),
                family_groups['group_size'].mean(),
                family_groups['total_sales'].mean(),
                family_groups['sales_per_person'].mean(),
                family_groups['orders_per_person'].mean()
            ],
            '非家族グループ': [
                len(non_family_groups),
                non_family_groups['group_size'].mean(),
                non_family_groups['total_sales'].mean(),
                non_family_groups['sales_per_person'].mean(),
                non_family_groups['orders_per_person'].mean()
            ]
        }, index=['グループ数', '平均人数', '平均売上', '1人当たり売上', '1人当たり注文数'])
        
        print(comparison_stats.round(1))
        
        # 統計的差の計算
        print(f"\n【家族 vs 非家族の差異】")
        print(f"売上差: {family_groups['total_sales'].mean() - non_family_groups['total_sales'].mean():.0f}円")
        print(f"1人当たり売上差: {family_groups['sales_per_person'].mean() - non_family_groups['sales_per_person'].mean():.0f}円")
        print(f"1人当たり注文数差: {family_groups['orders_per_person'].mean() - non_family_groups['orders_per_person'].mean():.1f}件")
    
    # 複数人グループの人気メニューカテゴリ分析
    print(f"\n【複数人グループの人気メニューカテゴリ】")
    all_categories = {}
    total_multi_orders = 0
    
    for _, group in multi_df.iterrows():
        for category, count in group['category_orders'].items():
            all_categories[category] = all_categories.get(category, 0) + count
            total_multi_orders += count
    
    if total_multi_orders > 0:
        category_ranking = sorted(all_categories.items(), key=lambda x: x[1], reverse=True)
        for i, (category, count) in enumerate(category_ranking, 1):
            percentage = (count / total_multi_orders * 100)
            print(f"  {i}位: {category} ({count}件, {percentage:.1f}%)")
        
        # 複数人グループ vs 全体の比較
        print(f"\n【複数人グループ vs 全体の注文傾向比較】")
        all_orders_category = merged_df.groupby('menu_category')['product_name'].count()
        total_all_orders = all_orders_category.sum()
        
        multi_vs_all = []
        all_category_names = set(all_categories.keys()) | set(all_orders_category.index)
        
        for category in all_category_names:
            multi_pct = (all_categories.get(category, 0) / total_multi_orders * 100) if total_multi_orders > 0 else 0
            all_pct = (all_orders_category.get(category, 0) / total_all_orders * 100) if total_all_orders > 0 else 0
            difference = multi_pct - all_pct
            
            multi_vs_all.append({
                'category': category,
                'multi_percentage': multi_pct,
                'all_percentage': all_pct,
                'difference': difference
            })
        
        multi_comparison_df = pd.DataFrame(multi_vs_all).sort_values('difference', ascending=False)
        
        for _, row in multi_comparison_df.iterrows():
            diff_str = f"+{row['difference']:.1f}%" if row['difference'] >= 0 else f"{row['difference']:.1f}%"
            print(f"  • {row['category']}: 複数人{row['multi_percentage']:.1f}% vs 全体{row['all_percentage']:.1f}% ({diff_str})")
    
    # 詳細なグループ属性分析
    print(f"\n【グループ構成別の詳細分析】")
    
    # 性別構成パターン別
    gender_patterns = []
    for _, group in multi_df.iterrows():
        if group['male_count'] > 0 and group['female_count'] > 0:
            gender_patterns.append('男女混合')
        elif group['male_count'] > 0:
            gender_patterns.append('男性のみ')
        else:
            gender_patterns.append('女性のみ')
    
    multi_df['gender_pattern'] = gender_patterns
    
    gender_pattern_stats = multi_df.groupby('gender_pattern').agg({
        'group_size': ['count', 'mean'],
        'total_sales': 'mean',
        'sales_per_person': 'mean',
        'is_likely_family': 'mean'
    }).round(1)
    
    gender_pattern_stats.columns = ['グループ数', '平均人数', '平均売上', '1人当たり売上', '家族率']
    print(f"\n【性別構成パターン別統計】")
    print(gender_pattern_stats)
    
    # 年代構成パターン別
    age_patterns = []
    for _, group in multi_df.iterrows():
        age_types = []
        if group['young_adult_count'] > 0:
            age_types.append('若年')
        if group['middle_aged_count'] > 0:
            age_types.append('中年')
        if group['senior_count'] > 0:
            age_types.append('高齢')
        age_patterns.append('+'.join(age_types) if age_types else '不明')
    
    multi_df['age_pattern'] = age_patterns
    
    age_pattern_stats = multi_df.groupby('age_pattern').agg({
        'group_size': ['count', 'mean'],
        'total_sales': 'mean',
        'sales_per_person': 'mean',
        'is_likely_family': 'mean'
    }).round(1)
    
    age_pattern_stats.columns = ['グループ数', '平均人数', '平均売上', '1人当たり売上', '家族率']
    print(f"\n【年代構成パターン別統計】")
    print(age_pattern_stats)
    
    # 最も多い注文をしたグループの詳細
    print(f"\n【高注文・高売上グループの事例】")
    top_sales_groups = multi_df.nlargest(3, 'total_sales')
    
    for i, (_, group) in enumerate(top_sales_groups.iterrows(), 1):
        print(f"\n{i}位: テーブル{group['table_id']} ({group['group_size']}人グループ)")
        print(f"   売上: {group['total_sales']:,}円 (1人当たり: {group['sales_per_person']:,.0f}円)")
        print(f"   注文数: {group['total_orders']}件 (1人当たり: {group['orders_per_person']:.1f}件)")
        print(f"   構成: 男性{group['male_count']}人, 女性{group['female_count']}人")
        print(f"   年代: 若年{group['young_adult_count']}人, 中年{group['middle_aged_count']}人, 高齢{group['senior_count']}人")
        print(f"   家族推定: {'はい' if group['is_likely_family'] else 'いいえ'} ({group['family_indicators']})")
        
        if group['top_products']:
            print(f"   人気商品: {', '.join(list(group['top_products'].keys())[:3])}")
    
    # 可視化: 複数人グループの詳細分析
    plt.figure(figsize=(16, 12))
    
    # 1. グループサイズ分布
    plt.subplot(3, 3, 1)
    multi_df['group_size'].value_counts().sort_index().plot(kind='bar', color='skyblue', ax=plt.gca())
    plt.title('グループサイズ分布')
    plt.xlabel('グループ人数')
    plt.ylabel('グループ数')
    plt.xticks(rotation=0)
    
    # 2. 家族 vs 非家族の売上分布
    plt.subplot(3, 3, 2)
    if len(family_groups) > 0 and len(non_family_groups) > 0:
        plt.boxplot([family_groups['total_sales'], non_family_groups['total_sales']], 
                   labels=['家族', '非家族'])
        plt.title('売上分布: 家族 vs 非家族')
        plt.ylabel('総売上 (円)')
    else:
        plt.text(0.5, 0.5, '比較データが\n不十分です', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('家族 vs 非家族 売上')
        plt.axis('off')
    
    # 3. 性別構成パターン
    plt.subplot(3, 3, 3)
    gender_pattern_counts = multi_df['gender_pattern'].value_counts()
    gender_pattern_counts.plot(kind='pie', autopct='%1.1f%%', ax=plt.gca())
    plt.title('性別構成パターン')
    plt.ylabel('')
    
    # 4. 年代構成パターン
    plt.subplot(3, 3, 4)
    age_pattern_counts = multi_df['age_pattern'].value_counts()
    if len(age_pattern_counts) <= 6:  # 表示可能な数の場合のみ
        age_pattern_counts.plot(kind='bar', color='lightgreen', ax=plt.gca())
        plt.title('年代構成パターン')
        plt.xlabel('年代パターン')
        plt.ylabel('グループ数')
        plt.xticks(rotation=45)
    else:
        # 多すぎる場合は上位6つのみ
        age_pattern_counts.head(6).plot(kind='bar', color='lightgreen', ax=plt.gca())
        plt.title('年代構成パターン トップ6')
        plt.xlabel('年代パターン')
        plt.ylabel('グループ数')
        plt.xticks(rotation=45)
    
    # 5. グループサイズ vs 1人当たり売上
    plt.subplot(3, 3, 5)
    colors = ['red' if is_family else 'blue' for is_family in multi_df['is_likely_family']]
    plt.scatter(multi_df['group_size'], multi_df['sales_per_person'], 
               c=colors, alpha=0.6)
    plt.xlabel('グループ人数')
    plt.ylabel('1人当たり売上 (円)')
    plt.title('グループサイズ vs 1人当たり売上')
    # 凡例を手動で作成
    import matplotlib.patches as mpatches
    blue_patch = mpatches.Patch(color='blue', label='非家族')
    red_patch = mpatches.Patch(color='red', label='家族')
    plt.legend(handles=[blue_patch, red_patch], loc='upper right')
    
    # 6. 家族グループの年代分布
    plt.subplot(3, 3, 6)
    if len(family_groups) > 0:
        family_age_data = {
            '若年': family_groups['young_adult_count'].sum(),
            '中年': family_groups['middle_aged_count'].sum(),
            '高齢': family_groups['senior_count'].sum()
        }
        plt.pie(family_age_data.values(), labels=family_age_data.keys(), autopct='%1.1f%%')
        plt.title('家族グループの年代分布')
    else:
        plt.text(0.5, 0.5, '家族グループが\n特定されませんでした', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('家族グループ年代分布')
        plt.axis('off')
    
    # 7. 複数人グループのメニューカテゴリ嗜好
    plt.subplot(3, 3, 7)
    if all_categories:
        category_series = pd.Series(all_categories)
        category_series.plot(kind='bar', color='orange', ax=plt.gca())
        plt.title('メニューカテゴリ嗜好\n(複数人グループ)')
        plt.xlabel('メニューカテゴリ')
        plt.ylabel('注文数')
        plt.xticks(rotation=45)
    else:
        plt.text(0.5, 0.5, '注文データが\nありません', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('メニューカテゴリ嗜好')
        plt.axis('off')
    
    # 8. 注文数 vs 売上の関係
    plt.subplot(3, 3, 8)
    scatter = plt.scatter(multi_df['total_orders'], multi_df['total_sales'], 
               c=multi_df['group_size'], cmap='viridis', alpha=0.7)
    plt.colorbar(scatter, label='グループ人数')
    plt.xlabel('総注文数')
    plt.ylabel('総売上 (円)')
    plt.title('注文数 vs 売上 (グループ人数別)')
    
    # 9. 家族判定要因の分析
    plt.subplot(3, 3, 9)
    if len(family_groups) > 0:
        family_indicator_counts = {}
        for indicators in family_groups['family_indicators']:
            if indicators != 'なし':
                for indicator in indicators.split('; '):
                    family_indicator_counts[indicator] = family_indicator_counts.get(indicator, 0) + 1
        
        if family_indicator_counts:
            indicator_series = pd.Series(family_indicator_counts)
            indicator_series.plot(kind='bar', color='lightcoral', ax=plt.gca())
            plt.title('家族グループ判定要因')
            plt.xlabel('判定要因')
            plt.ylabel('頻度')
            plt.xticks(rotation=45)
        else:
            plt.text(0.5, 0.5, '家族判定要因が\n見つかりません', 
                    ha='center', va='center', transform=plt.gca().transAxes)
            plt.title('家族判定要因')
            plt.axis('off')
    else:
        plt.text(0.5, 0.5, '家族グループが\n特定されませんでした', 
                ha='center', va='center', transform=plt.gca().transAxes)
        plt.title('家族判定要因')
        plt.axis('off')
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'multi_person_group_detailed_analysis.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    # 詳細データをCSVで保存
    multi_df.to_csv(os.path.join(output_dir, 'multi_person_group_detailed_stats.csv'), index=False)
    size_stats.to_csv(os.path.join(output_dir, 'group_size_statistics.csv'))
    
    if len(family_groups) > 0 and len(non_family_groups) > 0:
        comparison_stats.to_csv(os.path.join(output_dir, 'family_vs_non_family_comparison.csv'))
    
    gender_pattern_stats.to_csv(os.path.join(output_dir, 'gender_pattern_statistics.csv'))
    age_pattern_stats.to_csv(os.path.join(output_dir, 'age_pattern_statistics.csv'))
    multi_comparison_df.to_csv(os.path.join(output_dir, 'multi_group_vs_all_comparison.csv'), index=False)
    
    print(f"\n複数人グループの詳細分析結果を保存しました")
    print(f"保存されたファイル:")
    print(f"  - multi_person_group_detailed_stats.csv: 全グループの詳細統計")
    print(f"  - group_size_statistics.csv: グループサイズ別統計")
    print(f"  - gender_pattern_statistics.csv: 性別構成パターン別統計")
    print(f"  - age_pattern_statistics.csv: 年代構成パターン別統計")
    print(f"  - multi_group_vs_all_comparison.csv: 複数人グループ vs 全体比較")
    if len(family_groups) > 0 and len(non_family_groups) > 0:
        print(f"  - family_vs_non_family_comparison.csv: 家族 vs 非家族グループ比較")

else:
    print("複数人グループのデータが見つかりませんでした")

print(f"\n--- 全ての分析が完了しました ---")