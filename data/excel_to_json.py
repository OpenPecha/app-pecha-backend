import pandas as pd
import json
from collections import defaultdict

EXCEL_FILE_NAME = 'Segment_Mapping.xlsx'
OUTPUT_FILE = "output.json"


def excel_to_mapping_json(excel_path, sheet_number: int):
    excel_file = pd.ExcelFile(excel_path)
    sheet_name = excel_file.sheet_names[sheet_number]

    df = pd.read_excel(excel_path, sheet_name=sheet_number)

    df = df.fillna("")
    result = {"text_mappings": []}
    grouped = defaultdict(lambda: defaultdict(list))

    for _, row in df.iterrows():
        text_id = row["commentary_text_id"]
        segment_id = row["commentary_segment_id"]
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
    excel_to_mapping_json(EXCEL_FILE_NAME, 0)
    excel_to_mapping_json(EXCEL_FILE_NAME, 1)
    excel_to_mapping_json(EXCEL_FILE_NAME, 2)
    excel_to_mapping_json(EXCEL_FILE_NAME, 3)
    excel_to_mapping_json(EXCEL_FILE_NAME, 4)
    excel_to_mapping_json(EXCEL_FILE_NAME, 5)
    excel_to_mapping_json(EXCEL_FILE_NAME, 6)
