# TTT_hakkutu

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
