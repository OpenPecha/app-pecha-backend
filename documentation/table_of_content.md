# Table of Content Documentation


## Overview
This collection is designed to store and manage the table of content of text.
This document defines a hierarchical structure for organizing textual content with chapters, sections, and segments.


### Table of Content Object

- **_id**: Unique identifier for the TOC.
- **text_id**: Unique identifier to the associated text
- **chapters**: List of chapters for the text


#### Section Object
- **_id**: Unique identifier for the chapter.
- **title**: Section / Chapter Title
- **section_number**: section number to order in the text
- **parent_id**: Segment parent id , null for the first item
- **segments**: Array of segment Object (Optional)
- **sections**: Array of nested section objects (optional)
- **created_date**: ISO 8601 timestamp
- **updated_date**: ISO 8601 timestamp
- **published_date**: ISO 8601 timestamp

## Segment Object
- **segment_id**: UUID for the segment
- **segment_number**: Integer indicating segment order

### Example document:

#### Section 
```json
{
    "id": "d19338e4-da52-4ea2-800e-3414eac8167e",
    "title": "A brief presentation of the ground path and result",
    "section_number": 1,
    "parent_id": null,
    "segments": [
        {
            "segment_id": "31fe9ea0-f032-46e7-86c9-f07ae70b5b35",
            "segment_number": 1
        },
        {
            "segment_id": "41e438b8-2286-458b-a1b2-860553ce0f54",
            "segment_number": 2
        }
    ],
    "sections": [
        {
            "id": "39965c2a-e89e-4834-83bb-e3a294a8f705",
            "title": "",
            "section_number": 1,
            "parent_id": "d19338e4-da52-4ea2-800e-3414eac8167e",
            "segments": [
                {
                    "segment_id": "8bac2031-e8c6-4c5b-981f-ed17dbc755fb",
                    "segment_number": 1
                },
                {
                    "segment_id": "b3dc7cec-0e18-4238-8184-9b59bc6b114d",
                    "segment_number": 2
                }
            ],
            "sections": [],
            "created_date": "2021-09-01T00:00:00.000Z",
            "updated_date": "2021-09-01T00:00:00.000Z",
            "published_date": "2021-09-01T00:00:00.000Z"
        }
    ],
    "created_date": "2021-09-01T00:00:00.000Z",
    "updated_date": "2021-09-01T00:00:00.000Z",
    "published_date": "2021-09-01T00:00:00.000Z"
}
```

#### table of content(TOC)

```json
[
    {
        "id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
        "text_id": "9b603059-d8b4-42b2-9211-60d058c33480",
        "segments": [
            {
                "id": "d19338e4-da52-4ea2-800e-3414eac8167e",
                "title": "A brief presentation of the ground path and result",
                "section_number": 1,
                "segments": [],
                "sections": [
                    {
                        "id": "39965c2a-e89e-4834-83bb-e3a294a8f705",
                        "title": "",
                        "section_number": 1,
                        "parent_id": "d19338e4-da52-4ea2-800e-3414eac8167e",
                        "created_date": "2021-09-01T00:00:00.000Z",
                        "updated_date": "2021-09-01T00:00:00.000Z",
                        "published_date": "2021-09-01T00:00:00.000Z",
                        "segments": [
                            {
                                "segment_id": "8bac2031-e8c6-4c5b-981f-ed17dbc755fb",
                                "segment_number": 1
                            },
                            {
                                "segment_id": "b3dc7cec-0e18-4238-8184-9b59bc6b114d",
                                "segment_number": 2
                            },
                            {
                                "segment_id": "606135bf-1f71-41fd-8c12-1cc037a768d5",
                                "segment_number": 3
                            },
                            {
                                "segment_id": "980ab7e0-aefc-4120-8817-ff0873ed429c",
                                "segment_number": 4
                            },
                            {
                                "segment_id": "b0e4578c-e604-44a9-a302-fe9fb5b08626",
                                "segment_number": 5
                            },
                            {
                                "segment_id": "af8d904f-26b7-4725-9d00-ede7939a6baf",
                                "segment_number": 6
                            },
                            {
                                "segment_id": "84a9d639-0a17-4525-ac4e-12527cc925c8",
                                "segment_number": 7
                            }
                        ],
                        "sections": []
                    }
                ],
                "created_date": "2021-09-01T00:00:00.000Z",
                "updated_date": "2021-09-01T00:00:00.000Z",
                "published_date": "2021-09-01T00:00:00.000Z"
            },
            {
                "id": "b48dad38-da6d-45c3-ad12-97bca590769c",
                "title": "The detailed explanation of the divisions of reality",
                "section_number": 2,
                "parent_id": null,
                "segments": [],
                "sections": [
                    {
                        "id": "0971f07a-8491-4cfe-9720-dac1acb9824d",
                        "title": "Basis",
                        "segments": [],
                        "sections": [
                            {
                                "id": "0971f07a-8491-4cfe-9720-dac1acb9824d",
                                "title": "The extensive explanation of the abiding nature of the ground",
                                "segments": [
                                    {
                                        "segment_id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e0",
                                        "segment_number": 1
                                    },
                                    {
                                        "segment_id": "d2fabe6c-a112-4e09-a265-5d43078467b1",
                                        "segment_number": 2
                                    },
                                    {
                                        "segment_id": "b66daafd-8451-4cd2-9743-ceabb62661a1",
                                        "segment_number": 3
                                    },
                                    {
                                        "segment_id": "ec911cd3-afd0-4052-8928-0984f8f37acd",
                                        "segment_number": 4
                                    },
                                    {
                                        "segment_id": "007f2197-5a37-4696-b34e-f67eca870830",
                                        "segment_number": 5
                                    }
                                ],
                                "sections": [],
                                "created_date": "2021-09-01T00:00:00.000Z",
                                "updated_date": "2021-09-01T00:00:00.000Z",
                                "published_date": "2021-09-01T00:00:00.000Z"
                            }
                        ],
                        "created_date": "2021-09-01T00:00:00.000Z",
                        "updated_date": "2021-09-01T00:00:00.000Z",
                        "published_date": "2021-09-01T00:00:00.000Z"
                    }
                ],
                "created_date": "2021-09-01T00:00:00.000Z",
                "updated_date": "2021-09-01T00:00:00.000Z",
                "published_date": "2021-09-01T00:00:00.000Z"
            }
        ]
    },
    {
        "id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
        "text_id": "9b603059-d8b4-42b2-9211-60d058c33480",
        "segments": [
            {
                "id": "d19338e4-da52-4ea2-800e-3414eac8167e",
                "title": "A brief presentation of the ground path and result",
                "section_number": 1,
                "parent_id": null,
                "created_date": "2021-09-01T00:00:00.000Z",
                "updated_date": "2021-09-01T00:00:00.000Z",
                "published_date": "2021-09-01T00:00:00.000Z",
                "sections": [
                    {
                        "id": "39965c2a-e89e-4834-83bb-e3a294a8f705",
                        "title": "",
                        "section_number": 1,
                        "parent_id": "d19338e4-da52-4ea2-800e-3414eac8167e",
                        "segments": [
                            {
                                "segment_id": "8bac2031-e8c6-4c5b-981f-ed17dbc755fb",
                                "segment_number": 1
                            },
                            {
                                "segment_id": "b3dc7cec-0e18-4238-8184-9b59bc6b114d",
                                "segment_number": 2
                            },
                            {
                                "segment_id": "606135bf-1f71-41fd-8c12-1cc037a768d5",
                                "segment_number": 3
                            },
                            {
                                "segment_id": "980ab7e0-aefc-4120-8817-ff0873ed429c",
                                "segment_number": 4
                            },
                            {
                                "segment_id": "b0e4578c-e604-44a9-a302-fe9fb5b08626",
                                "segment_number": 5
                            },
                            {
                                "segment_id": "af8d904f-26b7-4725-9d00-ede7939a6baf",
                                "segment_number": 6
                            },
                            {
                                "segment_id": "84a9d639-0a17-4525-ac4e-12527cc925c8",
                                "segment_number": 7
                            },
                            {
                                "segment_id": "606135bf-1f71-41fd-8c12-1cc037a768d5",
                                "segment_number": 3
                            },
                            {
                                "segment_id": "980ab7e0-aefc-4120-8817-ff0873ed429c",
                                "segment_number": 4
                            },
                            {
                                "segment_id": "b0e4578c-e604-44a9-a302-fe9fb5b08626",
                                "segment_number": 5
                            },
                            {
                                "segment_id": "af8d904f-26b7-4725-9d00-ede7939a6baf",
                                "segment_number": 6
                            },
                            {
                                "segment_id": "84a9d639-0a17-4525-ac4e-12527cc925c8",
                                "segment_number": 7
                            }
                        ],
                        "sections": [], 
                        "created_date": "2021-09-01T00:00:00.000Z",
                        "updated_date": "2021-09-01T00:00:00.000Z",
                        "published_date": "2021-09-01T00:00:00.000Z"
                    }
                ]
            }
        ]
    }
]
```
## Note:
1. Current structure supports multiple table of content for same text