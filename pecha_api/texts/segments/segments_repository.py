from __future__ import annotations

from uuid import UUID, uuid4

from pecha_api.constants import Constants
from .segments_models import Segment
from .segments_response_models import CreateSegmentRequest, SegmentResponse, SegmentTranslation, SegmentCommentry
import logging
from beanie.exceptions import CollectionWasNotInitialized
from typing import List, Dict


async def get_segment_by_id(segment_id: str) -> Segment | None:
    try:
        segment = await Segment.get_segment_by_id(segment_id=segment_id)
        return segment
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return None

async def check_segment_exists(segment_id: UUID) -> bool:
    try:
        is_segment_exists = await Segment.check_exists(segment_id=segment_id)
        return is_segment_exists
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False


async def check_all_segment_exists(segment_ids: List[UUID]) -> bool:
    try:
        is_segment_exists = await Segment.exists_all(segment_ids=segment_ids, batch_size=Constants.QUERY_BATCH_SIZE)
        return is_segment_exists
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return False


async def get_segments_by_ids(segment_ids: List[str]) -> Dict[str, SegmentResponse]:
    try:
        if not segment_ids:
            return {}
        list_of_segments_detail = await Segment.get_segments(segment_ids=segment_ids)
        return {str(segment.id): SegmentResponse(
            id=str(segment.id),
            text_id=segment.text_id,
            content=segment.content,
            mapping=segment.mapping
        ) for segment in list_of_segments_detail}
    except CollectionWasNotInitialized as e:
        logging.debug(e)
        return {}


async def create_segment(create_segment_request: CreateSegmentRequest) -> List[Segment]:
    new_segment_list = [
        Segment(
            text_id=create_segment_request.text_id,
            content=segment.content,
            mapping=segment.mapping
        )
        for segment in create_segment_request.segments
    ]
    # Store the insert result but don't return it directly
    await Segment.insert_many(new_segment_list)

    return new_segment_list

async def get_translations(
        segment_id: str
    ):
    return [
        SegmentTranslation(
            text_id=str(uuid4()),
            title="Śikhin, Viśvabhū",
            source="source 1",
            language="en",
            content="To the buddhas: Vipaśyin,<br> Śikhin, Viśvabhū,<br>   Krakucchanda, Kanakamuni,<br> and Kāśyapa,<br>   And Śākyamuni—Gautama,<br> deity of all deities,   <br>To the seven warrior-like buddhas, I pay homage!"
        ),
        SegmentTranslation(
            text_id=str(uuid4()),
            title="Seven Buddhas",
            source="source 2",
            language="en",
            content="To the seven special buddhas,<br>   We say hello and thank you! <br>  You are like heroes who help everyone, <br>  And we bow to show we care."
        ),
        SegmentTranslation(
            text_id=str(uuid4()),
            title="སངས་རྒྱས་རྣམས་ལ།རྣམ་པར་གཟིགས",
            source="source 3",
            language="bhu",
            content="སངས་རྒྱས་རྣམས་ལ།རྣམ་པར་གཟིགས་དང་།ག<br>ཙུག་ཏོར་ཅན་དང་།ཐམས་ཅད་སྐྱོབ་དང་།<br>  འཁོར་བ་འཇིག་དང་།གསེར་ཐུབ་དང་།འོད་སྲུང་དང་། <br> ཤཱཀྱ་ཐུབ་པ་གཽ་ཏ་མ།ལྷ་ཡི་ལྷ།<br>  དཔའ་བོ་བདུན་པོ་འདི་དག་ལ་ཕྱག་འཚལ་ལོ།"
        ),
        SegmentTranslation(
            text_id=str(uuid4()),
            title="Ante los",
            source="Source 4",
            language="sp",
            content="Ante los budas: Vipaśyin,<br> Śikhin, Viśvabhukra   Krakucchanda,<br> Kanakamuni, and Kāśyapa   y Śākyamuni Gautama,<br> el dios de dioses <br>  ¡ante estos siete budas que<br> son como guerreros nos postramos!"
        ),
        SegmentTranslation(
            text_id=str(uuid4()),
            title="Seven Buddhas",
            source="Source 5",
            language="ko",
            content="비파시불, 시기불,<br> 비사부불,   구류손불,<br> 구나함모니불, 가섭불, <br>  그리고 석가모니불 - 고타마, <br> 모든 신들의 신께,   이 일곱 용사 같은 <br> 부처님들께 예배드립니다!"
        ),
        SegmentTranslation(
            text_id=str(uuid4()),
            title="諸仏：毘婆尸仏",
            source="Source 6",
            language="ja",
            content="諸仏：毘婆尸仏、<br> 尸棄仏、毘舍浮仏、 <br>  拘留孫仏、拘那含牟尼仏、迦葉仏、 <br>  そして釈迦牟尼仏—ゴータマ、諸天の天に、 <br>  この七人の勇者のような仏陀<br>たちに礼拝いたします！"
        ),
        SegmentTranslation(
            text_id=str(uuid4()),
            title="Бурхан багш",
            source="Source 7",
            language="mo",
            content="Бурхан багш нар: Вибашин,<br> Шихин, Вишвабу,<br>   Кракуччанда, Канакамуни,<br> Кашьяпа,   Мөн Шакьямуни—Гаутама,<br> бүх бурхадын бурхан, <br>  Эдгээр долоон баатарлаг бурхан<br> багш нарт би мөргөн залбирна!"
        )
    ]

async def get_commentaries(
        segment_id: str
    ):
    return [
        SegmentCommentry(
            text_id=str(uuid4()),
            title="པཎ་ཆེན་ཤཱཀྱ་མཆོག་ལྡན། དབུ་མ་འཇུག་པའི་རྣམ་བཤད་ངེས་དོན་གནད་ཀྱི་ཊཱི་ཀ",
            language="bo",
            count=1
        ),
        SegmentCommentry(
            text_id=str(uuid4()),
            title="པཎྜི་ཏ་ཛ་ཡ་ཨ་ནནྟ། དབུ་མ་ལ་འཇུག་པའི་འགྲེལ་བཤད།",
            language="bo",
            count=1
        ),
        SegmentCommentry(
            text_id=str(uuid4()),
            title="པཎྜི་ཏ་ཛ་ཡ་ཨ་ནནྟ། དབུ་མ་ལ་འཇུག་པའི་འགྲེལ་བཤད།",
            language="bo",
            count=2
        ),
        SegmentCommentry(
            text_id=str(uuid4()),
            title="གོ་བོ་རམ་འབྱམས་པ། འཇུག་འགྲེལ་ལྟ་བ་ངན་སེལ།",
            language="bo",
            count=1
        ),
        SegmentCommentry(
            text_id=str(uuid4()),
            title="དཔལ་ལྡན་ཟླ་བ་གྲགས་པ། དབུ་མ་ལ་འཇུག་པའི་བཤད་པ།",
            language="bo",
            count=2
        ),
        SegmentCommentry(
            text_id=str(uuid4()),
            title="དགོངས་པ་རབ་གསལ་ལས་སེམས་བསྐྱེད་དྲུག་པ། ཤོ་ལོ་ཀ ༡ ནས་ ༦༤",
            language="bo",
            count=1
        )
    ]   