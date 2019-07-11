# CryoEM-scripts

Some Python and bash scripts to make cryoEM easier.


**Scripts to help scaling and merging data sets**

`boxscaler.py` will find combinations of even box sizes that give a desired scaling factor.

`scale_ctf.sh` will do a pretty good approximate job of rescaling your defocus values to a different pixel size. This bypasses having to re-run CTFFIND or Gctf, which is useful e.g. if micrographs are no longer on disk

