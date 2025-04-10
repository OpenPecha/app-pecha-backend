from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException
from starlette import status

from pecha_api.error_contants import ErrorConstants
from .texts_repository import check_text_exists, check_all_text_exists
from .texts_response_models import (
    DetailTableOfContent, 
    TableOfContent, 
    TextSegment, 
    DetailSection, 
    DetailTextSegment
)


class TextUtils:
    """
    Utility class for text-related operations.
    Contains helper methods for text processing, validation, and transformations.
    """
    
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
    async def convert_to_detail_table_of_content(table_of_content: TableOfContent) -> DetailTableOfContent:
        """
        Convert a TableOfContent model to a DetailTableOfContent model by enriching
        each segment with detailed information fetched from get_segment_details_by_id.
        
        Args:
            table_of_content: The TableOfContent model to be converted
            
        Returns:
            A DetailTableOfContent model with enriched segment details
        """
        from .segments.segments_service import get_segment_details_by_id
        
        # Create a new DetailTableOfContent with the same base attributes
        detail_table_of_content = DetailTableOfContent(
            id=str(table_of_content.id) if table_of_content.id else None,
            text_id=table_of_content.text_id,
            sections=[]
        )
        
        # Process sections recursively
        async def process_section(section) -> 'DetailSection':
            detail_section = DetailSection(
                id=section.id,
                title=section.title,
                section_number=section.section_number,
                parent_id=section.parent_id,
                segments=[],
                sections=[],
                created_date=section.created_date,
                updated_date=section.updated_date,
                published_date=section.published_date
            )
            
            # Process segments
            for segment in section.segments:
                # Fetch detailed segment information
                segment_details = await get_segment_details_by_id(segment.segment_id)
                
                # Create DetailTextSegment with enriched information
                detail_segment = DetailTextSegment(
                    segment_id=segment.segment_id,
                    segment_number=segment.segment_number,
                    content=segment_details.content,
                    # Translation can be added here if available
                )
                
                detail_section.segments.append(detail_segment)
            
            # Process nested sections recursively
            if section.sections:
                for subsection in section.sections:
                    detail_subsection = await process_section(subsection)
                    detail_section.sections.append(detail_subsection)
            
            return detail_section
        
        # Process all top-level sections
        for section in table_of_content.sections:
            detail_section = await process_section(section)
            detail_table_of_content.sections.append(detail_section)
        
        return detail_table_of_content
