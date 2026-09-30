# DelayRay Data Dictionary

## 1. Projects Table (`projects`)
| Column Name | Data Type | Nullable | Description |
|---|---|---|---|
| `project_id` | VARCHAR(100) | No | Unique identifier for central sector project |
| `project_name` | VARCHAR(255) | No | Project title (fictional names for synthetic data) |
| `ministry` | VARCHAR(150) | No | Sponsoring central ministry (e.g. Ministry of Railways) |
| `sector` | VARCHAR(100) | No | Infrastructure sector (e.g. Railways, Highways, Power) |
| `sub_sector` | VARCHAR(100) | Yes | Granular infrastructure classification |
| `primary_state` | VARCHAR(100) | No | Primary state/UT hosting the project alignment |
| `implementing_agency` | VARCHAR(150) | No | PSU / Agency executing the work (e.g. NHAI, RVNL) |
| `agency_type` | VARCHAR(50) | No | `central_psu`, `state_agency`, `private_epc`, `spv` |
| `sanction_date` | VARCHAR(20) | No | Date of formal sanction (YYYY-MM-DD) |
| `start_date` | VARCHAR(20) | No | Ground execution start date (YYYY-MM-DD) |
| `original_cost_cr` | FLOAT | No | Sanctioned cost in ₹ Crore (>= ₹150 Cr) |
| `original_completion_date` | VARCHAR(20) | No | Initial approved completion date (YYYY-MM-DD) |
| `planned_duration_months` | FLOAT | No | Original planned execution duration |
| `funding_mode` | VARCHAR(50) | No | Contract/financing structure (EPC, HAM, BOT, budgetary) |
| `status` | VARCHAR(50) | No | `ongoing` or `completed` |
| `data_source` | VARCHAR(50) | No | `synthetic` or `real` |

## 2. Monthly Snapshots Table (`project_snapshots`)
| Column Name | Data Type | Nullable | Description |
|---|---|---|---|
| `project_id` | VARCHAR(100) | No | Foreign key referencing projects.project_id |
| `month` | VARCHAR(7) | No | Reporting period (YYYY-MM) |
| `cumulative_expenditure_cr` | FLOAT | No | Financial expenditure incurred to date |
| `physical_progress_pct` | FLOAT | No | Reported physical execution percentage |
| `planned_progress_pct` | FLOAT | No | S-curve baseline expected percentage |
| `milestones_planned_to_date` | INT | No | Milestones targeted by this month |
| `milestones_achieved_to_date` | INT | No | Milestones physically accomplished |
| `anticipated_completion_date` | VARCHAR(20) | Yes | Contractor/agency updated completion forecast |
| `cost_revised_to_date_cr` | FLOAT | Yes | Revised cost if officially approved prior to month |
| `revision_count_to_date` | INT | No | Count of formal scope/cost revisions |
| `reporting_lag_days` | INT | No | Delay between measurement and portal upload |
| `remarks` | TEXT | Yes | Monthly engineer field notes and impediment descriptions |
