

class MappingService:
    def __init__(self):
        self.all_text = {}

    async def trigger_mapping(self, text_ids: dict[str, str]):
        for pecha_text_id in text_ids.values():
            print("pecha_text_id: >>>>>>>>>>>>>>>>>", pecha_text_id)
        pass