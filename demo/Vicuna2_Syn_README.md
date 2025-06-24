# Synthesis for Vicuna2 RTL

## Prerequisites

Make sure to use patched versions/forks of Vicuna2 repositories:
- `vicuna2_tinyml_benchmarking`: https://github.com/PhilippvK/vicuna2_tinyml_benchmarking/tree/philippvk
- `vicuna2_core`: https://github.com/PhilippvK/vicuna2_core/tree/philippvk

## FPGA Synthesis

### Relevant Changes

- `Makefile2`: Vincuna2 variant of `Makefile`
- `Makefile2`: Vincuna2 variant of `Makefile`

### Commands

```sh
# Generate Vivado project (fixed clk period)
make -f Makefile2 RAM_FILE=test.vmem BOARD=genesys2 CORE=cv32e40x CLK_PER=50

# Search for max clock frequency
make -f Makefile2 RAM_FILE=test.vmem BOARD=genesys2 CORE=cv32e40x perf
```

### Plotting

#### Prerequisites

```sh
# Hint: enter virtual environment first!
pip install -r requirements.txt
```

#### Commands

Make sure that the reports are copied to the proper directories in `reports`

```sh
# Convert .rpt files to .csv
find reports -name "utilization_report.rpt" -exec python3 parse_vivado_util_hier_report.py {} -o {}.csv --agg pipeline \;

# Combine reports into single file
python3 collect_reports.py

# Launch jupyter
python3 -m jupyter notebook --ip 0.0.0.0

# Copy the output to the Plotting.ipynb notebook
```



### Synthesize Old Vicuna as reference

```sh
# Original paper used ibex core
make RAM_FILE=test.vmem BOARD=genesys2 CORE=ibex perf
make RAM_FILE=test.vmem BOARD=genesys2 CORE=cv32e40x perf
```

## ASIP Synthesis

TODO
