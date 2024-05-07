from bytewax import operators as op
from typing import List
from bytewax.dataflow import Dataflow
from qdrant_client import QdrantClient
from utils.embedding import EmbeddingModelSingleton
from models.json_source import JSONSource
from models.post import ChunkedPost, CleanedPost, EmbeddedChunkedPost, RawPost
from utils.qdrant import QdrantVectorOutput


def build(in_memory: bool = False, data_source_path: List[str]=None):
    embedding_model = EmbeddingModelSingleton()
    flow = Dataflow("flow")
    if data_source_path:
        stream = op.input(
            "input", flow, JSONSource(data_source_path)
        )
        stream = op.map("raw_post", stream, RawPost.from_source)
        stream = op.map("cleaned_post", stream, CleanedPost.from_raw_post)
        stream = op.flat_map(
            "chunked_post",
            stream,
            lambda cleaned_post: ChunkedPost.from_cleaned_post(
                cleaned_post, embedding_model=embedding_model
            ),
        )
        stream = op.map(
            "embedded_chunked_post",
            stream,
            lambda chunked_post: EmbeddedChunkedPost.from_chunked_post(
                chunked_post, embedding_model=embedding_model
            ),
        )
        op.inspect("inspect", stream, print)
        op.output(
            "output", stream, _build_output(model=embedding_model, in_memory=in_memory)
        )
    return flow


def _build_output(model: EmbeddingModelSingleton, in_memory: bool = False):
    if in_memory:
        return QdrantVectorOutput(
            vector_size=model.embedding_size,
            client=QdrantClient(":memory:"),
        )
    else:
        return QdrantVectorOutput(
            vector_size=model.embedding_size,
        )
