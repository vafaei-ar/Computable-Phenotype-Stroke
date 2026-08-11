import importlib.util
from pathlib import Path
import pandas as pd

SPEC=importlib.util.spec_from_file_location("bench", Path(__file__).parents[1]/"scripts"/"run_aggregate_benchmark.py")
bench=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(bench)

def test_lin_ccc_identity():
    assert abs(bench.lin_ccc([1,2,3],[1,2,3])-1.0) < 1e-12

def test_nested_checks_clean():
    rows=[]
    for d,n in {"D5":10,"D1":8,"D2":9,"D7":7,"D3":5,"D4":6,"D6":4,"D8":3}.items():
        rows.append(["C1","2024-01",d,n,8,"1.0.0"])
    df=pd.DataFrame(rows,columns=["center_id","month","definition_id","phenotype_count","registry_count","definition_version"])
    out=bench.logical_checks(df)
    assert not out["violation"].any()
