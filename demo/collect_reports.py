import re
from pathlib import Path

import pandas as pd

data = []

p = Path("reports")
for child in p.glob('**/*'):
    if child.is_file():
        filename = child.name
        if filename == "utilization_report.rpt.csv":
            temp = str(child.parent).lstrip(f"{p}/")
            assert temp.count("/") == 4
            keys = ["Board", "Vicuna Version", "Core", "Config", "Arch"]
            values = temp.split("/")
            attrs = dict(zip(keys, values))
            # print("filename", filename)
            # print("attrs", attrs)
            df = pd.read_csv(child)
            # print("df", df)
            # df.index.rename("Module", inplace=True)
            df.rename(columns={"Unit": "Module"}, inplace=True)
            df = df.reset_index()
            # print("df", df)
            child_ = child.parent / "get_max_clk.log"
            assert child_.is_file()
            with open(child_, "r") as f:
                content = f.read()
            # print("content", content)
            matches = re.compile(r"Max.\sfrequency:\s+(\d+\.\d+)\s+MHz").findall(content)
            # print("matches", matches)
            if len(matches) == 0:
                # fallback
                matches = re.compile(r"\[PASS\]\s(\d+\.\d+)\sMHz\s\(WNS:\s(\d+\.\d+)\)").findall(content)
                # matches = re.compile(r"\[PASS\]\s(\d+\.\d+)\sMHz").findall(content)
                assert len(matches) > 0
                clk_mhz, wns_ns = matches[-1]
                clk_mhz = float(clk_mhz)
                # wns_ns = float(wns_ns)
                # print("matches", matches)
                # input(">>")
            else:
                assert len(matches) == 1
                clk_mhz = float(matches[0])

            # print("clk_mhz", clk_mhz)
            # input(">")
            attrs["Clock [MHz]"] = clk_mhz
            data_ = [{**attrs, **x} for x in  df.to_dict(orient="records")]
            data.extend(data_)


print(data, len(data))
