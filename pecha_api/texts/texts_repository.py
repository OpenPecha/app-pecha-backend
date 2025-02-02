import uuid

from .texts_models import Text


def get_texts_by_id():
    root_text = Text(
        id=uuid.uuid4(),
        titles={"en": "Root Text title", "bo": "Root གྲྭ་ཚན"},
        summaries={"en": "Root Summaries", "bo": "Root སྙིང་བསྡུས་"},
    )
    versions = [
        Text(
            id=uuid.uuid4(),
            titles={"en": f"Version Topic {i}", "bo": f"Version གྲྭ་ཚན {i}"},
            summaries={"en": f"Version Summaries {i}", "bo": f"Version སྙིང་བསྡུས་ {i}"}
        )
        for i in range(1, 6)
    ]
    return root_text, versions