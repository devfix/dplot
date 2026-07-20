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

### Four-Sided Multi-Axis System

- **Independent Axis Configuration:** Fully customize Top (`'t'`), Bottom (`'b'`), Left (`'l'`), and Right (`'r'`) axes independently on a single figure.
    
- **Seamless Multi-Axis Overlays:** Plot different datasets against entirely different X and Y axes on the same chart (e.g., combining a bottom-left linear plot with a top-right secondary scale) without manual alignment hacks.
    
- **Linear & Logarithmic Scaling:** Easily switch between linear and logarithmic scales with customizable logarithmic base values.
    
- **Smart Data Limits & Scaling:** Automatically detect and compute axis limits from your data, apply mathematical scaling factors to axes, or override limits manually.
    
- **Precision Labeling:** Configure custom axis labels with adjustable millimeter padding shifts for perfect typographical alignment.
    

### Comprehensive Styling & Palette

- **Rich Color Enumerations:** Access an extensive `Color` library featuring core design colors, the complete W3C/SVG standard color palette, and the Matplotlib/Tableau 10 palette (`TAB_BLUE`, `TAB_ORANGE`, etc.).
    
- **Smart Color Lookup & Transparency:** Use string-based color lookups (e.g., `'tab:blue'`, `'dark-gray'`) or define custom transparent colors using backend-agnostic RGBA representations (`RGBAColor`).
    
- **Fine-Grained Line Styles:** Choose from a wide array of line styles, including solid, dashed, dotted, and dash-dotted variations, complete with density modifiers (e.g., `densely dotted`, `loosely dashed`).
    
- **Advanced Marker Control:** Apply diverse data markers (circles, squares, triangles, crosses, diamonds, asterisks) with built-in frequency controls (`marker_repeat` and `marker_phase`) to prevent visual clutter on dense datasets.
    
- **Semantic Thickness Presets:** Apply standardized line weights using semantic enum presets (from `ULTRA_THIN` to `ULTRA_THICK`) or specify exact point measurements.
    

### Grid, Tick, & Legend Control

- **Dual-Layer Grid Layouts:** Independently enable, color, and style major and minor background grid lines.
    
- **Custom Tick Management:** Precisely configure major tick intervals, minor tick subdivisions, tick colors, line thickness, and opposite-axis mirroring.
    
- **Flexible Legend Positioning:** Place legends inside or outside the plotting area using semantic vertical and horizontal alignment anchors (`HAlign`, `VAlign`), or override with exact coordinate mapping.
    
- **Typography & Unified Legends:** Customize legend font sizes in absolute points, add optional legend box titles, and automatically generate unified legend handles across complex multi-axis overlays.


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
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/classic_plot_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/classic_plot.expected.png" width="400"/>
        </a>
      </td>
    </tr>
    <!-- s-parameters -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/s_parameters_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/s_parameters.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/s_parameters_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/s_parameters.expected.png" width="400"/>
        </a>
      </td>
    </tr>
    <!-- crlb -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/crlb_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/crlb_10.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/crlb_typst.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/crlb_10.expected.png" width="400"/>
        </a>
      </td>
    </tr>
    <!-- all axes -->
    <tr>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/all_axes_latex.py">
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-latex/all_axes.expected.png" width="400"/>
        </a>
      </td>
      <td align="center">
        <a target="_blank" href="https://github.com/devfix/dplot/blob/main/tests/all_axes_typst.py">
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
