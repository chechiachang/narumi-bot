import re
import tempfile

import httpx
from langchain_community.document_loaders.html_bs import BSHTMLLoader
from langchain_community.document_loaders.pdf import PyPDFLoader

DEFAULT_HEADERS = {
    "User-Agent": "Chrome/126.0.0.0 Safari/537.36",
}


def download(path_or_url: str) -> str:
    if path_or_url.startswith("http"):
        resp = httpx.get(url=path_or_url, headers=DEFAULT_HEADERS)
        resp.raise_for_status()

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf" if resp.headers.get("content-type") == "application/pdf" else None,
        ) as fp:
            fp.write(resp.content)
            f = fp.name
    else:
        f = path_or_url

    return f


def find_url(s: str) -> str:
    # Regular expression pattern to match URLs
    url_pattern = r"https?://[^\s]+"

    # Search for the pattern in the input string
    match = re.search(url_pattern, s)

    # Return the URL if a match is found, otherwise return an empty string
    if match:
        return match.group(0)

    return ""


def load_html(f: str) -> str:
    loader = BSHTMLLoader(f)
    docs = loader.load()
    return "\n".join([doc.page_content for doc in docs])


def load_pdf(f: str) -> str:
    loader = PyPDFLoader(f)
    docs = loader.load()
    return "\n".join([doc.page_content for doc in docs])


def load_url(url: str) -> str:
    f = download(url)
    if f.endswith(".pdf"):
        return load_pdf(f)

    return load_html(f)
