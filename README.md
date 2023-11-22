# prompt-python-expansion
Expands a single prompt into multiple prompts by running eval()

## Example
Expands python list comprehension like `a ['red','blue'] tree in a ['desert', 'city']`,`[f'{x} dogs' for x in range(start,[stop,step])]` or `[f'{x} dogs' for x in ['black','grey']]`. 
If set to 'Prompts' will automatically adjust the batch count. 
If positive and negative prompts are expanded then it will result in the product, for example for `pos=[1,2,3]` and `neg=[4,5]`:
 positive = `[1,1,2,2,3,3]`
 negative = `[4,5,4,5,4,5]`
 Same for multiple [] in single prompt

Clashes with dynamic prompt extension
