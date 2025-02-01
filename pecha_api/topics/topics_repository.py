from topics.topics_models import Topic


def get_topics(search: str) -> list[Topic]:
    return [
        Topic(titles={"en": f"Topic {i}", "bo": f"གྲྭ་ཚན {i}"})
        for i in range(1, 6)
    ]

def get_term_by_id(topic_id: str):
    return Topic(titles={"en": "Topic 1", "bo": "གྲྭ་ཚན 1"})