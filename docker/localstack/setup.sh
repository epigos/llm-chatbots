#!/bin/bash
set -x
export AWS

# create s3 buckets
awslocal s3 mb s3://uploads

awslocal s3api put-bucket-cors --bucket uploads --cors-configuration '{"CORSRules" : [{"AllowedHeaders":["*"],"AllowedMethods":["GET","PUT","POST"],"AllowedOrigins":["*"],"ExposeHeaders":[]}]}'

set +x
