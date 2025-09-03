def error_payload(status_code: int, message: str) -> dict[str, str]:
        error_map = {
            400: "bad_request",
            401: "unauthorized",
            403: "forbidden",
            404: "not_found",
            409: "conflict",
            422: "unprocessable_entity",
            500: "internal_server_error",
        }
        return {"error": error_map.get(status_code, "internal_server_error"), "message": message}
