# CryoEM-scripts

Some Python and bash scripts to make cryoEM easier.


**Scripts to help scaling and merging data sets**

These four scripts are featured in our Acta D paper "Methods for Merging Data Sets in Electron Cryo-Microscopy" and aim to make merging data sets a bit more tolerable.

A couple of scripts are written by me, apologies for the poor python/bash styling:

`boxscaler.py` will find combinations of even box sizes that give a desired scaling factor.

`scale_ctf.sh` will do a pretty good* approximate job of rescaling your defocus values to a different pixel size. This bypasses having to re-run CTFFIND or Gctf, which is useful e.g. if micrographs are no longer on disk.

And a couple of much more nicely written scripts by Thomas Martin, Ana Casanal, and Takanori Nakane:

`determine_relative_pixel_size.py` will find the pixel size that maximises the correlation (measured with FSC) of one map to a reference map - useful for finding relative pixel sizes when merging data sets.

`rescale_particles.py` will rescale particle coordinates, for if you've decided to scale your datasets by rescaling your micrographs. Also does some STAR file wizardry to fix up various paths.

\*"pretty good" means +/- 40A compared to actually re-runnning GCTF. Considering this is probably very close or better than the precision of GCTF itself, especially at normal resolution regimes, I'd say "pretty good" really means "entirely good enough, especially if you plan on running per-particle CTF refinement anyway." At least in my experience, YMMV.
