import xml.etree.ElementTree as ET
import os
import time
from googletrans import Translator

def google_translate(text, target_language="ko"):
    """`googletrans` 모듈을 사용하여 텍스트를 번역합니다."""
    translator = Translator()
    max_retries = 5  # 최대 재시도 횟수
    retry_delay = 5  # 재시도 사이의 딜레이 (초)
    
    for attempt in range(max_retries):
        try:
            # 번역 시도
            return translator.translate(text, dest=target_language).text
        except Exception as e:
            print(f"Translation failed with error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)  # 잠시 대기 후 재시도
            else:
                print("Maximum retries reached. Translation failed.")
    return None

def translate_xml_content(file_path, target_language="ko"):
    """XML 파일의 내용을 번역합니다."""
    tree = ET.parse(file_path)
    root = tree.getroot()

    for idx, content_elem in enumerate(root.findall('content'), start=1):
        original_text = content_elem.text
        if original_text is not None:
            # LSTag 부분을 건너뛰고 번역합니다.
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
            
            # 콘솔에 정보를 출력합니다.
            print(f"Translating '{file_path}' - Line {idx}")
            print(f"Original: {original_text}")
            print(f"Translated: {translated_text}")
            print("-" * 50)
            
            content_elem.text = translated_text

    tree.write(file_path + ".translated.xml")

def main():
    # 현재 경로의 모든 XML 파일을 찾습니다.
    for file_name in os.listdir():
        if file_name.endswith('.xml'):
            translate_xml_content(file_name)
    
    input("Translation completed! Press any key to exit...")

if __name__ == '__main__':
    main()
