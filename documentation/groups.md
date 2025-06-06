# Group Documentation

## Overview
This collection is designed to store and manage the group of texts base on either versions or commentaries. Since in the new pecha inhouse we don't have the concept of root text being fixed.
Since we don't have fixed root text it's not possible to list down the versions of the root text.
Hence we are introducing group collection which the root text will be choosen base on the current language selected. Hence there is not type as root text and all texts are versions.

## NOTE
Before creating or uploading any texts. Group must be created first. Then assign the group_id to the texts group_id field.

### Group Object

- **_id**: Unique identifier for the group.
- **type**: Type of the group (e.g., version, commentary).

### Example document:

**Text Version Group**
```json
{
    "_id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
    "type": "version"
}
```

**Text Commentary Group**
```json
{
    "_id": "5894c3b8-4c52-4964-b0d1-9498a71fd1e1",
    "type": "commentary"
}
```


