"""
PythonDBAGraphs: Graphs to help with Oracle Database Tuning
Copyright (C) 2016  Robert Taft Durrett (Bobby Durrett)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

Contact:

bobby@bobbydurrettdba.com

sqlstatwithplans.py

Graph execution time by plan.

"""

import myplot
import util

def sqlstatwithplans(sql_id):
    q_string = """
select 
sn.END_INTERVAL_TIME,
plan_hash_value,
ELAPSED_TIME_DELTA/(executions_delta*1000000) ELAPSED_AVG_SEC
from DBA_HIST_SQLSTAT ss,DBA_HIST_SNAPSHOT sn
where ss.sql_id = '""" 
    q_string += sql_id
    q_string += """'
and ss.snap_id=sn.snap_id
and executions_delta > 0
and ss.INSTANCE_NUMBER=sn.INSTANCE_NUMBER
order by ss.snap_id,ss.sql_id,plan_hash_value"""
    return q_string

database,dbconnection = util.script_startup('Graph execution time by plan')

# Get user input

sql_id=util.input_with_default('SQL_ID','dkqs29nsj23jq')

mainquery = sqlstatwithplans(sql_id)

mainresults = dbconnection.run_return_flipped_results(mainquery)

util.exit_no_results(mainresults)

date_times = mainresults[0]
plan_hash_values = mainresults[1]
elapsed_times = mainresults[2]
num_rows = len(date_times)

"""

There are multiple rows for a given date and time.
Build list of distinct date times and build a list of
the same length for each plan. Initialize plan lists
with 0.0. Later we will loop through every row updating
the entrees for a given plan and date.

"""

# build list of distinct plan hash values

distinct_plans = []
for phv in plan_hash_values:
    string_phv = str(phv)
    if string_phv not in distinct_plans:
        distinct_plans.append(string_phv)

# build list of distinct date times

distinct_date_times = []
for dt in date_times:
    if dt not in distinct_date_times:
        distinct_date_times.append(dt)
          
# create list with empty list for each plan    
                        
elapsed_by_plan = []
for p in distinct_plans:
    elapsed_by_plan.append([])

# insert zeros for len(distinct_date_times) entries for each
# plan's list.

for ddt in distinct_date_times:
    for elist in elapsed_by_plan:
        elist.append(0.0)
    
# update an entry for each row.

for i in range(num_rows):
    date_index = distinct_date_times.index(date_times[i])
    plan_num = distinct_plans.index(str(plan_hash_values[i]))
    elapsed_by_plan[plan_num][date_index] = elapsed_times[i]
            
# plot query
    
myplot.xdatetimes = distinct_date_times
myplot.ylists = elapsed_by_plan

myplot.title = "Sql_id "+sql_id+" on "+database+" database with plans"
myplot.ylabel1 = "Averaged Elapsed Seconds"
    
myplot.ylistlabels=distinct_plans

myplot.line()
