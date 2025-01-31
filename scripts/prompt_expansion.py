from modules import scripts
import gradio as gr
import itertools
from modules.ui_components import InputAccordion
import numpy as np
from .util import expand_prompts


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

        with InputAccordion(
            value=True, label="Enable Prompt expansion"
        ) as self.checkbox:
            self.markdown = gr.Markdown(
                value=(
                    "Expands python list comprehension like `a ['red','blue'] tree in a ['desert', 'city']`,`[f'{x} dogs' for x in range(start,[stop,step])]`"
                    " or `[f'{x} dogs' for x in ['black','grey']]`. \nIf set to 'Prompts' will automatically adjust the batch count. \nIf positive and negative"
                    " prompts are expanded then it will result in the product, for example for `pos=[1,2,3]` and `neg=[4,5]`:\n positive = `[1,1,2,2,3,3]`\n"
                    " negative = `[4,5,4,5,4,5]`\n Same for multiple [] in single prompt\n\nClashes with dynamic prompt extension"
                )
            )
            with gr.Row():
                self.output = gr.Radio(
                    choices=["Multiline", "Prompts"],
                    value="Prompts",
                    label="As what the multiple prompts should be returned",
                )
                self.random_radio = gr.Radio(
                    label="Randomization",
                    choices=["None", "Per list", "fully"],
                    type="index",
                    value=False,
                    info="Shuffle the expanded prompts randomly",
                )
        return (self.markdown, self.checkbox, self.output, self.random_radio)

    def show(self, is_img2img):
        """
        is_img2img is True if this function is called for the img2img interface, and Fasle otherwise

        This function should return:
         - False if the script should not be shown in UI at all
         - True if the script should be shown in UI if it's selected in the scripts dropdown
         - script.AlwaysVisible if the script should be shown in UI at all times
        """

        return scripts.AlwaysVisible

    def setup(
        self, p, *args
    ):  # this isn't the setup for this script, but refers to the setup of the prompt from the main app and is a hook.
        """For AlwaysVisible scripts, this function is called when the processing object is set up, before any processing starts.
        args contains all values returned by components from ui().
        """
        checkbox = self.checkbox
        random = self.random_radio

        if not checkbox:
            return

        prompt_pos = p.prompt.strip()
        prompt_neg = p.negative_prompt.strip()
        prompt_pos = expand_prompts(
            [p.strip() for p in prompt_pos.split("\n") if p.strip()], random
        )
        prompt_neg = expand_prompts(
            [p.strip() for p in prompt_neg.split("\n") if p.strip()], random
        )

        if len(prompt_neg) == 0:
            prompt_neg = [""]

        combinations = list(itertools.product(prompt_pos, prompt_neg))
        p.prompt, p.negative_prompt = next(
            (list(a), list(b)) for a, b in [zip(*combinations)]
        )

        p.n_iter = len(p.prompt) // p.batch_size
