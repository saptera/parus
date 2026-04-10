# PARUS Application Programming Interface (API)

The API reference for **Parus** is automatically generated from docstrings using 
[**Sphinx**](https://www.sphinx-doc.org/) with the [**Furo**](https://github.com/pradyunsg/furo) theme.

Users can download the `api.zip` file from the current directory for offline access. 
This archive is updated with each release to reflect the latest documentation.

After unzipping the archive, the generated documentation can be found at:

```
[current folder]/api/index.html
```

---

A `Makefile` is also provided to allow users to generate the documentation locally. To rebuild the API reference, run:

```
make rebuild
```

This command works on both **Windows** (via `MinGW-make`) and **Unix-like systems**.

After the build process is complete, the generated documentation can be found at:

```
[current folder]/build/html/index.html
```