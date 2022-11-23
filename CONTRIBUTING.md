# How to Contribute

Contributions are welcome and very much appreciated.

There are multiple ways in which you can contribute to the project.


## Report Bugs
Please report bugs by opening a new issue on Github.

If you are reporting a bug, please include the following information:

- Version of the package and the versions of the required packages
- Your operating system
- Detailed steps to reproduce the bug


If the bug/issue is on the website, please include the following information:

- IEEE Society
- Link to the Call for Paper that is not (or incorrectly) listed

## Fix Bugs
Any open issue that is tagged with "bug" is open to whoever wants to fix it.


## Adding More IEEE Societies/Journals
You can always add new societies or journals to the website.

Please make sure to follow these guidelines:

1. Create a new file for a new society, e.g., `comsoc.py` for the
   Communications Society.
2. This module needs to provide a function called `get_all_cfp()` which returns
   a pandas data frame that contains the columns specified in the
   [`constants.py`](constants.py) module.
3. Add the new society to the `SOCIETIES` array in
   [`generate_website.py`](generate_website.py) with the required information.
