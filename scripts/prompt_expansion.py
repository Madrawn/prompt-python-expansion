from modules import scripts
import gradio as gr
import itertools
from modules.ui_components import InputAccordion
import numpy as np


class PromptExpansionScript(scripts.Script):
    def __init__(self):
        pass

    def title(self):
        """this function should return the title of the script. This is what will be displayed in the dropdown menu."""

        return "Prompt expansion"

    def ui(self, is_img2img):
        """this function should create gradio UI elements. See https://gradio.app/docs/#components
        The return value should be an array of all components that are used in processing.
        Values of those returned components will be passed to run() and process() functions.
        """

        with InputAccordion(value=True, label="Enable Prompt expansion") as self.checkbox:
            self.markdown = gr.Markdown(
                value=(
                    "Expands python list comprehension like `a ['red','blue'] tree in a ['desert', 'city']`,`[f'{x} dogs' for x in range(start,[stop,step])]`"
                    " or `[f'{x} dogs' for x in ['black','grey']]`. \nIf set to 'Prompts' will automatically adjust the batch count. \nIf positive and negative"
                    " prompts are expanded then it will result in the product, for example for `pos=[1,2,3]` and `neg=[4,5]`:\n positive = `[1,1,2,2,3,3]`\n"
                    " negative = `[4,5,4,5,4,5]`\n Same for multiple [] in single prompt\n\nClashes with dynamic prompt extension"
                )
            )
            with gr.Row():
                self.output = gr.Radio(choices=["Multiline", "Prompts"], value="Prompts", label="As what the multiple prompts should be returned")
        return (self.markdown, self.checkbox, self.output)

    def show(self, is_img2img):
        """
        is_img2img is True if this function is called for the img2img interface, and Fasle otherwise

        This function should return:
         - False if the script should not be shown in UI at all
         - True if the script should be shown in UI if it's selected in the scripts dropdown
         - script.AlwaysVisible if the script should be shown in UI at all times
        """

        return scripts.AlwaysVisible

    def setup(self, p, *args):
        """For AlwaysVisible scripts, this function is called when the processing object is set up, before any processing starts.
        args contains all values returned by components from ui().
        """
        prompt_pos = p.prompt.strip()
        prompt_neg = p.negative_prompt.strip()
        prompt_pos = expand_prompts([p.strip() for p in prompt_pos.split("\n") if p.strip()])
        prompt_neg = expand_prompts([p.strip() for p in prompt_neg.split("\n") if p.strip()])
        if len(prompt_neg) == 0:
            prompt_neg = [""]
        combinations = list(itertools.product(prompt_pos, prompt_neg))
        p.prompt, p.negative_prompt = next((list(a), list(b)) for a, b in [zip(*combinations)])
        p.n_iter = len(p.prompt) // p.batch_size


def parse_brackets(val):
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


def eval_expander(prompts: list[str]):
    return_prompts = []
    if not isinstance(prompts, list):
        prompts = [prompts]
    for prompt in prompts:
        try:
            return_prompts += eval(prompt)
        except:
            return_prompts.append(prompt)

    return return_prompts


def expand_prompts(prompt):
    if isinstance(prompt, list):
        return np.asarray([x for t in prompt for x in [expand_prompts(t)]]).flatten().tolist()
    brackets = parse_brackets(prompt)
    if len(brackets) > 0:
        t = [expand_prompts(prompt.replace(brackets[0], str(expansion))) for expansion in eval_expander(brackets[0])]
        return t if not isinstance(t[0], list) else [x for y in t for x in y]
    else:
        return prompt


assert parse_brackets("Hello stuff in here] and also [sometimes recursive [brackets[0]]] in here") == ["[sometimes recursive [brackets[0]]]"]
assert parse_brackets("Hello stuff in here] and also [sometimes recursive [brackets[0]] in here") == []
assert parse_brackets(r"Hello (stuff in here) and also [sometimes recursive {brackets[0]}] in here") == [r"[sometimes recursive {brackets[0]}]"]
assert parse_brackets("Hello [stuff in here] and also [sometimes recursive [brackets[0]] [brackets[1]]] in here") == [
    "[stuff in here]",
    "[sometimes recursive [brackets[0]] [brackets[1]]]",
]
assert expand_prompts("hello") == "hello"
assert expand_prompts(["hello", "hi"]) == ["hello", "hi"]
assert expand_prompts(["[f'{x} colored' for x in ['red', 'green']] wall"]) == ["red colored wall", "green colored wall"]
assert expand_prompts(["[f'{x} colored' for x in ['red', 'green']] ['tree','wall']"]) == [
    "red colored tree",
    "red colored wall",
    "green colored tree",
    "green colored wall",
]
