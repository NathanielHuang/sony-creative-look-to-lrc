#!/usr/bin/env python3
import argparse,json
from common import validate_samples,dump
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--adapter',required=True);ap.add_argument('--manifest',required=True);ap.add_argument('--report',required=True);a=ap.parse_args()
 result=validate_samples(a.adapter,a.manifest);dump(a.report,result);print(json.dumps({'metadata_result':result['metadata_result'],'pairs':result['pair_count'],'render_result':result['render_result']},ensure_ascii=False))
