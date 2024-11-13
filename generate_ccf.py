import os.path
from typing import List, Tuple

import unicodedata


class ColorChartFile:
    def __init__(self, color_data: List[Tuple[Tuple[int, int, int], str]]):
        """
        ColorChartFile クラスを初期化します。

        :param color_data: RGBタプル (int, int, int) とラベル (str) を含むタプルのリスト。
        """
        self.color_data: List[Tuple[Tuple[int, int, int], str]] = color_data

    def dec_to_hex_byte(self, value: int) -> bytes:
        """
        10進数の値を1バイトの16進数に変換します。

        :param value: 整数値 (0-255)。
        :return: 値の16進数バイト表現。
        """
        return value.to_bytes(1, 'big')

    def encode_label(self, label: str) -> bytes:
        """
        ラベルをエンコードします。英数字と記号はASCII、その他はGB2312を使用。

        :param label: ラベル文字列。
        :return: エンコードされたバイト列。
        """
        encoded_bytes = bytearray()

        for char in label:
            # 英数字と記号はASCIIでエンコード
            if char.isascii():
                encoded_bytes.extend(char.encode('ascii'))
            else:
                # Unicodeデータベースを使用して文字の種類を確認
                char_category = unicodedata.name(char)
                try:
                    if "CJK UNIFIED IDEOGRAPH" in char_category:
                        # もし文字が中国語の漢字であれば、EUC-CNでエンコード
                        encoded_bytes.extend(char.encode('euc_cn'))
                    elif "HIRAGANA" in char_category or "KATAKANA" in char_category or "CJK" in char_category:
                        # もし文字が日本語の文字（ひらがな、カタカナ、または日本語の漢字）であれば、EUC-JPでエンコード
                        encoded_bytes.extend(char.encode('euc_jp'))
                    else:
                        # もし文字が中国語や日本語の文字でない場合、例外を発生させる
                        raise UnicodeEncodeError("サポートされていない文字エンコード", char, -1, -1,
                                                 "EUC-CNまたはEUC-JPでサポートされていない文字です。")
                except UnicodeEncodeError as e:
                    # エンコードエラーを報告
                    raise UnicodeEncodeError(f"文字 '{char}' のEUC-CNまたはEUC-JPでのエンコードに失敗しました: {e}")

        return bytes(encoded_bytes)

    def add_color_block(self, content: bytearray, rgb: Tuple[int, int, int], label: str) -> None:
        """
        色のブロックをバイト配列に追加します。

        :param content: バイト配列。
        :param rgb: RGBタプル (int, int, int)。
        :param label: ラベル (str)。
        """
        r, g, b = rgb
        # 8bit RGB値を 16bit に変換し、それぞれの文字を2回繰り返す
        content.extend(self.dec_to_hex_byte(r) * 2)
        content.extend(self.dec_to_hex_byte(g) * 2)
        content.extend(self.dec_to_hex_byte(b) * 2)

        # ラベルをエンコード
        label_bytes = self.encode_label(label)
        label_bytes_length: int = len(label_bytes)  # エンコード後のバイト数
        if label_bytes_length > 15:
            label_bytes = label_bytes[:15]  # 15バイト以上の場合は切り捨て

        content.append(label_bytes_length)  # ラベルの長さ (ASCII形式) を追加

        # エンコードされたラベルを追加
        content.extend(label_bytes)

        # 文字ブロック長を16バイトにするためにゼロでパディング
        padding_length: int = 15 - label_bytes_length
        if padding_length > 0 and label_bytes_length < 15:
            content.extend([0] * padding_length)

    def fill_to_target_length(self, content: bytearray, target_length: int) -> None:
        """
        指定された長さまでバイト配列を埋めます。

        :param content: バイト配列。
        :param target_length: 目標の長さ (int)。
        """
        content.extend([0xFF] * 6)
        fill_pattern: List[int] = [0] * 16 + [0xFF] * 6
        fill_length = target_length - len(content) - 16  # 最後の16個のゼロを除外

        if fill_length > 0:
            full_patterns, extra_bytes = divmod(fill_length, len(fill_pattern))
            content.extend(fill_pattern * full_patterns)
            content.extend(fill_pattern[:extra_bytes])

        # 最後の16個のゼロを追加
        content.extend([0] * 16)

    def create_ccf_file(self, output_file_path: str) -> None:
        """
        カラーチャートファイル (CCF) を作成し、指定されたファイルパスに保存します。

        :param output_file_path: CCFファイルを保存するファイルパス。
        """
        content: bytearray = bytearray()
        # ファイルヘッダーを追加
        content.append(0)  # SOH
        content.extend(self.dec_to_hex_byte(100))  # d

        # 各色とラベルをバイト配列に追加
        for rgb, label in self.color_data:
            self.add_color_block(content, rgb, label)

        # バイト配列を0x6E01まで埋める
        target_length: int = 0x6E01
        self.fill_to_target_length(content, target_length)

        content.append(0)  # 終端のバイトを追加

        # ファイルに書き込む
        with open(output_file_path, 'wb') as file:
            file.write(content)

# 使用例
if __name__ == "__main__":
    # 例のカラーデータ: 8bit RGB値とラベルのリスト
    example_color_data: List[Tuple[Tuple[int, int, int], str]] = [
        ((255, 0, 0), "Red"),
        ((0, 255, 0), "Green"),
        ((0, 0, 255), "Blue"),
        ((0, 0, 0), "黑色"), # 中国語の文字
        ((255, 255, 255), "White白色"),
        ((128, 128, 128), "Gray灰色"),
        ((255, 255, 0), "Yellow"),
        ((0, 255, 255), "Cyanシアン"), # 日本語の文字
        ((255, 0, 255), "Magenta")
    ]

    # ColorChartFile クラスのインスタンスを作成
    color_chart = ColorChartFile(example_color_data)

    # CCFファイルを作成
    ccf_file_path: str = "output_file.ccf"
    color_chart.create_ccf_file(ccf_file_path)
    print(f"CCFファイルが {os.path.abspath(ccf_file_path)} に作成されました。")
