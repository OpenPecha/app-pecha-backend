## Category Data Structure


The following is the structure of the category data in MongoDB:

```json
{
    "_id" : "",
    "parent_id": "",
    "path" : {
        "en": "Madyamika/Madyamika sub" // it will be a comma-separated string
    },
    "title": {
        "en": "This is the English description.",
        "bo": "འདི་ནི་བོད་ཡིག་གི་བརྗོད་དོན་རེད།",
        "es": "Esta es la descripción en español.",
        "fr": "Ceci est la description en français.",
        "de": "Dies ist die deutsche Beschreibung."
    },
    "descriptions": {
        "en": "This is the English description.",
        "bo": "འདི་ནི་བོད་ཡིག་གི་བརྗོད་དོན་རེད།",
        "es": "Esta es la descripción en español.",
        "fr": "Ceci est la description en français.",
        "de": "Dies ist die deutsche Beschreibung."
    },
    "shortDescriptions": {
        "en": "Short description in English.",
        "bo": "འདི་ནི་བོད་ཡིག་གི་བརྗོད་དོན་རེད།",
        "es": "Descripción corta en español.",
        "fr": "Description courte en français.",
        "de": "Kurze Beschreibung auf Deutsch."
    }
}
```

### Fields

- **_id**: Unique identifier for the category.
- **parent_id**: Identifier of the parent category.
- **path**: Object containing the hierarchical path of the category in different languages, represented as a comma-separated string.
- **title**: Object containing the title of the category in different languages.
- **descriptions**: Object containing the detailed descriptions of the category in different languages.
- **shortDescriptions**: Object containing the short descriptions of the category in different languages.

## Terms Data structure

```json
{
    "_id" : "",
    "titles" : {
            "en": "",
            "bo": "",
            "zh": ""
    }
}
```

### Fields

- **_id**: Unique identifier for the category.
- **title**: Object containing the title of the category in different languages.