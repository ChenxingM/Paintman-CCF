from typing import List, Tuple
import os


class CCFFileReader:
    def __init__(self, file_path: str):
        """
        CCFFileReader クラスを初期化します。

        :param file_path: 読み込む CCF ファイルのパス。
        """
        self.file_path: str = file_path

    def hex_byte_to_dec(self, byte_data: bytes) -> int:
        """
        16進数バイトを10進数に変換します。

        :param byte_data: 1バイトのデータ。
        :return: 10進数の整数値。
        """
        return int.from_bytes(byte_data, 'big')

    def decode_label(self, label_bytes: bytes) -> str:
        """
        ラベルをデコードします。英数字と記号はASCII、中国語、日本語の文字はGB18030でデコードします。

        :param label_bytes: エンコードされたラベルのバイト列。
        :return: デコードされたラベル文字列。
        """
        decoded_label = ""
        i = 0
        while i < len(label_bytes):
            if label_bytes[i] <= 127:  # ASCII範囲内の場合
                decoded_label += label_bytes[i:i + 1].decode('ascii')
                i += 1
            else:
                try:
                    # GB18030でデコード
                    decoded_label += label_bytes[i:i + 2].decode('gb18030') # GB18030は、EUC-CNやEUC-JPに含まれない文字をサポート
                    i += 2
                except UnicodeDecodeError as e:
                    print(f"UnicodeDecodeError: {e}")
                    break

        return decoded_label

    def read_ccf_file(self) -> List[Tuple[str, Tuple[int, int, int]]]:
        """
        CCFファイルを読み込み、色名とRGB値のリストを返します。

        :return: (色名, RGB値) のタプルのリスト。
        """
        color_data: List[Tuple[str, Tuple[int, int, int]]] = []

        with open(self.file_path, 'rb') as file:
            # 読み込み開始（最初の2バイトはヘッダーなのでスキップ）
            file.read(2)

            while True:
                # RGB値を読み取る（16bit RGB）
                r_bytes = file.read(2)
                g_bytes = file.read(2)
                b_bytes = file.read(2)

                # 終端に達した場合、ループを終了
                if not r_bytes or not g_bytes or not b_bytes:
                    break

                # RGB値を10進数に変換
                r = self.hex_byte_to_dec(r_bytes)
                g = self.hex_byte_to_dec(g_bytes)
                b = self.hex_byte_to_dec(b_bytes)

                # ラベル長を読み取り
                label_length = self.hex_byte_to_dec(file.read(1))

                # ラベルを読み取り、デコード
                label_bytes = file.read(label_length)
                label = self.decode_label(label_bytes)

                # 色データをリストに追加
                color_data.append((label, (r, g, b)))

                # パディングをスキップして次の色ブロックへ（15バイトに合わせるための0パディング）
                padding_length = 15 - label_length
                file.read(padding_length)

        return color_data


# 使用例
if __name__ == "__main__":
    # 読み込む CCF ファイルのパス
    ccf_file_path = "output_file.ccf"

    # CCFFileReader クラスのインスタンスを作成
    reader = CCFFileReader(ccf_file_path)

    # CCF ファイルを読み込み
    color_data = reader.read_ccf_file()

    # 色名とRGB値を出力
    cnt = 0
    for label, rgb in color_data:
        if label:
            # 8bit RGB値に変換
            r_8bit = rgb[0] // 257
            g_8bit = rgb[1] // 257
            b_8bit = rgb[2] // 257
            print(f"ラベル: {label} \t8bit RGB: ({r_8bit}, {g_8bit}, {b_8bit})")
            cnt += 1
    print(f"合計 {cnt} 色が見つかりました。")
