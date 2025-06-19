import pytest
from unittest.mock import patch, AsyncMock, Mock
from pecha_api.search.search_service import (
    _get_query_by_type,
    generate_multi_field_exact_query,
    generate_fuzzy_exact_query,
    generate_combined_exact_query
)
from pecha_api.search.search_enums import QueryType

class TestExactSearchQueries:
    """Test cases for exact search query generation."""
    
    def test_term_query_generation(self):
        """Test term query generation for exact term matching."""
        query = _get_query_by_type("dharma", QueryType.TERM)
        
        expected = {
            "term": {
                "content": {
                    "value": "dharma"
                }
            }
        }
        
        assert query == expected
    
    def test_phrase_query_generation(self):
        """Test phrase query generation for exact phrase matching."""
        query = _get_query_by_type("way of the bodhisattva", QueryType.PHRASE)
        
        expected = {
            "match_phrase": {
                "content": {
                    "query": "way of the bodhisattva"
                }
            }
        }
        
        assert query == expected
    
    def test_wildcard_query_generation(self):
        """Test wildcard query generation for pattern matching."""
        query = _get_query_by_type("meditation", QueryType.WILDCARD)
        
        expected = {
            "wildcard": {
                "content": {
                    "value": "*meditation*"
                }
            }
        }
        
        assert query == expected
    
    def test_bool_query_generation(self):
        """Test bool query generation for complex exact matching."""
        query = _get_query_by_type("compassion", QueryType.BOOL)
        
        expected = {
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
        
        assert query == expected
    
    def test_default_match_query_generation(self):
        """Test default match query generation (original behavior)."""
        query = _get_query_by_type("buddha", QueryType.MATCH)
        
        expected = {
            "match": {
                "content": {
                    "query": "buddha"
                }
            }
        }
        
        assert query == expected
    
    def test_multi_field_exact_query(self):
        """Test multi-field exact query generation."""
        query = generate_multi_field_exact_query(
            query="bodhisattva",
            fields=["content", "title", "summary"],
            operator="or"
        )
        
        expected = {
            "multi_match": {
                "query": "bodhisattva",
                "fields": ["content", "title", "summary"],
                "type": "phrase",
                "operator": "or"
            }
        }
        
        assert query == expected
    
    def test_fuzzy_exact_query(self):
        """Test fuzzy exact query generation."""
        query = generate_fuzzy_exact_query(
            query="bodhisattva",
            fuzziness="AUTO",
            max_expansions=50
        )
        
        expected = {
            "match": {
                "content": {
                    "query": "bodhisattva",
                    "fuzziness": "AUTO",
                    "max_expansions": 50
                }
            }
        }
        
        assert query == expected
    
    def test_combined_exact_query_with_exact_terms_only(self):
        """Test combined query with only exact terms."""
        query = generate_combined_exact_query(
            exact_terms=["dharma", "buddha"],
            boost_exact=2.0
        )
        
        expected = {
            "bool": {
                "should": [
                    {
                        "term": {
                            "content": {
                                "value": "dharma",
                                "boost": 2.0
                            }
                        }
                    },
                    {
                        "term": {
                            "content": {
                                "value": "buddha",
                                "boost": 2.0
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
        
        assert query == expected
    
    def test_combined_exact_query_with_both_terms(self):
        """Test combined query with both exact and fuzzy terms."""
        query = generate_combined_exact_query(
            exact_terms=["dharma"],
            fuzzy_terms=["meditation"],
            boost_exact=1.5
        )
        
        expected = {
            "bool": {
                "should": [
                    {
                        "term": {
                            "content": {
                                "value": "dharma",
                                "boost": 1.5
                            }
                        }
                    },
                    {
                        "match": {
                            "content": {
                                "query": "meditation",
                                "fuzziness": "AUTO"
                            }
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        }
        
        assert query == expected

@pytest.mark.asyncio
class TestExactSearchIntegration:
    """Integration tests for exact search functionality."""
    
    async def test_exact_term_search_integration(self):
        """Test integration of exact term search with mock Elasticsearch response."""
        from pecha_api.search.search_service import get_search_results
        from pecha_api.search.search_enums import SearchType
        
        # Mock Elasticsearch response for exact term search
        mock_response = {
            "hits": {
                "total": {"value": 1, "relation": "eq"},
                "hits": [
                    {
                        "_source": {
                            "id": "test-segment-id",
                            "content": "The dharma teachings are profound.",
                            "text_id": "test-text-id",
                            "text": {
                                "title": "Test Text",
                                "language": "en",
                                "published_date": "2024-01-01"
                            }
                        }
                    }
                ]
            }
        }
        
        mock_client = AsyncMock()
        mock_client.search = AsyncMock(return_value=mock_response)
        
        with patch("pecha_api.search.search_service.search_client", 
                  new_callable=AsyncMock, return_value=mock_client):
            with patch("pecha_api.search.search_service.get", return_value="test-index"):
                
                response = await get_search_results(
                    query="dharma",
                    search_type=SearchType.SOURCE,
                    text_id="test-text-id",
                    query_type=QueryType.TERM,
                    skip=0,
                    limit=10
                )
                
                # Verify the search was called with term query
                mock_client.search.assert_called_once()
                call_args = mock_client.search.call_args[1]
                
                # Check that the query contains a term query
                assert "query" in call_args
                query_body = call_args["query"]
                assert "bool" in query_body["query"]
                assert "must" in query_body["query"]["bool"]
                
                # Verify response structure
                assert response is not None
                assert response.sources is not None
                assert len(response.sources) == 1
                assert response.sources[0].text.text_id == "test-text-id" 