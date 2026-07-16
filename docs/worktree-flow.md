# Issue・ブランチ・worktree運用

作業ごとに次の対応を1対1で作成する。

- Issue 1件
- `feature/issue-<番号>-<内容>` ブランチ1本
- 専用worktree 1つ

変更対象を分け、各worktreeでテストとコミットを完了してからpushする。PR本文には対応Issueを `Closes #番号` として記載する。
