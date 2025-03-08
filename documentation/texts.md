# Text Documentation

## Overview
This collection is designed to store metadata of the text.

### Text Object

- **id**: Unique identifier in UUID v4 format
- **title**: Full title of the Buddhist text
- **type**: Document classification (root_text,commentary,translation)
- **categories**: Array for taxonomical classification (currently empty)
- **language**: ISO 639-1 language code ('bo' = Tibetan)
- **is_published**: Boolean flag indicating if text is publicly available
- **published_by**: Organization responsible for publishing
- **created_date**: Initial creation timestamp
- **updated_date**: Last modification timestamp
- **published_date**: When the text was made public

// root text


### Example document:

```json
{
    "id": "uuid.v4",
    "title": "The short path of Samantabhadra the lamp that illuminates with light",
    "language": "en",
    "is_published": true,
    "created_date": "2021-09-01T00:00:00.000Z",
    "updated_date": "2021-09-01T00:00:00.000Z",
    "published_date": "2021-09-01T00:00:00.000Z",
    "published_by": "buddhist_tab",
    "type": "commentary",
    "categories": []
}

```