import markdown2

def render_markdown(text):
    if not text:
        return ''
    return markdown2.markdown(
        text,
        extras=["fenced-code-blocks", "tables", "strike", "footnotes"]
    )
