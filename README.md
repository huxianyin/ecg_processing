# Overview
biopluxで取得した心電データを処理するパッケージの使い方に関するデモ

### package
```
ecg_processing
├ sample_data
│   └ biopluxデータ
├ 使い方.ipynb                    　　... デモ用のmainコード
├ feature_extraction.py           ... データ処理，特徴量抽出関数群
└ utils.py                                ... 汎用関数群（データの読込み）
```

# Setting

- python version : 3.6.1


# Run

```sh
pip install -r requirements.txt
jupyter notebook
```
jupyter notebook の使い方は以下に参考してください：https://note.com/mc_kurita/n/n4261e54d2539

### Steps:

1. ブラウザーで　http://localhost:8888/tree　を開く
2. 使い方.ipynbをクリックして開く
3. コードを実行してみよう
