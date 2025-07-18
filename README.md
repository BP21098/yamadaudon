yamadaudon
仮想環境をコミットできない。
ブランチを退避：git checkout --orphan new-main
任意ブランチに切り替え：git checkout main(ブランチ名)

ポート番号が使われている場合
lsof -ti :5001 | xargs kill -9

仮想環境有効化
source env/bin/activate





IPアドレスの調べ方（コマンド）
ifconfig | grep inet
inet 127.0.0.1 netmask 0xff000000
inet6 ::1 prefixlen 128
inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1
inet6 fe80::4b5:6dfc:28cc:a39f%en0 prefixlen 64 secured scopeid 0xb
inet 172.31.81.113 netmask 0xffffc000 broadcast 172.31.127.255
inet6 fe80::6466:33ff:feef:fbfe%awdl0 prefixlen 64 scopeid 0xd
inet6 fe80::6466:33ff:feef:fbfe%llw0 prefixlen 64 scopeid 0xe
inet6 fe80::6ba4:bbb0:4bb8:b2b9%utun1 prefixlen 64 scopeid 0x10
inet6 fe80::2d0:d1db:4515:5b74%utun2 prefixlen 64 scopeid 0x11
inet6 fe80::ce81:b1c:bd2c:69e%utun3 prefixlen 64 scopeid 0x12
inet 172.30.165.208 --> 172.30.165.208 netmask 0xffffffff
inet6 fe80::5cf1:d8ba:e4fa:a417%utun5 prefixlen 64 scopeid 0x14
inet6 fe80::1d47:1f86:5caf:b7fb%utun6 prefixlen 64 scopeid 0x15
inet6 fe80::b34b:fa3:cd04:ebe9%utun7 prefixlen 64 scopeid 0x16
inet6 fe80::c5b5:4341:38a0:1ec8%utun8 prefixlen 64 scopeid 0x17
inet6 fe80::437e:e706:558d:d7e2%utun0 prefixlen 64 scopeid 0x18


# アクセスできるURL： 
# http://127.0.0.1:5001  # お客様用アプリ
# http://127.0.0.1:5002  # 店員用アプリ



→IPアドレス：172.31.81.113
http://172.31.81.113:5001/
http://172.31.81.113:5002/