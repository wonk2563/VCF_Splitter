# VCF檔案處理腳本使用說明

## 功能概述
1. 將vCard 2.1 升級到 3.0 格式
2. 分割大檔案為多個子檔案（預設每個檔案 10000 個聯絡人）
3. 自動處理以下轉換：
   - 解碼 QUOTED-PRINTABLE 編碼內容
   - 移除參數 (ENCODING=QUOTED-PRINTABLE)
   - 特殊字符轉義處理

## 環境要求
- Python 3.6+
- 輸入檔案需為 UTF-8 編碼

## 安裝與使用
注意：本文檔中使用的數據為隨機生成，與真實人物無關。
正式使用時，請確保遵守個資法相關規定。

```bash
# 執行命令
python main.py 輸入檔案.vcf [聯絡人數量上限] (可選) [輸出前綴] (可選)

# 範例
python main.py test_data/example.vcf
python main.py test_data/example.vcf 10000
python main.py test_data/example.vcf 10000 output_v3
```

# 輸入
```vcard
BEGIN:VCARD
VERSION:2.1
N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=E9=99=B3=E5=BB=A3=E5=BF=97
TEL;CELL;PREF:0987-654-321
ADR;PREF;WORK;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:;;=32=36=E8=99=9F=20=E4=B8=AD=E6=AD=A3=E8=B7=AF
END:VCARD
```

# 輸出
```vcard
BEGIN:VCARD
VERSION:3.0
N:陳廣志
TEL;CELL;PREF:0987-654-321
ADR;PREF;WORK:;;26號 中正路
END:VCARD
```