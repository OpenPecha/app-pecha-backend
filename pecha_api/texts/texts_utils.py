from uuid import UUID
from typing import List, Optional, Dict, Union
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from .texts_repository import check_text_exists, check_all_text_exists, get_texts_by_id,\
    get_texts_by_ids
from .texts_response_models import TextModel
from .texts_response_models import (
    TableOfContent, 
    TextSegment,
    Section
)
from .texts_repository import get_contents_by_id, get_texts_by_id

class TextUtils:
    """
    Utility class for text-related operations.
    Contains helper methods for text processing, validation, and transformations.
    """

    @staticmethod
    async def get_text_details_by_ids(text_ids: List[str]) -> Dict[str, TextModel]:
        texts_detail = await get_texts_by_ids(text_ids=text_ids)
        return texts_detail
    
    async def get_text_details_by_id(text_id: str) -> TextModel:
        text_detail = await get_texts_by_id(text_id=text_id)
        return TextModel(
            id=str(text_detail.id),
            title=text_detail.title,
            language=text_detail.language,
            parent_id=text_detail.parent_id,
            type=text_detail.type,
            is_published=text_detail.is_published,
            created_date=text_detail.created_date,
            updated_date=text_detail.updated_date,
            published_date=text_detail.published_date,
            published_by=text_detail.published_by,
            categories=text_detail.categories
        )
    
    @staticmethod
    async def validate_text_exists(text_id: str):
        """
        Validate if a text exists by its ID.
        
        Args:
            text_id: The ID of the text to validate
            
        Returns:
            bool: True if the text exists
            
        Raises:
            HTTPException: If the text does not exist
        """
        uuid_text_id = UUID(text_id)
        is_exists = await check_text_exists(text_id=uuid_text_id)
        if not is_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE
            )
        return is_exists

    @staticmethod
    async def validate_texts_exist(text_ids: List[str]):
        """
        Validate if multiple texts exist by their IDs.
        
        Args:
            text_ids: List of text IDs to validate
            
        Returns:
            bool: True if all texts exist
            
        Raises:
            HTTPException: If any text does not exist
        """
        uuid_text_ids = [UUID(text_id) for text_id in text_ids]
        all_exists = await check_all_text_exists(text_ids=uuid_text_ids)
        if not all_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE
            )
        return all_exists

    @staticmethod
    def get_all_segment_ids(table_of_content: TableOfContent) -> List[str]:
        """
        Extract all segment IDs from a TableOfContent object.
        
        Args:
            table_of_content: The TableOfContent to extract segment IDs from
            
        Returns:
            List[str]: List of all segment IDs in the table of content
        """
        # Use an iterative approach with a stack
        stack = list(table_of_content.sections)  # Start with top-level sections
        segment_ids = []

        while stack:
            section = stack.pop()

            # Add segment IDs
            segment_ids.extend(
                segment.segment_id
                for segment in section.segments
                if isinstance(segment, TextSegment)
            )

            # Add nested sections to the stack
            if section.sections:
                stack.extend(section.sections)

        return segment_ids
    
    @staticmethod
    async def get_text_detail_by_id(text_id: str) -> TextModel:
        """
        Get text details by ID.
        
        Args:
            text_id: The ID of the text to retrieve
            
        Returns:
            TextModel: The text model with details
            
        Raises:
            HTTPException: If the text does not exist or text_id is None
        """
        if text_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ErrorConstants.TEXT_OR_TERM_NOT_FOUND_MESSAGE)
        text = await get_texts_by_id(text_id=text_id)
        if text is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ErrorConstants.TEXT_NOT_FOUND_MESSAGE)
        return TextModel(
            id=str(text.id),
            title=text.title,
            language=text.language,
            parent_id=text.parent_id,
            type=text.type,
            is_published=text.is_published,
            created_date=text.created_date,
            updated_date=text.updated_date,
            published_date=text.published_date,
            published_by=text.published_by,
            categories=text.categories
        )
        
    @staticmethod
    def remove_segments_from_list_of_table_of_content(table_of_content: List[TableOfContent]) -> List[TableOfContent]:
        """
        Removes all segments from each section in a list of TableOfContent models while maintaining the section structure.
        
        Args:
            table_of_content: A list of TableOfContent models or a single TableOfContent model
            
        Returns:
            List of TableOfContent models with the same structure but no segments,
            or a single TableOfContent model if that was the input
        """
        # Define recursive function for processing sections - defined once, used for all cases
        def process_section_without_segments(section):
            # Create a new section with the same metadata but empty segments list
            new_section = Section(
                id=str(section.id),
                title=section.title,
                section_number=section.section_number,
                parent_id=section.parent_id,
                segments=[],  # Empty segments list
                sections=[],
                created_date=section.created_date,
                updated_date=section.updated_date,
                published_date=section.published_date
            )
            
            # Process nested sections recursively
            if section.sections:
                for subsection in section.sections:
                    clean_subsection = process_section_without_segments(subsection)
                    new_section.sections.append(clean_subsection)
            
            return new_section
            
        # Helper function to process a single TableOfContent
        def process_table_of_content(content):
            clean_content = TableOfContent(
                id=str(content.id) if content.id else None,
                text_id=content.text_id,
                sections=[]
            )
            
            # Process all top-level sections
            for section in content.sections:
                clean_section = process_section_without_segments(section)
                clean_content.sections.append(clean_section)
                
            return clean_content
        
        # Process a list of TableOfContent objects
        if isinstance(table_of_content, list):
            result = []
            for content in table_of_content:
                result.append(process_table_of_content(content))
            return result
        
        # Process individual TableOfContent object
        return process_table_of_content(table_of_content)

    @staticmethod
    async def get_table_of_content_id_and_respective_section_by_segment_id(text_id: str, segment_id: str) -> TableOfContent:
        """
        Searches for a segment_id within all sections of table of contents for the given text_id.
        Returns a TableOfContent object with only the section containing the segment_id.
        
        Args:
            text_id: The ID of the text to search in
            segment_id: The ID of the segment to search for
            
        Returns:
            TableOfContent: A TableOfContent object with only the section containing the segment_id,
                           or None if the segment is not found
        """
        table_of_contents = await get_contents_by_id(text_id=text_id)
        # Recursive function to search for segment_id in sections
        def find_section_with_segment(sections):
            for section in sections:
                # Check if segment_id exists in this section's segments
                for segment in getattr(section, "segments", []):
                    if getattr(segment, "segment_id", None) == segment_id:
                        return section
                        
                # Check subsections recursively
                if getattr(section, "sections", None):
                    found_section = find_section_with_segment(section.sections)
                    if found_section:
                        # we need to return the found section and not the whole main section
                        return found_section
            return None
        
        # Search through all table of contents
        for content in table_of_contents:
            found_section = find_section_with_segment(getattr(content, "sections", []))
            if found_section:
                # Create a new TableOfContent with only the found section
                filtered_content = TableOfContent(
                    id=str(content.id),
                    text_id=content.text_id,
                    sections=[found_section]  # Only include the section with the segment_id
                )
                return filtered_content
                
        return None  # Return None if segment not found in any section
