# TTT_hakkutsu
## 概要
外気浴のスペースが満員で，満足に整うことができないという課題を解決するための，整いスペース予約システム

<br>

## 作成に至った経緯
2024年9月24日から9月26日に開催されたハックツハッカソンスピノカップに出場した．「アツすぎる」というお題に対して，チームメンバー全員がサウナ好きということで
サ活における課題を解決するプロダクトを作成した．

<br>

## 詳細
[Topa'z_TTT_整know](https://topaz.dev/projects/1a5a4ffedaa05c7a06b4)

[progate賞をいただきました](https://x.com/Hackz_team/status/1839221550186377516?ref_src=twsrc%5Egoogle%7Ctwcamp%5Eserp%7Ctwgr%5Etweet)

<br>

## 実行準備
backend直下にYOLOXのリポジトリをclone

```bash
git clone -c core.ignorecase=true https://github.com/Megvii-BaseDetection/YOLOX.git
```

依存関係のインストール

```bash
cd YOLOX
pip install -e .
```

<br>

## 実行方法

### 1. Flask を仮想環境で実行

backend ディレクトリに移動

```bash
cd backend
```

仮想環境起動

```bash
source bin/activate
```

Flask 実行

```bash
python app.py
```

### 2. next.js 実行

frontend ディレクトリに移動

```bash
cd frontend
```

実行

```bash
npm run dev
```

### 3. json-server の実行方法

frontend ディレクトリで以下のコマンドを実行する。

```bash
npx json-server --watch data.json -p 3000
```
