from typing import Any
import numpy as np


def parse_brackets(val) -> list[Any]:
    stack = 0
    result = []
    try:
        for i, c in enumerate(val):
            if c == "[":
                if stack == 0:
                    j = i
                stack += 1
            if c == "]" and stack > 0:
                stack -= 1
                if stack == 0:
                    result.append(val[j : i + 1])
    except:
        pass

    return result

# tests for parse_brackets

assert parse_brackets(
    "Hello stuff in here] and also [sometimes recursive [brackets[0]]] in here"
) == ["[sometimes recursive [brackets[0]]]"]

assert (
    parse_brackets(
        "Hello stuff in here] and also [sometimes recursive [brackets[0]] in here"
    )
    == []
)

assert parse_brackets(
    r"Hello (stuff in here) and also [sometimes recursive {brackets[0]}] in here"
) == [r"[sometimes recursive {brackets[0]}]"]

assert parse_brackets(
    "Hello [stuff in here] and also [sometimes recursive [brackets[0]] [brackets[1]]] in here"
) == [
    "[stuff in here]",
    "[sometimes recursive [brackets[0]] [brackets[1]]]",
]


def eval_expander(prompts: list[str]) -> list[str]:
    return_prompts: list[str] = []
    if not isinstance(prompts, list):
        prompts = [prompts]
    for prompt in prompts:
        try:
            return_prompts += eval(prompt)
        except:
            return_prompts.append(prompt)

    return return_prompts


def expand_prompts(prompt: str | list[str], rand=False) -> str | list[str]:
    if isinstance(prompt, list):
        return (
            np.asarray([x for t in prompt for x in [expand_prompts(t)]])
            .flatten()
            .tolist()
        )
    brackets = parse_brackets(prompt)
    if len(brackets) > 0:
        t = [
            expand_prompts(prompt.replace(brackets[0], str(expansion)))
            for expansion in eval_expander(brackets[0])
        ]
        return_prompts: list[str | list[str]] | list[str] = (
            t if not isinstance(t[0], list) else [x for y in t for x in y]
        )
        if rand:
            np.random.shuffle(return_prompts)
        return return_prompts
    else:
        return prompt

# tests for expand_prompts
assert expand_prompts("hello") == "hello"
assert expand_prompts(["hello", "hi"]) == ["hello", "hi"]
assert expand_prompts(["there is [f'{x} colored' for x in ['red', 'green']] wall"]) == [
    "there is red colored wall",
    "there is green colored wall",
]

assert expand_prompts(
    [
        "[[f'{x} colored' for x in ['red', 'green']], [f'{x} glowing' for x in ['bright', 'weak']]] wall",
        "[[f'{x} colored' for x in ['blue', 'yellow']], [f'{x} glowing' for x in ['hot', 'cold']]] wall",
    ]
) == [
    "red colored wall",
    "green colored wall",
    "bright glowing wall",
    "weak glowing wall",
    "blue colored wall",
    "yellow colored wall",
    "hot glowing wall",
    "cold glowing wall",
]

assert expand_prompts(
    ["[f'{x} colored' for x in ['red', 'green']] ['tree','wall']"]
) == [
    "red colored tree",
    "red colored wall",
    "green colored tree",
    "green colored wall",
]

print(expand_prompts("['a','b']-['1','2']-['Y','Z']"))
print(expand_prompts("['a','b']-['1','2']-['Y','Z']", True))
print(expand_prompts("['a','b','c','d']-['1','2','3']"))
[
    "c-2",
    "c-1",
    "c-3",
    "b-3",
    "b-2",
    "b-1",
    "d-3",
    "d-1",
    "d-2",
    "a-1",
    "a-2",
    "a-3",
]
