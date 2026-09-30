# CUF Column Mappings & Candidate Data Schema

## Standard Common Uniform Format (CUF) Fields
- `project_id`: Unique identifier for the infrastructure project
- `project_name`: Name of the project (fictional for synthetic data)
- `ministry`: Central government ministry
- `sector`: Infrastructure sector (Railways, Roads, Power, etc.)
- `sub_sector`: Granular sub-category
- `primary_state`: Primary execution state/UT
- `secondary_states`: Multi-state coverage list
- `implementing_agency`: PSU, authority, or SPV executing the project
- `agency_type`: central_psu | state_agency | private_epc | spv
- `sanction_date`: Cabinet / ministry approval date
- `start_date`: Actual ground execution commencement date
- `original_cost_cr`: Sanctioned cost in ₹ Crore (>= 150 Cr)
- `original_completion_date`: Initial target commissioning date
- `planned_duration_months`: Calculated baseline schedule
- `funding_mode`: EPC | BOT | HAM | Central Budgetary Support | Multilateral

## Monthly Monitoring Snapshot Fields
- `month`: Snapshot reporting month (YYYY-MM)
- `cumulative_expenditure_cr`: Cumulative financial expenditure incurred
- `physical_progress_pct`: Validated physical progress percentage (0 - 100)
- `planned_progress_pct`: S-curve baseline target percentage (0 - 100)
- `milestones_planned_to_date`: Count of milestones scheduled by snapshot
- `milestones_achieved_to_date`: Count of milestones completed by snapshot
- `anticipated_completion_date`: Implementing agency's forecast date
- `cost_revised_to_date_cr`: Approved revised cost *only if approved prior to snapshot*
- `revision_count_to_date`: Number of formal sanction revisions
- `reporting_lag_days`: Delay between physical measurement and portal upload
- `remarks`: Free-text field containing progress status, impediments, and explanations
