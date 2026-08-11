#!/usr/bin/env python3
import sys, pandas as pd
REQ=['center_id','month','definition_id','phenotype_count','registry_count','definition_version']
ALLOWED={f'D{i}' for i in range(9)}
def main(p):
    df=pd.read_csv(p); errors=[]
    miss=[c for c in REQ if c not in df]
    if miss: errors.append(f'Missing required columns: {miss}')
    if not miss:
        if df[REQ].isna().any().any(): errors.append('Required fields contain missing values.')
        if (df[['phenotype_count','registry_count']]<0).any().any(): errors.append('Counts must be nonnegative.')
        bad=set(df.definition_id)-ALLOWED
        if bad: errors.append(f'Unexpected definition IDs: {sorted(bad)}')
        dup=df.duplicated(['center_id','month','definition_id'])
        if dup.any(): errors.append(f'Duplicate center-month-definition rows: {int(dup.sum())}')
    if errors:
        print('\n'.join('ERROR: '+x for x in errors)); raise SystemExit(1)
    print(f'OK: {len(df):,} rows; {df.center_id.nunique()} centers; {df.month.nunique()} distinct months.')
if __name__=='__main__':
    if len(sys.argv)!=2: raise SystemExit('Usage: validate_input.py <aggregate_counts.csv>')
    main(sys.argv[1])
