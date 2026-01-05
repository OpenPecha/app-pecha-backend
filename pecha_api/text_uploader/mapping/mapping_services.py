from pecha_api.text_uploader.mapping.mapping_repository import trigger_mapping_repo
class MappingService:
    def __init__(self):
        self.all_text = {}

    async def trigger_mapping(self, text_ids: dict[str, str]):
        text_ids_list = list(text_ids.values())
        await trigger_mapping_repo(text_ids_list)