# uv_build_pmt

A repository to (hopefully) demonstrate an issue with `uv build` and enable fixing it.

The repository represents a stripped down example of an internal library package, with most of the (possibly) relevant project meta-data retained.

For the purpose of publishing the LICENSE has been swapped out with Apache 2.0.

A singular module `src/utils/printing.py` has been retained to test the installation afterwards.

## Setup

git clone this repo and run `uv sync` then (possibly after activating venv) run:

```shell
python -c 'import uv_build_pmt'
```

and verify there are no errors.

## Issue

When building this library package using `uv build` two files are created in dist:
- uv_build_pmt-0.1.0-py3-none-any.whl (~10k bytes)
- uv_build_pmt-0.1.0.tar.gz (~10k bytes)

But the `.whl` does not contain the sources. So when you install this in a venv and try to import the package, you get an error.

```shell
uv pip install --force-reinstall .\dist\uv_build_pmt-0.1.0-py3-none-any.whl
python -c 'import uv_build_pmt'
```
> ModuleNotFoundError: No module named 'uv_build_pmt'

It does show up in `uv pip list` or `pip list` with the right version number, but it's just a shim.

## Expected

When building this library package *directly* with hatch (hatchling) instead using e.g. `uvx hatch build` (or `uv run hatch build` after installing hatch in the local env), the file in dist are:
- uv_build_pmt-0.1.0-py3-none-any.whl (~10k + ~2.5k bytes)
- uv_build_pmt-0.1.0.tar.gz (~10k bytes)

And now the `.whl` does contain the source code. To test

```shell
uvx hatch build
uv pip install dist\uv_build_pmt-0.1.0-py3-none-any.whl
python -c 'import uv_build_pmt'
```

and observe no errors this time.

## License

The `uv_build_pmt` library is licensed under Apache 2.0

## Contact

To report any issues feel free to reach out via e-mail me at
 [directly](mailto:noreply@cassini-technologies.com) (taking [this](a "replace noreply with j.snellenburg") into account).
