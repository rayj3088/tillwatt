# Third-party software and data

Everything Tillwatt borrows, with its license and how we use it.
Checked 2026-09-28 from each project's public repository page. LICENSE files were not read directly; verify before release.

Rule: borrowed models are wrapped as converter cards behind the conservation check. None of them owns the ledger.

## pvlib-python
- Repo: https://github.com/pvlib/pvlib-python
- License: BSD-3-Clause
- Use: solar converter, CEC panel and inverter data
- Version: pin when added
- Cite: Anderson, Hansen, Holmgren, Jensen, Mikofski, Driesse. "pvlib python: 2023 project update." JOSS 8(92), 5994 (2023). https://doi.org/10.21105/joss.05994

## PyPSA
- Repo: https://github.com/PyPSA/PyPSA
- License: MIT (code), CC-BY-4.0 (docs)
- Use: least-cost baseline design per site, to score player farms against. Not the hourly agent engine.
- Version: pin when added
- Cite: Brown, Horsch, Schlachtberger. "PyPSA: Python for Power System Analysis." JORS 6(1) (2018). https://doi.org/10.5334/jors.188

## AquaCrop-OSPy
- Repo: https://github.com/aquacropos/aquacrop
- License: Apache-2.0
- Use: water-stress and yield function, validation baseline
- Known gap: no fertility stress, weed management, or perennial crops (per its README). Nitrogen is modeled in Tillwatt itself.
- Note: not the official FAO implementation.
- Version: pin when added
- Cite: see the paper linked in its README (https://doi.org/10.1016/j.agwat.2021.106976)

## PASE (Python Agrivoltaic Simulation Environment)
- Code: https://gitlab.uliege.be/pase/pase_1.0 (not yet inspected)
- License: MIT (per the paper and the ULiege archive; confirm in the repo)
- Use: reference for checking Tillwatt's shading and light-sharing math. Not a dependency.
- Cite: Bruhwyler et al. "Modelling light-sharing in agrivoltaics: the open-source Python Agrivoltaic Simulation Environment (PASE 1.0)." Agroforestry Systems (2024). https://doi.org/10.1007/s10457-024-01090-8

## python-microgrid / pymgrid
- Repo: https://github.com/ahalev/python-microgrid
- License: LGPL-3.0
- Use: design reference only (fixed vs flex modules, benchmark microgrids). Not a dependency, so nothing here needs relicensing or upstream sharing.
- Latest release seen: v1.4.1 (April 2024)
- Cite: Henri, Levent, Halev, Alami, Cordier. "pymgrid: An Open-Source Python Microgrid Simulator for Applied Artificial Intelligence Research." arXiv:2011.08004 (2020).

## Adding an entry
Every new borrowed tool or dataset gets: repo or source URL, license, what we use it for, pinned version, citation. Every borrowed number also gets a row in sources/SOURCES.csv.
