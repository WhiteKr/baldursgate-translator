import xml.etree.ElementTree as ET
import os
import time
import shutil
from googletrans import Translator

def backup_original_file(file_path):
    base_name = os.path.splitext(file_path)[0]
    backup_path = f"{base_name}_bak.xml"
    shutil.copy(file_path, backup_path)
    print(f"Backup of the original file is created at {backup_path}")

def google_translate(text, target_language="ko"):
    translator = Translator()
    max_retries = 5  # 최대 재시도 횟수
    retry_delay = 5  # 재시도 사이의 딜레이 (초)
    
    for attempt in range(max_retries):
        try:
            return translator.translate(text, dest=target_language).text
        except Exception as e:
            print(f"Translation failed with error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("Maximum retries reached. Translation failed.")
    return None

def translate_xml_content(file_path, target_language="ko"):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for idx, content_elem in enumerate(root.findall('.//content'), start=1):
        original_text = content_elem.text
        if original_text is not None:
            translated_parts = []
            prev_end = 0
            lstag_placeholders = []

            # 모든 LSTag 태그를 찾아서 임시 플레이스홀더로 교체합니다.
            for lstag in content_elem.findall('.//LSTag'):
                lstag_str = ET.tostring(lstag, encoding='unicode')
                placeholder = f"LSTAG_PLACEHOLDER_{idx}_{len(lstag_placeholders)}"
                lstag_placeholders.append((placeholder, lstag_str))
                original_text = original_text.replace(lstag_str, placeholder, 1)

            # 번역할 텍스트를 조각내고 번역합니다.
            for placeholder, lstag_str in lstag_placeholders:
                start = original_text.find(placeholder, prev_end)
                translated_parts.append(google_translate(original_text[prev_end:start], target_language))
                translated_parts.append(lstag_str)  # 원본 LSTag 태그를 유지합니다.
                prev_end = start + len(placeholder)

            translated_parts.append(google_translate(original_text[prev_end:], target_language))
            translated_text = ''.join(translated_parts)

            # 번역된 텍스트에서 placeholder를 원본 LSTag 태그로 교체합니다.
            for placeholder, lstag_str in lstag_placeholders:
                translated_text = translated_text.replace(placeholder, lstag_str, 1)

            # 결과 출력
            print(f"Translating '{file_path}' - Line {idx}")
            print(f"Original: {original_text}")
            print(f"Translated: {translated_text}")
            print("-" * 50)
            
            content_elem.text = translated_text

    tree.write(file_path, encoding='utf-8', xml_declaration=True)


def main():
    for file_name in os.listdir():
        if file_name.endswith('.xml'):
            backup_original_file(file_name)  # 백업 생성
            translate_xml_content(file_name)
    
    input("Translation completed! Press any key to exit...")

if __name__ == '__main__':
    main()
