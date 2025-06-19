# Elasticsearch Exact Match Queries

This document explains how to implement exact term matching in Elasticsearch for the Pecha backend application.

## Query Types Overview

### 1. **Term Query** - Exact Term Matching
**Use Case**: Find documents containing the exact term (case-sensitive)
```python
# API Call
GET /search?query=dharma&query_type=term

# Generated Query
{
  "query": {
    "term": {
      "content": {
        "value": "dharma"
      }
    }
  }
}
```

**When to use**: 
- Looking for specific terms like "dharma", "buddha", "meditation"
- Case-sensitive exact matches
- Single word searches

### 2. **Match Phrase** - Exact Phrase Matching
**Use Case**: Find documents containing the exact phrase in order
```python
# API Call
GET /search?query=way of the bodhisattva&query_type=phrase

# Generated Query
{
  "query": {
    "match_phrase": {
      "content": {
        "query": "way of the bodhisattva"
      }
    }
  }
}
```

**When to use**:
- Multi-word phrases that must appear in exact order
- Book titles, specific teachings, or quotes
- Preserves word order and proximity

### 3. **Wildcard Query** - Pattern Matching
**Use Case**: Find documents matching a pattern
```python
# API Call
GET /search?query=meditation&query_type=wildcard

# Generated Query
{
  "query": {
    "wildcard": {
      "content": {
        "value": "*meditation*"
      }
    }
  }
}
```

**When to use**:
- Partial word matches
- Finding variations of terms
- Case-insensitive pattern matching

### 4. **Bool Query** - Complex Exact Matching
**Use Case**: Combine multiple exact match conditions
```python
# API Call
GET /search?query=compassion&query_type=bool

# Generated Query
{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "content": {
              "value": "compassion"
            }
          }
        }
      ]
    }
  }
}
```

**When to use**:
- Complex search logic
- Combining exact matches with other conditions
- Advanced filtering scenarios

## Advanced Exact Matching Functions

### Multi-Field Exact Search
```python
from pecha_api.search.search_service import generate_multi_field_exact_query

# Search in multiple fields with exact matching
query = generate_multi_field_exact_query(
    query="bodhisattva",
    fields=["content", "title", "summary"],
    operator="or"
)
```

### Fuzzy Exact Matching
```python
from pecha_api.search.search_service import generate_fuzzy_exact_query

# Approximate exact matching with typo tolerance
query = generate_fuzzy_exact_query(
    query="bodhisattva",
    fuzziness="AUTO",  # "0", "1", "2", or "AUTO"
    max_expansions=50
)
```

### Combined Exact and Fuzzy Search
```python
from pecha_api.search.search_service import generate_combined_exact_query

# Boost exact matches over fuzzy matches
query = generate_combined_exact_query(
    exact_terms=["dharma", "buddha"],
    fuzzy_terms=["meditation", "compassion"],
    boost_exact=2.0
)
```

## API Usage Examples

### Basic Exact Term Search
```bash
curl -X GET "http://localhost:8000/search?query=dharma&query_type=term&search_type=SOURCE&limit=10"
```

### Exact Phrase Search
```bash
curl -X GET "http://localhost:8000/search?query=way of the bodhisattva&query_type=phrase&search_type=SOURCE&limit=10"
```

### Pattern Matching Search
```bash
curl -X GET "http://localhost:8000/search?query=meditation&query_type=wildcard&search_type=SOURCE&limit=10"
```

### Search Within Specific Text
```bash
curl -X GET "http://localhost:8000/search?query=compassion&query_type=term&search_type=SOURCE&text_id=123&limit=10"
```

## Performance Considerations

### 1. **Term Queries**
- **Pros**: Fast, exact matches
- **Cons**: Case-sensitive, no stemming
- **Best for**: Known exact terms, IDs, codes

### 2. **Match Phrase**
- **Pros**: Preserves word order, good for phrases
- **Cons**: Slower than term queries
- **Best for**: Book titles, quotes, specific phrases

### 3. **Wildcard Queries**
- **Pros**: Flexible pattern matching
- **Cons**: Can be slow with leading wildcards
- **Best for**: Partial matches, variations

### 4. **Bool Queries**
- **Pros**: Most flexible, can combine multiple conditions
- **Cons**: More complex, potentially slower
- **Best for**: Advanced search scenarios

## Index Mapping Considerations

For optimal exact matching performance, consider these field mappings:

```json
{
  "mappings": {
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": {
            "type": "keyword"
          },
          "exact": {
            "type": "text",
            "analyzer": "keyword"
          }
        }
      }
    }
  }
}
```

This allows you to use:
- `content` for full-text search
- `content.keyword` for exact term matching
- `content.exact` for case-sensitive exact matching

## Best Practices

1. **Use Term Queries** for known exact values (IDs, codes, specific terms)
2. **Use Match Phrase** for multi-word exact phrases
3. **Use Wildcard** sparingly and avoid leading wildcards when possible
4. **Combine with Filters** for better performance
5. **Consider Fuzzy Matching** for user input with potential typos
6. **Use Bool Queries** for complex search logic

## Error Handling

The search service includes proper error handling for:
- Invalid query types
- Empty queries
- Connection errors
- Malformed Elasticsearch responses

All errors are logged and return appropriate HTTP status codes with descriptive error messages. 