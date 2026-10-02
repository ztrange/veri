"""The one reader of JSON documents written back to back, as gh_rest_list prints a listing."""
import json

_WHITESPACE = " \t\n\r"


def documents(text):
    """The JSON documents in `text`, in order, unflattened."""
    found, at, decoder = [], 0, json.JSONDecoder()
    while True:
        while at < len(text) and text[at] in _WHITESPACE:
            at += 1
        if at == len(text):
            return found
        document, at = decoder.raw_decode(text, at)
        found.append(document)


def items(text):
    """The elements of every document in `text`, as one list."""
    return [item for document in documents(text) for item in document]
