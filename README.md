# dplot

**Minimal python wrapper for pgfplot (LaTex) and lilaq (Typst)**

<hr/>

This project does not claim to be a complete wrapper of all features the plotting libraries support.
The aim is merely to provide convenient functions for the most common cases of plots.

## Features

| **Feature**          | **LaTeX Backend (LatexGenerator)**      | **Typst Backend (TypstGenerator)**        |
| -------------------- | --------------------------------------- | ----------------------------------------- |
| **Target Engine**    | PGFPlots / TikZ                         | Lilaq (`@preview/lilaq`)                  |
| **Output Format**    | Native `.tex` source files, PDF         | Native `.typ` source files, PDF           |
| **Compilation**      | Headless PDF compilation via `pdflatex` | Instant PDF rendering via `typst compile` |
| **Styling Paradigm** | Key-value TikZ style libraries          | Modern Typst `#show` and `set` rules      |

### Multi-Axis & Complex Layouts

Handling overlaid data with differing units or orders of magnitude is natively built into the architecture.

- **Arbitrary Axis Pairing:** Seamlessly map data series to any combination of axes (e.g., bottom-left, bottom-right, or top-left) without manually calculating container bounding boxes.

- **Intelligent Axis Positioning:** Dynamically positions primary and secondary axes (`position: top`, `position: right`) so labels, tick marks, and titles never collide.
    

### Precision Styling & Aesthetics

`dplot` exposes fine-grained control over every visual element through modular setup classes (`LineSetup`, `Marker`, `TickSetup`, `GridSetup`, and `LegendSetup`).

#### Lines & Markers

- **Extensive Line Styles:** Support for solid, dotted, dashed, and dash-dotted lines, alongside custom dash-array patterns (such as densely or loosely dashed variations).
    
- **Alpha & Color Resolution:** Full support for RGB, RGBA, and standard color palettes with automatic transparency percentage mapping.
    
- **Smart Marker Subsetting:** Prevent symbol clutter on high-density datasets by specifying marker repeat intervals (mapping to `every` in Lilaq and `mark repeat` in PGFPlots) while keeping the underlying line continuous.
    
- **Geometric Symbol Mapping:** Rich library of built-in shapes (circles, squares, triangles, diamonds, crosses, stars) with automatic differentiation between filled symbols (solid dots) and open geometric outlines.
    
- **Automatic Color Synchronization:** Marker strokes and fills dynamically inherit their parent plot line color by default, with overrides available for custom accents.
    

#### Grids & Ticks

- **Granular Tick Control:** Enable or disable major and minor ticks independently, enforce exact numerical step distances, and specify exact subtick counts.
    
- **Mirrored & Opposite Ticks:** Easily project tick marks onto opposite borders while selectively suppressing redundant numerical labels.
    
- **Custom Grid Dimensions:** Independent control over major and minor grid line thickness, color, and stroke patterns.
    

### Backend-Agnostic Legend Engine

Legends in `dplot` are designed around abstract semantic positioning rather than engine-specific anchor hacks.

- **Semantic Positioning:** Position legends inside or outside the data area using intuitive horizontal (`LEFT`, `CENTER`, `RIGHT`) and vertical (`TOP`, `CENTER`, `BOTTOM`) alignments.
    
- **Precision Coordinate Overrides:** For exact graphical placement, supply raw `(x, y)` relative coordinates that automatically translate to PGFPlots description space or Typst percentage offsets.
    
- **Unified Multi-Axis Legends:** `dplot` utilizes intelligent proxy handles (dummy plots with empty data arrays) across overlaid diagrams. This guarantees that data plotted on secondary axes still registers perfectly in a single, unified legend box on the primary layer.
    
- **Typography & Scaling:** Global font size scaling in absolute points alongside optional styled legend header titles.


## Example plots

The following table shows a comparision of the LaTex and Typst output.
Click on the images to see the code that created them.  
Just ignore the import of `tests.tools` and the `assert` statements.

**Important notice**: The plots are not necessarily intended to look nice and rather just show many
 features of dplot. You can customize it to your favor :)
<br/>

<table style="background-color: white;">
  <thead>
    <tr>
      <th align="center"><strong>Latex Generated</strong></th>
      <th align="center"><strong>Typst Generated</strong></th>
    </tr>
  </thead>
  <tbody>
    <!-- classic plot -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/classic_plot_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/classic_plot.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_classic_plot_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/classic_plot.expected.png" width="400"/>
        </a>
      </td>
    </tr>
    <!-- s-parameters -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_s_parameters_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/s_parameters.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_s_parameters_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/s_parameters.expected.png" width="400"/>
        </a>
      </td>
    </tr>
    <!-- crlb -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_crlb_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/crlb_10.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_crlb_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/crlb_10.expected.png" width="400"/>
        </a>
      </td>
    </tr>
    <!-- all axes -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_all_axes_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/all_axes.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/test_all_axes_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/all_axes.expected.png" width="400"/>
        </a>
      </td>
    </tr>
  </tbody>
</table>


## Installation in a local venv

```bash
source .venv/bin/activate
python3 -m pip install git+https://github.com/devfix/dplot.git
```

**Optional: run the tests**<br/>
Clone the repo to somewhere on your machine
```bash
git clone "https://github.com/devfix/dplot.git"  # download dplot repo, alternatively download the zip and extract
cd dplot  # enter repo path
python3 -m venv .venv  # create new venv
source .venv/bin/activate  # enter venv
pip install pytest pandas opencv-python matplotlib  # install dependencies of the tests
python3 -m pytest  # run tests
```

## Examples / Tests
- [ ] 1st order low-pass filter

## TODO
- [ ] Better compilation error detection: evalue return code of both processes etc.
- [ ] Titel
- [ ] MWE
- [ ] More examples
- [ ] code comments
