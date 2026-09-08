# Running the tasks

Every task in this workshop is a plain Python file with `# %%` cell markers, for
example `tasks/task_01_cross_sections/1_isotope_xs_plot.py`. The pages in this
book are those files rendered by [Quarto](https://quarto.org) after running them.

The cell markers mean the same file works three ways, so you can pick whichever
suits you.

## Jupyter Lab

Start Jupyter Lab from the repository root.

```bash
jupyter lab
```

Navigate to the task you want in the `tasks` folder, then right click the `.py`
file and choose **Open With** and then **Notebook**. Jupytext converts the cell
markers into notebook cells on the fly, so you get the usual notebook interface
with a kernel, and your edits are saved back into the `.py` file.

Double clicking the file instead opens it in the plain text editor, which is
useful for reading but does not let you run cells.

## VS Code

Open the repository folder in VS Code with the Python extension installed. Each
`# %%` marker gets a **Run Cell** link above it and the output appears in the
interactive window. This works on the `.py` file directly with no conversion
step.

## Straight through

Because the tasks are ordinary Python files you can also run a whole task from a
terminal.

```bash
cd tasks/task_01_cross_sections
python 1_isotope_xs_plot.py
```

Plots that a notebook would show inline are not displayed this way, but the
simulation runs and any files the task writes are still produced.

## Why not notebooks

The tasks used to be `.ipynb` notebooks. The `.py` files hold exactly the same
code and text, they just avoid the JSON wrapper, so they diff and merge cleanly,
can be run and imported like any other Python file, and can be searched with
ordinary tools.
