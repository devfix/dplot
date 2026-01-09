# dplot

**Minimal pgfplot wrapper for python**

This project does not claim to be a complete wrapper of all features of pgfplot.
The aim is merely to provide convenient functions for the most common cases of plots.

## Installation in a local venv

`source .venv/bin/activate`<br/>
`python3 -m pip install git+https://github.com/devfix/dplot.git`

**Optional: run the tests**<br/>
Clone the repo to somewhere on your machine
```bash
cd <repo path>  # enter repo path
python3 -m venv .venv  # create new venv
source .venv/bin/activate  # enter venv
pip install pytest pandas opencv-python  # install dependencies of the tests
python3 -m pytest  # run tests
```

 and run `pytest` in the root directory of the repo.

## Examples / Tests
- [ ] 1st order low-pass filter

## TODO
- [ ] Better compilation error detection: evalue return code of both processes etc.
- [ ] Titel
- [ ] MWE
- [ ] More examples
- [ ] code comments
