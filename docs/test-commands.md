# テスト実行手順

リポジトリのルートで次のコマンドを実行する。

```sh
python3 manage.py check
python3 manage.py test
```

CIと同じ確認を行う場合は、依存関係をインストールした後にflake8とDjangoテストを実行する。
