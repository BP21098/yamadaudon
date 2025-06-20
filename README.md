yamadaudon
仮想環境をコミットできない。
ブランチを退避：git checkout --orphan new-main
任意ブランチに切り替え：git checkout main(ブランチ名)

ポート番号が使われている場合
lsof -ti :5001 | xargs kill -9

仮想環境有効化：source env/bin/activate