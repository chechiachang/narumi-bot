import functools
import os

from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import Distance
from qdrant_client.models import FieldCondition
from qdrant_client.models import Filter
from qdrant_client.models import MatchValue
from qdrant_client.models import PointStruct
from qdrant_client.models import VectorParams

from .llm import create_embeddings


@functools.cache
def get_qdrant_client() -> QdrantClient:
    url = os.getenv("QDRANT_URL")

    if not url:
        logger.warning("QDRANT_URL is not set, using in-memory database")
        return QdrantClient(location=":memory:")

    return QdrantClient(url=url)


@functools.cache
def get_collection_name() -> str:
    collection_name = os.getenv("QDRANT_COLLECTION_NAME")
    if not collection_name:
        logger.warning("QDRANT_COLLECTION_NAME is not set, using default collection name")
        collection_name = "telegram"

    client = get_qdrant_client()
    if client.collection_exists(collection_name):
        return collection_name

    client.create_collection(
        collection_name,
        vectors_config=VectorParams(
            size=1536,
            distance=Distance.COSINE,
        ),
    )
    return collection_name


def create_points(texts: str | list[str], **kwargs) -> list[PointStruct]:
    if isinstance(texts, str):
        texts = [texts]

    response = create_embeddings(texts)

    return [
        PointStruct(
            id=idx,
            vector=data.embedding,
            payload={"text": text} | kwargs,
        )
        for idx, (data, text) in enumerate(zip(response.data, texts))
    ]


def upsert_to_qdrant(text: str | list[str], **kwargs) -> None:
    logger.info("upsert text: {} to qdrant", text)

    collection_name = get_collection_name()
    client = get_qdrant_client()
    points = create_points(text, **kwargs)
    client.upsert(collection_name, points)


def search_qdrant(text: str, chat_id: int) -> str:
    logger.info("searching qdrant for text: {}", text)

    client = get_qdrant_client()
    collection_name = get_collection_name()

    response = create_embeddings([text])

    points = client.search(
        collection_name=collection_name,
        query_vector=response.data[0].embedding,
        query_filter=Filter(
            must=[
                FieldCondition(
                    key="chat_id",
                    match=MatchValue(
                        value=chat_id,
                    ),
                ),
            ],
        ),
    )

    logger.info("search result: {}", points)

    s = ""
    for point in points:
        payload = point.payload
        text = payload.get("text")
        if not text:
            continue

        chat_id = int(payload.get("chat_id"))
        message_id = int(payload.get("message_id"))

        if chat_id < 0:
            chat_id += 1_000_000_000_000

        telegram_url = f"https://t.me/c/{chat_id}/{message_id}"

        s += f"{telegram_url}\n{text}\n"

    return s
