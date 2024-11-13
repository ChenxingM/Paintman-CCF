# Paintman 用カラーチャートファイル (CCF) 生成・読み取りプログラム

## 概要
- このプロジェクトは、Paintman用カラーチャートファイル（CCF）を作成・読み取りするための2つのPythonプログラムから構成されています。`generate_ccf.py` は指定された色データからCCFファイルを生成し、`read_ccf.py` は作成されたCCFファイルを読み取り、色の情報を出力します。
- 最後にCCFファイルの構造について解析を行いました。
---

## ファイル構成
1. **`generate_ccf.py`**: カラーチャートファイル（CCF）を作成するプログラム。
2. **`read_ccf.py`**: CCFファイルを読み取り、色名とRGB値を出力するプログラム。

---

## `generate_ccf.py` の説明
### 概要
このプログラムは、RGB値と色名を含むデータからカラーチャートファイル（CCF）を生成します。RGB値は8ビットから16ビットに変換され、色名はASCIIまたはGB2312でエンコードされます。

### 使用方法
1. `example_color_data` にRGB値と色名のタプルのリストを定義します。
2. `ColorChartFile` クラスのインスタンスを作成し、`create_ccf_file` メソッドを使用してCCFファイルを生成します。
3. 生成されたファイルは指定したパスに保存されます。
4. 生成されたファイルは `read_ccf.py` で読み取ることができます。また、Paintmanで開くこともできます。
![Paintmanで開いたCCFファイル](screenshot/output_sample.png)

### コードの説明
- **`dec_to_hex_byte` メソッド**: 10進数の値を1バイトの16進数に変換します。
- **`encode_label` メソッド**: 色名をエンコードし、英数字と記号はASCII、それ以外はGB2312でエンコードします。
- **`add_color_block` メソッド**: RGB値と色名をバイト配列に追加し、16バイトのブロックに整形します。
- **`fill_to_target_length` メソッド**: バイト配列を指定された長さまで埋めます。
- **`create_ccf_file` メソッド**: CCFファイルを作成し、保存します。

---

## `read_ccf.py` の説明
### 概要
このプログラムは、CCFファイルを読み取り、各色のRGB値と色名を出力します。16ビットのRGB値は8ビットに変換されて表示されます。

### 使用方法
1. 読み取りたいCCFファイルのパスを指定します。
2. `CCFFileReader` クラスのインスタンスを作成し、`read_ccf_file` メソッドを使用して色データを取得します。
3. 各色の名前と8ビットRGB値が出力されます。

### コードの説明
- **`hex_byte_to_dec` メソッド**: 16進数のバイトを10進数に変換します。
- **`decode_label` メソッド**: 色名をデコードし、英数字はASCII、それ以外はGB2312としてデコードします。
- **`read_ccf_file` メソッド**: CCFファイルを読み取り、色データをリストとして返します。

---

## プログラムの実行結果
1. **`generate_ccf.py`** を実行すると、指定したRGB値と色名を持つCCFファイルが生成され、ファイルパスが表示されます。
2. **`read_ccf.py`** を実行すると、CCFファイルを読み取り、各色の名前と8ビットRGB値がコンソールに表示され、合計の色数も出力されます。

---

## 使用例
### `generate_ccf.py`
```plaintext
CCFファイルが /path/to/your/directory/output_file.ccf に作成されました。
```

### `read_ccf.py`
```plaintext
ラベル: Red 	8bit RGB: (255, 0, 0)
ラベル: Green 	8bit RGB: (0, 255, 0)
ラベル: Blue 	8bit RGB: (0, 0, 255)
ラベル: 黑色 	8bit RGB: (0, 0, 0)
ラベル: White白色 	8bit RGB: (255, 255, 255)
ラベル: Gray灰色 	8bit RGB: (128, 128, 128)
ラベル: Yellow 	8bit RGB: (255, 255, 0)
ラベル: Cyan 	8bit RGB: (0, 255, 255)
ラベル: Magenta 	8bit RGB: (255, 0, 255)
合計 9 色が見つかりました。
```

---

## 注意事項
1. ラベルのエンコードは、英数字と記号はASCII、その他はGB2312で行います。ラベルが15バイトを超える場合は切り捨てられます。
2. RGB値は16ビットの形式で保存され、読み取り時に8ビットに変換されます。

---
## CCFファイル構造解析

#### ファイル紹介
- **拡張子**: `*.ccf`
- CCFファイルはRetas Studioシリーズのうち、Paintmanのカラーチャート(Color Chart)ファイルで、色データを保存するために使用されます。
- CCFファイルはバイナリファイルで、各ファイルには1280個の色データブロックが含まれ、各色データブロックは12バイトのRGBデータと16バイトのASCIIエンコードされたラベルから構成されます。

#### ファイルヘッダ
- **ヘッダの開始 (SOH)**: ファイルは`00`バイトで始まり、その後に`64`が続きます。これは特定のフォーマット識別子またはバージョン番号を表す可能性があります。

#### 色データブロック
各色データブロックには以下の部分が含まれます：
- **色値**: RGBの各成分は16bit RGBで表され、8bit RGBであれば、各バイトが一回繰り返されるように見えます。
  - 例: 8bit色`#C5E8F6`は`C5 C5 E8 E8 F6 F6`として保存されます。
- **ラベルの長さ**: 各色ブロックの直後には、ラベルのバイト数、最長16バイトで、16進法で保存されます。
- **ラベル**: 終了制御文字の直後には、色のラベルのうち、英数字、記号は`ASCII`形式で、日本語、中国語は`GB2312`でエンコードされて続きます。
  - 例："NOR"`4E 4F 52`、"普通"`C6 D5 CD A8`、"あか"`A4 A2 A4 AB`。
- **パディング**: ラベルの後の残りのバイトは`00`で埋められ、全体のラベルとパディングが合計16バイトになるようにします。

#### ファイルのパディング
- 指定された色データブロックを埋めた後、残りの空間は次のようなパターンで`0x6E01`まで埋められます：
  - 白色（`FF FF FF FF FF FF`）、ラベルなし（`''`）、その後`00`で16バイトになるまで埋められます。
  - このパターンがファイルの最後まで繰り返されます。
  - 合計全部1280色、10ページに分かれてPaintmanで表示されます。

#### ファイルの末尾
- ファイルの長さは正確に`0x6E01`バイトであるべきです。

---
## ライセンス
- MITライセンス

## その他
-　CCFファイルの構造解析については、間違いや改善点があれば、Issueを作成してください。