import xml.etree.ElementTree as ET
import os
import time
import shutil
from googletrans import Translator

def backup_original_file(file_path):
    # 원본 파일을 백업합니다. 예를 들어, 'original.xml' 파일을 'original.xml.bak'으로 복사합니다.
    backup_path = file_path + ".bak"
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

def restore_lstag(original_text, translated_text):
    """LSTag 태그의 원본 내용을 복원합니다."""
    # LSTag를 찾기 위한 임시 태그를 생성합니다.
    placeholder = "LSTAG_PLACEHOLDER"
    lstag_pairs = []
    
    # 원본에서 LSTag 위치와 내용을 추출합니다.
    while "<LSTag" in original_text:
        start = original_text.find("<LSTag")
        end = original_text.find(">", start) + 1
        lstag_content = original_text[start:end]
        lstag_pairs.append((placeholder, lstag_content))
        original_text = original_text.replace(lstag_content, placeholder, 1)
    
    # 번역된 텍스트에서 placeholder를 원본 LSTag 내용으로 교체합니다.
    for placeholder, lstag_content in lstag_pairs:
        translated_text = translated_text.replace(placeholder, lstag_content, 1)
    
    return translated_text

def translate_xml_content(file_path, target_language="ko"):
    tree = ET.parse(file_path)
    root = tree.getroot()

    for idx, content_elem in enumerate(root.findall('content'), start=1):
        original_text = content_elem.text
        if original_text is not None:
            # LSTag 부분을 보존하며 번역합니다.
            translated_parts = []
            prev_end = 0
            for lstag in content_elem.findall('LSTag'):
                start = original_text.find(ET.tostring(lstag, encoding='utf-8').decode('utf-8'))
                end = start + len(ET.tostring(lstag, encoding='utf-8').decode('utf-8'))
                
                translated_parts.append(google_translate(original_text[prev_end:start], target_language))
                translated_parts.append(original_text[start:end])
                
                prev_end = end

            translated_parts.append(google_translate(original_text[prev_end:], target_language))
            translated_text = ''.join(translated_parts)

            # LSTag 내용을 복원합니다.
            translated_text = restore_lstag(original_text, translated_text)
            
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