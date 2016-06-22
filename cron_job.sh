#!/bin/bash

# Copyright 2016 Peter Dymkar Brandt All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

# Run market_report scripts for today. Constants hard-coded due to short
# length.
today=`/bin/date +%Y%m%d`  # YYYYMMDD today.

portfolio_start_date="20160101"
portfolio_cmd="./main.py --config_file portfolio_config_local.yaml
  --output_dir portfolio_data/${today}/
  --start_date ${portfolio_start_date}
  --end_date ${today}"

universe_start_date=`/bin/date --date="8 weeks ago" +%Y%m%d`  # YYYYMMDD 8 weeks ago.
universe_cmd="./main.py --config_file universe_config_local.yaml
  --output_dir universe_data/${today}/
  --start_date ${universe_start_date}
  --end_date ${today}"

eval "export PYTHONPATH=/home/ubuntu/devel"
eval "cd /home/ubuntu/devel/market_report"

eval_with_retry() {
  counter=0
  while [ $counter -lt 5 ]; do  # Max 5 retries.
    let counter=counter+1
    echo "Attempt: ${counter}"
    echo $1
    eval $1
    if [ $? -eq 0 ]; then
      break
    fi

    eval "pkill tor"  # Kill any existing TOR processes.
    sleep 10
  done
}

eval_with_retry "$portfolio_cmd"
eval_with_retry "$universe_cmd"
