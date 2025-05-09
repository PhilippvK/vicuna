# TODO

import argparse
from pathlib import Path
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument("report", help="TODO")
parser.add_argument("--output", "-o", default=None, help="TODO")
parser.add_argument("--agg-mode", default="default", choices=["none", "default", "detailed"], help="TODO")
args = parser.parse_args()

report_file = Path(args.report)
assert report_file.is_file()

if args.output is not None:
    out_file = Path(args.output)
else:
    out_file = None

with open(report_file, "r") as f:
    content = f.read()

PRE = "1. Utilization by Hierarchy"
POST = "Note: The sum of lower-level cells may be larger than their parent cells total, due to cross-hierarchy LUT combining"

assert PRE in content

content = content.split(PRE)[-1]

assert POST in content

content = content.split(POST)[0]

lines = list(map(lambda x: x.strip(), content.splitlines()))

lines = [line for line in lines if len(line) > 1 and "---" not in line]

def parse_line(line):
    assert len(line) > 1
    assert line[0] == "|"
    assert line[-1] == "|"
    line = line[1:-1]
    cols = line.split("|")
    cols = list(map(lambda x: x.strip(), cols))
    return cols

data = list(map(parse_line, lines))

assert len(data) > 1

col_names = data[0]

data = data[1:]

df = pd.DataFrame(data, columns=col_names)
if "Module" not in df.columns:
    df["Module"] = None

if args.agg_mode in ["default", "detailed"]:
    u_ram_instances = ["u_ram", "u_iram"]
    u_core_instances = ["core"]
    u_fpu_instances = ["fpu_ss_i"]
    v_core_instances = ["v_core"]
    u_ram_df = df[df["Instance"].isin(u_ram_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("u_ram").to_frame().T
    u_core_df = df[df["Instance"].isin(u_core_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("u_core").to_frame().T
    u_fpu_df = df[df["Instance"].isin(u_fpu_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("u_fpu").to_frame().T
    v_core_df = df[df["Instance"].isin(v_core_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("v_core").to_frame().T
    dfs = [u_ram_df, u_core_df, u_fpu_df]
    if args.agg_mode == "default":
        dfs.append(v_core_df)
    elif args.agg_mode == "detailed":
        v_core_pipeline_instances = ["pipeline"]  # TODO: check
        v_core_fpu_instances = ["fpu"]  # TODO: check
        v_core_vregfile_instances = ["vregfile"]  # TODO: check
        v_core_pipeline_df = df[df["Instance"].isin(v_core_pipeline_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("v_core_pipeline").to_frame().T
        v_core_fpu_df = df[df["Instance"].isin(v_core_fpu_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("v_core_fpu").to_frame().T
        v_core_vregfile_df = df[df["Instance"].isin(v_core_vregfile_instances)].set_index(["Instance", "Module"]).astype(float).sum(axis=0).rename("v_core_vregfile").to_frame().T
        # print("v_core_pipeline_df\n", v_core_pipeline_df)
        # print("v_core_vregfile_df\n", v_core_vregfile_df)
        v_core_pipeline_df = v_core_pipeline_df - v_core_fpu_df.values
        # print("v_core_pipeline_df\n", v_core_pipeline_df)
        v_core_temp_df = pd.concat([v_core_pipeline_df, v_core_fpu_df, v_core_vregfile_df]).sum(axis=0).rename("v_core").to_frame().T
        # print("v_core_temp_df\n", v_core_temp_df)
        # print("v_core_df\n", v_core_df)
        v_core_misc_df = v_core_df - v_core_temp_df
        v_core_misc_df.rename(index={"v_core": "v_core_misc"}, inplace=True)
        # print("v_core_misc_df\n", v_core_misc_df)
        # input(">")
        dfs += [v_core_pipeline_df, v_core_fpu_df, v_core_vregfile_df, v_core_misc_df]
    agg_df = pd.concat(dfs)
    agg_df = agg_df.astype("int")
    agg_df.index.rename("Unit", inplace=True)
    df = agg_df
else:
    assert args.agg_mode == "none"

if out_file is None:
    with pd.option_context('display.max_rows', None, 'display.max_columns', None, 'display.width', 1000):
        print(df)
else:
    df.to_csv(out_file)
