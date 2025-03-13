import quopri
import sys
import os

def decode_quoted_printable(value, charset='UTF-8'):
    try:
        decoded_bytes = quopri.decodestring(value)
        return decoded_bytes.decode(charset)
    except:
        return value

def process_contact(contact_lines):
    merged_lines = []
    buffer = ''
    
    # 合併被分割的QP編碼行
    for line in contact_lines:
        stripped = line.rstrip('\r\n')
        if buffer:
            if stripped.endswith('='):
                buffer += stripped[:-1]
            else:
                merged_lines.append(buffer + stripped)
                buffer = ''
        else:
            if stripped.endswith('='):
                buffer = stripped[:-1]
            else:
                merged_lines.append(stripped)
    if buffer:
        merged_lines.append(buffer)

    decoded_lines = []
    vcard_version = '3.0'  # 轉換版本號
    
    for line in merged_lines:
        # 轉換版本號
        if line.startswith('VERSION:'):
            decoded_lines.append(f'VERSION:{vcard_version}')
            continue
            
        if ':' not in line:
            decoded_lines.append(line)
            continue

        parts = line.split(':', 1)
        prop_part = parts[0]
        value_part = parts[1] if len(parts) > 1 else ''

        # 處理參數
        params = prop_part.split(';')
        prop_name = params[0]
        new_params = []
        charset = 'UTF-8'
        encoding = None

        # 處理V3.0的參數格式
        for param in params[1:]:
            if '=' in param:
                key, val = param.split('=', 1)
                key = key.upper()
                if key == 'ENCODING':
                    encoding = val.upper()
                elif key == 'CHARSET':
                    charset = val.upper()
                else:
                    # V3.0參數格式轉換
                    new_params.append(f'{key}={val}')
            else:
                new_params.append(param)

        # 處理編碼轉換
        decoded_value = value_part
        if encoding == 'QUOTED-PRINTABLE':
            decoded_value = decode_quoted_printable(value_part, charset)
            # V3.0不再需要ENCODING參數
            if 'ENCODING=QUOTED-PRINTABLE' in new_params:
                new_params.remove('ENCODING=QUOTED-PRINTABLE')

        # 轉換特殊屬性
        if prop_name == 'TEL' and encoding == 'QUOTED-PRINTABLE':
            decoded_value = decoded_value.replace(' ', '').replace('-', '')

        # 構建新的屬性行
        new_prop = prop_name
        if new_params:
            new_prop += ';' + ';'.join(new_params)
        
        # 處理V3.0的格式要求
        if prop_name in ['N', 'FN'] and 'CHARSET' in new_params:
            new_prop = new_prop.replace('CHARSET=', 'CHARSET=')
            decoded_value = decoded_value.replace('\\', '\\\\').replace(',', '\\,')

        decoded_line = f"{new_prop}:{decoded_value}"
        decoded_lines.append(decoded_line)
    
    return decoded_lines

def split_vcf(input_file, output_prefix, chunk_size):
    contacts = []
    current_contact = []
    in_contact = False

    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped == 'BEGIN:VCARD':
                in_contact = True
                current_contact = [stripped]
            elif stripped == 'END:VCARD':
                current_contact.append(stripped)
                contacts.append(current_contact)
                current_contact = []
                in_contact = False
            elif in_contact:
                current_contact.append(line.rstrip('\r\n'))

    file_count = 0
    for i in range(0, len(contacts), chunk_size):
        file_count += 1
        output_file = f"{output_prefix}_{file_count}.vcf"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for contact in contacts[i:i+chunk_size]:
                f.write('BEGIN:VCARD\nVERSION:3.0\n')  # 添加統一版本頭
                processed = process_contact(contact)
                # 跳過原始的BEGIN和VERSION行
                filtered = [line for line in processed 
                          if not line.startswith('BEGIN:VCARD') 
                          and not line.startswith('VERSION:')]
                f.write('\n'.join(filtered))
                f.write('\n')  # 保證每個vCard以空行分隔

    print(f"成功分割為 {file_count} 個文件")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("使用方法: python main.py <input_file> [chunk_size](optional) [output_prefix](optional)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    chunk_size = int(sys.argv[2]) if len(sys.argv) > 2 else 10000
    output_prefix = sys.argv[3] if len(sys.argv) > 3 else 'contacts_v3'
    
    if not os.path.exists(input_file):
        print(f"錯誤：文件 {input_file} 不存在")
        sys.exit(1)

    split_vcf(input_file, output_prefix, chunk_size)