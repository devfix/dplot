# dplot

**Minimal python wrapper for pgfplot (LaTex) and lilaq (Typst)**

<hr/>

This project does not claim to be a complete wrapper of all features the plotting libraries support.
The aim is merely to provide convenient functions for the most common cases of plots.

## Example plots

The following table shows a comparision of the LaTex and Typst output.
Click on the images to see the code that created them.  
Just ignore the import of `tests.tools` and the `assert` statements.

<br/>
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
          <img src="https://raw.githubusercontent.com/devfix/dplot/refs/heads/main/tests/out-typst/test_classic_plot.expected.png" width="400"/>
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
