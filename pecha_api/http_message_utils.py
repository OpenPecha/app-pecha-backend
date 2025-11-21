def handle_http_status_error(e: httpx.HTTPStatusError) -> None:
    logger.error(f"External API error: {e.response.status_code} - {e.response.text}")
    raise HTTPException(
        status_code=e.response.status_code,
        detail=f"External search API error: {e.response.text}"
    )


def handle_request_error(e: httpx.RequestError) -> None:
    logger.error(f"Request to external API failed: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail="Failed to connect to the search service. Please try again later."
    )    