import functools

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableSerializable

from .utils import get_llm_from_env

PROMPT_TEMPLATE = """用台灣用語的繁體中文，簡潔地以條列式總結文章重點。
在摘要後直接加入相關的英文 hashtag，以空格分隔。

文章內容：
{text}

摘要："""  # noqa


@functools.cache
def get_chain() -> RunnableSerializable:
    llm = get_llm_from_env()
    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm
    return chain


def summarize(text: str) -> str:
    chain = get_chain()
    ai_message: AIMessage = chain.invoke({"text": text})

    content: str | list[str | dict] = ai_message.content
    if isinstance(content, str):
        return content

    contents = []
    for item in content:
        if isinstance(item, str):
            contents.append(f"• {item}")

        if isinstance(item, dict):
            for k, v in item.items():
                contents.append(f"• {k}: {v}")

    return "\n".join(contents)
