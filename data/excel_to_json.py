import pandas as pd
import json
from collections import defaultdict

EXCEL_FILE_NAME = 'Segment_Mapping.xlsx'
OUTPUT_FILE = "output.json"


def excel_to_mapping_json(excel_path, sheet_number: int, text_column_name: str, segment_column_name: str):
    excel_file = pd.ExcelFile(excel_path)
    sheet_name = excel_file.sheet_names[sheet_number]

    df = pd.read_excel(excel_path, sheet_name=sheet_number)

    result = {"text_mappings": []}
    grouped = defaultdict(lambda: defaultdict(list))

    for _, row in df.iterrows():
        if pd.isna(row[text_column_name]) or pd.isna(row[segment_column_name]) or pd.isna(
                row["parent_text_id"]) or pd.isna(
                row["parent_segment_id"]):
            continue
        text_id = row[text_column_name]
        segment_id = row[segment_column_name]
        parent_text_id = row["parent_text_id"]
        segment = row["parent_segment_id"]

        grouped[(text_id, segment_id)][parent_text_id].append(segment)

    for (text_id, segment_id), parent_map in grouped.items():
        mappings = []
        for parent_text_id, segments in parent_map.items():
            mappings.append({
                "parent_text_id": parent_text_id,
                "segments": segments
            })
        result["text_mappings"].append({
            "text_id": text_id,
            "segment_id": segment_id,
            "mappings": mappings
        })
    output_file = f"{sheet_name}.json"
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(result, file, indent=4, ensure_ascii=False)

    print(f"✅ JSON saved to: {output_file}")


if __name__ == "__main__":
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=0,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=1,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=2,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=3,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=4,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=5,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=6,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=7,text_column_name='commentary_text_id',segment_column_name='commentary_segment_id')
    excel_to_mapping_json(excel_path=EXCEL_FILE_NAME, sheet_number=9,text_column_name='version_text_id',segment_column_name='version_segment_id')
