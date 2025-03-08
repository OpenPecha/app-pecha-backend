# Segment Documentation

## Overview
This collection is designed to store and manage the segment along with their mapping with another text.
Each segment of the text is stored as a separate document, allowing efficient querying, retrieval, and pagination.

## Data Structure
Each document follows a hierarchical structure with unique identifiers and parent-child relationships. The key fields in the dataset include:

### Segment Object

- **_id**: Unique identifier for the subsection.
- **text_id**: Identifier for the complete text this segment belongs to.
- **content**: The actual text content, which may include HTML tags or styling.
- **mappings**: A list of mappings that link this segment to related texts or translations.

### Mappings Object
Each mapping object links a segment to another text and contains:

- **text_id** (string): Identifier of the related text (e.g., translation or commentary).
- **segments** (array of string): List of segment IDs from the related text that correspond to the current segment.


### Example document:

**One to Many**
```json
{
            "id": "e47b3b6a-6c4a-4c9f-80d9-8aa632c42b44",
            "text_id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
            "content": "<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
            "mappings": [
                {
                    "text_id": "93b0cd89-62c6-445d-b8e1-2789ec8d0f1d",
                    "segments": [
                        "e47b3b6a-6c4a-4c9f-80d9-8aa632c42b44",
                        "01362397-7599-4276-a23e-a64943870602"
                    ] 
                }
            ]
}
```
**Many to one**
```json
[
  {
            "id": "e47b3b6a-6c4a-4c9f-80d9-8aa632c42b44",
            "text_id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
            "content": "<span class=\"text-quotation-style\">དང་པོ་ནི་</span><span class=\"text-citation-style\">ཧོ་སྣང་སྲིད་</span>སོགས་ཚིག་རྐང་དྲུག་གིས་བསྟན།<span class=\"text-citation-style\">ཧོ༵་</span>ཞེས་པ་འཁྲུལ་བས་དབང་མེད་དུ་བྱས་ཏེ་མི་འདོད་པའི་ཉེས་རྒུད་དྲག་པོས་རབ་ཏུ་གཟིར་བའི་འཁོར་བའི་སེམས་ཅན་རྣམས་ལ་དམིགས་མེད་བརྩེ་བའི་རྣམ་པར་ཤར་ཏེ་འཁྲུལ་སྣང་རང་སར་དག་པའི་ཉེ་ལམ་ཟབ་མོ་འདིར་བསྐུལ་བའི་ཚིག་ཏུ་བྱས་པ་སྟེ།",
            "mappings": [
                {
                    "text_id": "93b0cd89-62c6-445d-b8e1-2789ec8d0f1d",
                    "segments": [
                        "e47b3b6a-6c4a-4c9f-80d9-8aa632c42b44",
                        "01362397-7599-4276-a23e-a64943870602"
                    ] 
                }
            ]
  },
  {
            "id": "01362397-7599-4276-a23e-a64943870602",
            "text_id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
            "content": "འདི་ལྟར་བློའི་ཡུལ་དུ་བྱ་རུང་བའི་ཆོས་རང་ངོས་ནས་བདེན་པར་མ་གྲུབ་པས་<span class=\"text-citation-style\">སྣང༵་</span>བ་ཙམ་དུ་ཟད་ཅིང་།གང་སྣང་ཐ་སྙད་ཙམ་དུ་བསླུ་བ་མེད་པར་གནས་པས་སྣང་ཙམ་དུ་<span class=\"text-citation-style\">སྲི༵ད་</span>ཅིང་ཡོད་པའི་མ་དག་ཀུན་ཉོན་འཁྲུལ་བའི་<span class=\"text-citation-style\">འཁོ༵ར་</span>བའི་སྣོད་བཅུད་རྒྱུ་འབྲས་ཀྱི་སྒྱུ་འཕྲུལ་སྣ་ཚོགས་ཀྱི་བཀོད་པ་འདི་དང་།དག་པ་རྣམ་བྱང་མྱང་<span class=\"text-citation-style\">འད༵ས་</span>ཀྱི་གྲོལ་བ་ཐར་པའི་ཡེ་ཤེས་ཡོན་ཏན་ཕྲིན་ལས་ཀྱི་རོལ་གར་བསམ་ལས་འདས་པའི་འཁྲུལ་གྲོལ་གྱི་ཆོས་འདི་<span class=\"text-citation-style\">ཐམ༵ས་</span><span class=\"text-citation-style\">ཅ༵ད་</span><span class=\"text-citation-style\">ཀུན༵</span>།",
            "mappings": [
                {
                    "text_id": "93b0cd89-62c6-445d-b8e1-2789ec8d0f1d",
                    "segments": [
                        "e47b3b6a-6c4a-4c9f-80d9-8aa632c42b44"
                    ] 
                }
            ]
  }
]
```

## Note:
1. The segment collection is totally independent of the text structure which is build using collection(table_of_content).
2. The mapping structure helps us to have many-to-many relationship between segments.
   1. As shown above, one segment can be mapped to many segment from the source text.
   2. Also, Many segments can be mapped to single segment from the source text.