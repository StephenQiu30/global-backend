---
title: Complex Markdown Test
lang: en
tags: [markdown, test, fidelity]
---

# Introduction

This is a **complex** Markdown document for testing fidelity protection.

## Code Examples

Inline code: `print("hello")` and `len(data)`.

Fenced code block:

```python
def greet(name: str) -> str:
    """Return a greeting message."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    print(greet("World"))
```

JavaScript example:

~~~
const add = (a, b) => a + b;
console.log(add(2, 3));
~~~

## Links and Images

Visit [Python Docs](https://docs.python.org/3/) for more info.

See also: [Local Guide](./docs/guide.md) and [Parent README](../README.md).

Badge: ![Build Status](https://img.shields.io/badge/build-passing-green)

Logo: ![Project Logo](./assets/logo.png)

## Table

| Feature | Status | Priority |
|---------|--------|----------|
| Code    | done   | high     |
| Links   | done   | medium   |
| Tables  | wip    | low      |

## Blockquote

> This is a blockquote with `inline code` and a [link](https://example.com).
>
> It spans multiple paragraphs.

## HTML Comments

<!-- This is a single-line comment -->

<!--
This is a
multi-line comment
-->

## Nested Structures

1. First item with `code`
2. Second item with [link](https://example.com)
3. Third item:
   - Sub-item with **bold**
   - Sub-item with ![img](./pic.png)

---

*End of document.*
