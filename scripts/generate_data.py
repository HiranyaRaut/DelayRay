"""
DelayRay Synthetic Infrastructure Data Generator
Modelled on MoSPI PAIMANA project monitoring (1,981 ongoing projects >= ₹150 Cr,
7,500 historical completed projects, monthly & checkpoint snapshots, latent drivers,
realistic messiness, external indicators, and hidden ground-truth file).
Adheres strictly to docs/BUILD_SPEC.md Section 4.
"""

import os
import sys
import json
import math
import random
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd

# Add repository root to python path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

from backend.app.db.master_data import MINISTRIES, SECTORS, STATES, AGENCIES

RANDOM_SEED = 42
SNAPSHOT_DATE_ONGOING = date(2026, 4, 1)  # April 2026

# Realistic fictional project name fragments by sector
NAME_PREFIXES = {
    "Railways": ["Doubling of", "Third Line between", "New Broad Gauge Link", "Electrification of", "High Speed Bypass for"],
    "Road Transport & Highways": ["Four-Laning of NH-", "Six-Laning Greenfield Expressway", "Bypass Construction on NH-", "Elevated Corridor across"],
    "Thermal Power": ["Super Thermal Power Station Phase-", "Ultra Mega Power Project Unit-", "Thermal Expansion Project Stage-"],
    "Hydro Power": ["Hydroelectric Project on River", "Pumped Storage Hydel Scheme", "Run-of-River Dam Project"],
    "Power Transmission": ["765kV D/C Transmission System", "Inter-Regional Power Corridor", "Substation Augmentation at"],
    "Renewable Energy (Solar/Wind)": ["Ultra Mega Solar Park Phase-", "Wind-Solar Hybrid Facility", "Green Energy Evacuation Corridor"],
    "Petroleum Refining": ["Refinery Modernization & Expansion", "Petrochemical Complex Unit", "Desulphurization Facility at"],
    "Oil & Gas Pipelines": ["Natural Gas Trunk Pipeline", "Cross-Country Petroleum Pipeline", "City Gas Grid Expansion"],
    "Telecommunications": ["National Optical Fibre Network Package", "BharatNet 4G/5G Backhaul Phase-", "Submarine Cable Link"],
    "Civil Aviation & Airports": ["Greenfield International Airport", "Runway & Terminal Expansion at", "Air Cargo Terminal Complex"],
    "Metro Rail Transit": ["Metro Rail Phase-II Corridor", "Elevated Metro Alignment Line-", "Underground Metro Tunneling Section"],
    "Urban Infrastructure & Water": ["Smart City Bulk Water Supply", "Urban Stormwater & Drainage Scheme", "Inter-City Water Transmission"],
    "Ports & Harbours": ["Deep Water Container Berth at", "Mechanized Coal Terminal", "Port Connectivity Corridor at"],
    "Inland Waterways": ["National Waterway Multi-Modal Terminal", "Fairway Development on NW-", "Navigational Lock at"],
    "Coal Mining & Washeries": ["Opencast Mining Project", "Heavy Earthmoving Washery Unit", "Coal Evacuation Rail Spur"],
    "Steel Production": ["Hot Strip Mill Modernization", "Pellet Plant Expansion Stage-", "Blast Furnace Augmentation"],
    "Mines & Minerals": ["Bauxite Mining & Processing Facility", "Iron Ore Beneficiation Plant", "Copper Smelter Expansion"],
    "Strategic & Defence Roads/Infra": ["Strategic Border Road Alignment", "All-Weather Mountain Tunnel", "Defence Logistic Base"],
    "Atomic Energy": ["Nuclear Power Project Unit-", "Heavy Water Facility Expansion", "Nuclear Fuel Fabrication Complex"],
    "Space Technology Infrastructure": ["Launch Complex Pad-3 at", "Deep Space Tracking Terminal", "Solid Propellant Plant"],
    "Fertilizers & Chemicals": ["Urea & Ammonia Fertilizer Revival", "Specialty Chemical Synthesis Unit", "Bio-Fertilizer Complex"],
    "Irrigation & Water Resources": ["Inter-State River Linking Link", "Lift Irrigation Canal Scheme", "Barrage & Aqueduct Project"]
}

INDIAN_CITIES = [
    "Raipur", "Ranchi", "Patna", "Bhopal", "Nagpur", "Indore", "Jaipur", "Surat", "Vadodara",
    "Kanpur", "Lucknow", "Varanasi", "Prayagraj", "Guwahati", "Bhubaneswar", "Visakhapatnam",
    "Vijayawada", "Kochi", "Kozhikode", "Madurai", "Coimbatore", "Hubballi", "Mysuru", "Warangal",
    "Gwalior", "Jabalpur", "Amritsar", "Jalandhar", "Jodhpur", "Udaipur", "Agartala", "Dehradun"
]

TERRAIN_CLASSES = ["plain", "hilly", "coastal", "urban_dense"]
CLEARANCE_STATUSES = ["cleared", "pending", "delayed"]
UTILITY_COMPLEXITIES = ["low", "medium", "high", "critical"]
FUNDING_MODES = ["EPC", "HAM", "BOT (Toll)", "Central Budgetary Support", "Multilateral (ADB/JICA)"]

REMARK_TEMPLATES = {
    "land": [
        "Land handover pending for {n} villages in package {pkg}. RoW dispute ongoing with local district revenue office.",
        "Section 3D notification gazetted; physical possession awaited for {pct}% of alignment.",
        "Encroachment clearance in progress; joint demarcation survey underway with state authorities."
    ],
    "clearance": [
        "Stage-II Forest Clearance pending with Regional Empowered Committee. Tree felling permission awaited.",
        "Environmental Clearance granted with specific conditions; wildlife mitigation plan submitted to MoEFCC.",
        "Statutory clearance delayed due to coastal regulation zone (CRZ) boundary realignment."
    ],
    "utility": [
        "33kV / 132kV overhead high-tension lines require shifting across {n} spans by state power utility.",
        "Underground water and municipal sewer utility diversion pending municipal approvals.",
        "Gas transmission pipeline crossing requires safety clearances before deep excavation."
    ],
    "contractor": [
        "Contractor machinery mobilization inadequate; show-cause notice issued by project director.",
        "Primary EPC agency reported liquidity constraints; additional sub-contractors inducted to ramp up casting yard.",
        "Contractor performance satisfactory; batching plants operating at full planned throughput."
    ],
    "funds": [
        "State matching grant disbursement delayed; letter sent to state finance department.",
        "Monthly interim payment certificate no. {n} processed; contractor mobilization advance recovered.",
        "Funds release in progress under revised budget sanction allocation."
    ],
    "weather": [
        "Unseasonal heavy monsoon rainfall halted earthwork and embankment compaction.",
        "Flooding in riverbed delayed pier foundation casting; de-watering pumps deployed.",
        "Work resumed after monsoon hiatus; road sub-base restoration in progress."
    ],
    "design": [
        "Geotechnical strata investigation revealed fractured rock; pile design revised by technical consultant.",
        "Scope alteration approved for additional grade separator at major junction; revised drawings issued.",
        "Bridge superstructure structural design optimization under final review by independent proof consultant."
    ],
    "routine": [
        "Civil construction progressing smoothly as per current baseline target.",
        "Routine quality audits, cube compressive testing, and third-party inspection passed satisfactorily.",
        "Regular monitoring meeting held with district administration and executing agencies."
    ]
}

def generate_fictional_project_name(sector_name: str, index: int) -> str:
    prefixes = NAME_PREFIXES.get(sector_name, ["Infrastructure Construction Project at"])
    prefix = prefixes[index % len(prefixes)]
    city1 = INDIAN_CITIES[index % len(INDIAN_CITIES)]
    city2 = INDIAN_CITIES[(index * 7 + 3) % len(INDIAN_CITIES)]
    pkg_char = chr(65 + (index % 6))
    num = (index % 89) + 11

    if "between" in prefix or "Line" in prefix:
        return f"{prefix} {city1} - {city2} (Section {num})"
    elif "NH-" in prefix:
        return f"{prefix}{num} ({city1} Bypass to {city2} Section, Pkg {pkg_char})"
    elif "Unit" in prefix or "Phase" in prefix or "Stage" in prefix:
        return f"{prefix}{index % 5 + 1} at {city1}"
    else:
        return f"{prefix} {city1} Mega Facility (Pkg {pkg_char})"

def s_curve(t_ratio: float, k: float = 6.0, x0: float = 0.5) -> float:
    """Logistic S-curve mapping duration elapsed ratio (0.0 - 1.0) to progress (0 - 100%)."""
    t_clamped = max(0.0, min(1.0, t_ratio))
    val = 1.0 / (1.0 + math.exp(-k * (t_clamped - x0)))
    val_0 = 1.0 / (1.0 + math.exp(-k * (0.0 - x0)))
    val_1 = 1.0 / (1.0 + math.exp(-k * (1.0 - x0)))
    normalized = (val - val_0) / (val_1 - val_0)
    return round(float(normalized * 100.0), 2)

def generate_external_indicators(start_year: int = 2006, end_year: int = 2026, seed: int = 42) -> pd.DataFrame:
    """
    Generates monthly state-level rainfall anomalies and commodity price indices (steel, cement, crude)
    with AR(1) dynamics and structural shocks (e.g. 2008 global financial crisis, 2020 COVID shock).
    """
    rng = np.random.default_rng(seed)
    months = []
    curr = date(start_year, 1, 1)
    end = date(end_year, 5, 1)
    while curr < end:
        months.append(curr.strftime("%Y-%m"))
        # Add one month
        if curr.month == 12:
            curr = date(curr.year + 1, 1, 1)
        else:
            curr = date(curr.year, curr.month + 1, 1)

    records = []
    
    # Global AR(1) commodity baselines
    steel_val = 100.0
    cement_val = 100.0
    crude_val = 100.0
    
    macro_by_month = {}
    for m in months:
        yr = int(m.split("-")[0])
        # Shock factors
        covid_shock = 1.25 if yr in (2020, 2021) else 1.0
        gfc_shock = 1.15 if yr in (2008, 2009) else 1.0
        
        # AR(1) update with mean reversion
        steel_val = 0.95 * steel_val + 0.05 * (100.0 + (yr - 2006) * 3.5) + rng.normal(0, 2.5)
        cement_val = 0.94 * cement_val + 0.06 * (100.0 + (yr - 2006) * 2.8) + rng.normal(0, 2.0)
        crude_val = 0.92 * crude_val + 0.08 * (100.0 + (yr - 2006) * 4.0) + rng.normal(0, 3.5)
        
        macro_by_month[m] = {
            "steel": round(float(steel_val * covid_shock * gfc_shock), 2),
            "cement": round(float(cement_val * covid_shock), 2),
            "crude": round(float(crude_val * covid_shock), 2)
        }

    for state in STATES:
        state_name = state["name"]
        for m in months:
            month_idx = int(m.split("-")[1])
            # Seasonal monsoon rainfall anomaly (June - Sept)
            is_monsoon = month_idx in (6, 7, 8, 9)
            base_anomaly = rng.normal(0, 18.0) if is_monsoon else rng.normal(0, 8.0)
            
            records.append({
                "month": m,
                "state": state_name,
                "rainfall_anomaly_pct": round(float(base_anomaly), 2),
                "steel_price_index": macro_by_month[m]["steel"],
                "cement_price_index": macro_by_month[m]["cement"],
                "crude_oil_price_index": macro_by_month[m]["crude"]
            })

    return pd.DataFrame(records)

def generate_synthetic_dataset(
    n_completed: int = 7500,
    n_ongoing: int = 1981,
    seed: int = RANDOM_SEED
) -> Dict[str, Any]:
    """
    Main generator producing:
    - projects (static metadata)
    - project_snapshots (monthly / checkpoints)
    - project_outcomes (completed projects only)
    - project_extras (G6 variables)
    - external_indicators (G5 variables)
    - project_remarks (text + challenge tags)
    - milestones
    - hidden ground-truth file (_truth.json)
    """
    print(f"Initializing synthetic data generator with seed={seed}...")
    rng = np.random.default_rng(seed)
    py_rand = random.Random(seed)

    # Pre-generate external macro indicators
    print("Generating monthly macroeconomic and state weather indicators (2006-2026)...")
    df_external = generate_external_indicators(2006, 2026, seed=seed)

    # Master mappings
    sector_map = {s["name"]: s for s in SECTORS}
    ministry_map = {m["code"]: m["name"] for m in MINISTRIES}
    
    # 50 contractor pools with assigned latent quality effect
    contractors = [f"CONT-EPC-{i:03d}" for i in range(1, 51)]
    contractor_quality_effect = {c: float(rng.normal(0.0, 4.5)) for c in contractors}

    # Ground-truth driver coefficients to save in _truth.json
    ground_truth = {
        "metadata": {
            "seed": seed,
            "generated_at": datetime.now().isoformat(),
            "n_completed": n_completed,
            "n_ongoing": n_ongoing,
            "description": "Latent ground-truth structure for testing SHAP recovery and econometric ablation."
        },
        "coefficients": {
            "land_shortfall_x_terrain_hilly": 18.5,
            "clearance_delay_threshold_gt12m": 14.2,
            "contractor_concurrent_load_gt3": 9.8,
            "commodity_price_shock_long_duration": 12.0,
            "covid_regime_shock_2020_2021": 15.6,
            "geotech_uncertainty_weight": 0.12,
            "design_changes_weight": 2.4,
            "rainfall_monsoon_anomaly_weight": 0.08
        },
        "sector_base_delay": {s["name"]: round(float(rng.normal(3.0, 2.0)), 2) for s in SECTORS},
        "contractor_quality": contractor_quality_effect
    }

    projects: List[Dict[str, Any]] = []
    outcomes: List[Dict[str, Any]] = []
    extras: List[Dict[str, Any]] = []
    snapshots: List[Dict[str, Any]] = []
    remarks: List[Dict[str, Any]] = []
    milestones: List[Dict[str, Any]] = []

    total_projects = n_completed + n_ongoing
    print(f"Generating {total_projects} projects ({n_completed} completed, {n_ongoing} ongoing)...")

    for i in range(total_projects):
        is_completed = (i < n_completed)
        status = "completed" if is_completed else "ongoing"
        
        # Sector & Ministry
        sector_idx = i % len(SECTORS)
        sec = SECTORS[sector_idx]
        sector_name = sec["name"]
        ministry_name = ministry_map[sec["ministry_code"]]
        
        # State & Agency
        state_obj = STATES[(i * 3 + 1) % len(STATES)]
        primary_state = state_obj["name"]
        
        # Multi-state projects for linear infrastructure
        secondary_states = None
        if sector_name in ("Railways", "Road Transport & Highways", "Oil & Gas Pipelines", "Power Transmission") and (i % 3 == 0):
            sec_state_idx = (i * 3 + 5) % len(STATES)
            secondary_states = [STATES[sec_state_idx]["name"]]

        agency_obj = AGENCIES[i % len(AGENCIES)]
        agency_name = agency_obj["name"]
        agency_type = agency_obj["agency_type"]

        # Project ID & Name
        prefix_code = sec["code"].replace("SEC-", "")
        project_id = f"PRJ-{prefix_code}-{i+1:05d}"
        project_name = generate_fictional_project_name(sector_name, i)

        # Dates & Duration
        if is_completed:
            # Completed: Start years 2006 to 2022
            start_year = 2006 + (i % 17)
            start_month = (i % 12) + 1
            start_d = date(start_year, start_month, 1)
            planned_duration_months = float(py_rand.choice([24, 30, 36, 42, 48, 54, 60, 72]))
            sanction_lag = py_rand.randint(3, 12)
            sanction_d = start_d - timedelta(days=sanction_lag * 30)
            orig_comp_d = start_d + timedelta(days=int(planned_duration_months * 30.4375))
        else:
            # Ongoing: Start years 2020 to late 2025
            start_year = 2020 + (i % 6)
            start_month = (i % 12) + 1
            start_d = date(start_year, start_month, 1)
            planned_duration_months = float(py_rand.choice([30, 36, 42, 48, 60, 72, 84]))
            sanction_lag = py_rand.randint(4, 14)
            sanction_d = start_d - timedelta(days=sanction_lag * 30)
            orig_comp_d = start_d + timedelta(days=int(planned_duration_months * 30.4375))

        # Original Cost (Log-Normal, Min ₹150 Cr, heavy tail up to ~₹50,000 Cr)
        median_c = sec["median_cost"]
        # log-normal with mean log(median_c) and sigma ~0.75
        raw_cost = float(rng.lognormal(mean=math.log(median_c), sigma=0.72))
        original_cost_cr = round(max(150.0, min(52000.0, raw_cost)), 2)

        funding_mode = FUNDING_MODES[i % len(FUNDING_MODES)]

        # ----------------------------------------------------------------------
        # Project Extras (G6 non-CUF variables)
        # ----------------------------------------------------------------------
        terrain = TERRAIN_CLASSES[(i * 2) % len(TERRAIN_CLASSES)]
        clearance_status = CLEARANCE_STATUSES[(i * 5) % len(CLEARANCE_STATUSES)]
        clearance_delay = float(round(py_rand.uniform(0.0, 24.0), 1)) if clearance_status != "cleared" else 0.0
        utility_complexity = UTILITY_COMPLEXITIES[(i * 3) % len(UTILITY_COMPLEXITIES)]
        utility_count = py_rand.randint(2, 45) if utility_complexity in ("high", "critical") else py_rand.randint(0, 10)
        
        # Land acquisition shortfall at start (percentage 35% - 100%)
        land_acq_pct = round(float(rng.beta(a=7, b=2) * 100.0), 1)
        land_acq_pct = max(35.0, min(100.0, land_acq_pct))

        contractor = contractors[i % len(contractors)]
        contractor_score = round(float(rng.normal(74.0, 12.0)), 1)
        contractor_score = max(30.0, min(98.0, contractor_score))
        contractor_concurrent = int(rng.poisson(lam=2.5)) + 1
        geotech_uncertainty = round(float(py_rand.uniform(10.0, 95.0)), 1)
        design_changes = int(rng.poisson(lam=2.0))
        law_order_index = round(float(rng.normal(78.0, 10.0)), 1)
        law_order_index = max(40.0, min(99.0, law_order_index))

        extras.append({
            "project_id": project_id,
            "land_acquisition_pct_at_start": land_acq_pct,
            "env_forest_clearance_status": clearance_status,
            "env_forest_clearance_delay_months": clearance_delay,
            "utility_shifting_complexity": utility_complexity,
            "utility_shifting_count": utility_count,
            "terrain_class": terrain,
            "contractor_id": contractor,
            "contractor_performance_score": contractor_score,
            "contractor_concurrent_projects": contractor_concurrent,
            "geotechnical_uncertainty_score": geotech_uncertainty,
            "design_changes_count": design_changes,
            "local_law_order_index": law_order_index
        })

        # ----------------------------------------------------------------------
        # Latent Ground-Truth Outcome Process (Completed Projects)
        # ----------------------------------------------------------------------
        if is_completed:
            # Base sector & contractor effects
            sec_delay = ground_truth["sector_base_delay"].get(sector_name, 2.0)
            cont_effect = ground_truth["contractor_quality"].get(contractor, 0.0)

            # Non-linear Interaction 1: Land shortfall (<75%) x Difficult terrain (hilly/urban_dense)
            land_deficit = max(0.0, 80.0 - land_acq_pct) / 20.0
            terrain_mult = 1.8 if terrain in ("hilly", "urban_dense") else 0.7
            delay_land_terrain = land_deficit * terrain_mult * ground_truth["coefficients"]["land_shortfall_x_terrain_hilly"] * 0.4

            # Non-linear Interaction 2: Clearance delay threshold (> 12 months)
            delay_clearance = 0.0
            if clearance_delay > 12.0:
                delay_clearance = ground_truth["coefficients"]["clearance_delay_threshold_gt12m"] * ((clearance_delay - 12.0) / 6.0)

            # Non-linear Interaction 3: Contractor concurrency overload (> 3 concurrent projects)
            delay_concurrency = 0.0
            if contractor_concurrent > 3:
                delay_concurrency = ground_truth["coefficients"]["contractor_concurrent_load_gt3"] * (contractor_concurrent - 3) * 0.6

            # Non-linear Interaction 4: COVID-19 Pandemic shock if project active during 2020-2021
            proj_end_baseline = start_d + timedelta(days=int(planned_duration_months * 30.4375))
            hit_covid = not (orig_comp_d.year < 2020 or start_d.year > 2021)
            delay_covid = ground_truth["coefficients"]["covid_regime_shock_2020_2021"] * float(rng.uniform(0.7, 1.3)) if hit_covid else 0.0

            # Heavy-tailed noise (Student-t with df=3)
            noise_delay = float(rng.standard_t(df=3) * 4.5)

            # Total delay months
            total_delay = (
                sec_delay
                - cont_effect * 0.4
                + delay_land_terrain
                + delay_clearance
                + delay_concurrency
                + delay_covid
                + (geotech_uncertainty * 0.06)
                + (design_changes * 1.5)
                + noise_delay
            )
            time_overrun_months = round(max(0.0, float(total_delay)), 1)
            actual_comp_d = orig_comp_d + timedelta(days=int(time_overrun_months * 30.4375))

            # Cost overrun % process (correlated with delay + commodity shock + design changes)
            cost_overrun_pct = (
                0.45 * time_overrun_months
                + (design_changes * 3.2)
                + float(rng.normal(2.0, 6.0))
            )
            cost_overrun_pct = round(max(0.0, float(cost_overrun_pct)), 2)
            final_cost_cr = round(original_cost_cr * (1.0 + cost_overrun_pct / 100.0), 2)
            
            # High risk flag: cost overrun > 10% OR time overrun > 12 months
            high_risk = bool(cost_overrun_pct > 10.0 or time_overrun_months > 12.0)

            outcomes.append({
                "project_id": project_id,
                "final_cost_cr": final_cost_cr,
                "actual_completion_date": actual_comp_d.strftime("%Y-%m-%d"),
                "cost_overrun_pct": cost_overrun_pct,
                "time_overrun_months": time_overrun_months,
                "high_risk_flag": high_risk
            })

        # ----------------------------------------------------------------------
        # Realistic Messiness in Projects
        # ----------------------------------------------------------------------
        # Sub-sector missing in 10% of rows
        sub_sector = f"{sector_name} Package"
        if py_rand.random() < 0.10:
            sub_sector = None

        projects.append({
            "project_id": project_id,
            "project_name": project_name,
            "ministry": ministry_name,
            "sector": sector_name,
            "sub_sector": sub_sector,
            "primary_state": primary_state,
            "secondary_states": secondary_states,
            "implementing_agency": agency_name,
            "agency_type": agency_type,
            "sanction_date": sanction_d.strftime("%Y-%m-%d"),
            "start_date": start_d.strftime("%Y-%m-%d"),
            "original_cost_cr": original_cost_cr,
            "original_completion_date": orig_comp_d.strftime("%Y-%m-%d"),
            "planned_duration_months": planned_duration_months,
            "funding_mode": funding_mode,
            "status": status,
            "data_source": "synthetic"
        })

        # ----------------------------------------------------------------------
        # Generate Snapshots
        # Ongoing: Monthly from start to April 2026
        # Completed: Checkpoints at 25%, 50%, 75% of planned duration
        # ----------------------------------------------------------------------
        if is_completed:
            # 3 checkpoints: 25%, 50%, 75% of planned duration
            checkpoint_ratios = [0.25, 0.50, 0.75]
            for ratio in checkpoint_ratios:
                elapsed_months = int(planned_duration_months * ratio)
                # Snapshot date
                snap_d = start_d + timedelta(days=int(elapsed_months * 30.4375))
                month_str = snap_d.strftime("%Y-%m")
                
                # Planned progress from S-curve
                planned_prog = s_curve(ratio)
                
                # Physical progress lags based on eventual outcome
                perf_penalty = min(0.35, (time_overrun_months / (planned_duration_months + 1e-3)) * 0.4)
                actual_ratio = max(0.05, ratio * (1.0 - perf_penalty) + rng.normal(0, 0.03))
                physical_prog = round(min(99.0, s_curve(actual_ratio)), 2)
                
                # Cumulative expenditure
                expenditure_prog = physical_prog * (1.0 + (cost_overrun_pct / 100.0) * 0.5) + rng.normal(0, 2.0)
                expenditure_prog = max(0.0, min(150.0, expenditure_prog))
                cumulative_exp = round((expenditure_prog / 100.0) * original_cost_cr, 2)

                # Revisions
                rev_count = 1 if (ratio >= 0.5 and cost_overrun_pct > 15.0) else 0
                cost_rev = round(original_cost_cr * 1.15, 2) if rev_count > 0 else None

                # Milestones
                ms_planned = max(1, int(10 * ratio))
                ms_achieved = max(0, int(ms_planned * (physical_prog / max(1.0, planned_prog))))

                # Reporting lag (5-15% missingness / mess)
                rep_lag = int(rng.exponential(scale=14.0)) + 3
                if py_rand.random() < 0.05:  # 5% extreme lag outlier
                    rep_lag += py_rand.randint(45, 90)

                # Remarks generator
                remark_topic = "routine"
                tags = []
                if physical_prog < planned_prog - 8.0:
                    topic_candidates = ["land", "clearance", "utility", "contractor", "funds", "weather", "design"]
                    remark_topic = py_rand.choice(topic_candidates)
                    tags = [remark_topic]
                
                tpl = py_rand.choice(REMARK_TEMPLATES[remark_topic])
                remark_text = tpl.format(
                    n=py_rand.randint(2, 6),
                    pkg=chr(65 + (i % 4)),
                    pct=py_rand.randint(15, 45)
                )

                snapshots.append({
                    "project_id": project_id,
                    "month": month_str,
                    "cumulative_expenditure_cr": cumulative_exp,
                    "physical_progress_pct": physical_prog,
                    "planned_progress_pct": planned_prog,
                    "milestones_planned_to_date": ms_planned,
                    "milestones_achieved_to_date": ms_achieved,
                    "anticipated_completion_date": (orig_comp_d + timedelta(days=int(time_overrun_months * 0.5 * 30))).strftime("%Y-%m-%d"),
                    "cost_revised_to_date_cr": cost_rev,
                    "revision_count_to_date": rev_count,
                    "reporting_lag_days": rep_lag,
                    "remarks": remark_text
                })

                remarks.append({
                    "project_id": project_id,
                    "month": month_str,
                    "remark_text": remark_text,
                    "extracted_tags": tags,
                    "tag_confidence": 0.88 if tags else 0.0
                })
        else:
            # Ongoing project: Monthly snapshots from start date to April 2026
            curr_month_d = date(start_d.year, start_d.month, 1)
            m_count = 0
            
            # Latent drift trend for ongoing project
            ongoing_drag = float(rng.uniform(0.70, 1.15))
            if land_acq_pct < 65.0:
                ongoing_drag *= 0.82
            if clearance_status == "delayed":
                ongoing_drag *= 0.85
            if contractor_concurrent > 3:
                ongoing_drag *= 0.90

            while curr_month_d <= SNAPSHOT_DATE_ONGOING:
                m_count += 1
                month_str = curr_month_d.strftime("%Y-%m")
                total_months_elapsed = m_count
                t_ratio = total_months_elapsed / max(1.0, planned_duration_months)
                
                planned_prog = s_curve(t_ratio)
                actual_ratio = max(0.01, t_ratio * ongoing_drag + rng.normal(0, 0.015))
                physical_prog = round(min(98.0, s_curve(actual_ratio)), 2)
                
                spend_ratio = (physical_prog / 100.0) * float(rng.uniform(0.95, 1.25))
                cumulative_exp = round(min(original_cost_cr * 1.5, spend_ratio * original_cost_cr), 2)

                rev_count = 1 if (m_count > 24 and physical_prog < planned_prog - 15.0) else 0
                cost_rev = round(original_cost_cr * 1.20, 2) if rev_count > 0 else None

                ms_planned = max(1, int(12 * min(1.0, t_ratio)))
                ms_achieved = max(0, int(ms_planned * (physical_prog / max(1.0, planned_prog))))

                rep_lag = int(rng.exponential(scale=12.0)) + 2

                # Select topic for remark
                tags = []
                if physical_prog < planned_prog - 7.0:
                    topic = py_rand.choice(["land", "clearance", "utility", "contractor", "funds", "weather", "design"])
                    tags = [topic]
                else:
                    topic = "routine"

                tpl = py_rand.choice(REMARK_TEMPLATES[topic])
                remark_text = tpl.format(
                    n=py_rand.randint(1, 5),
                    pkg=chr(65 + (i % 4)),
                    pct=py_rand.randint(20, 60)
                )

                # Realistic mess: 8% missingness in remarks, 6% missingness in anticipated_completion_date
                if py_rand.random() < 0.08:
                    remark_text = None
                
                ant_comp = None
                if py_rand.random() >= 0.06:
                    delay_proj = max(0, int((planned_prog - physical_prog) * 1.2))
                    ant_comp = (orig_comp_d + timedelta(days=delay_proj * 30)).strftime("%Y-%m-%d")

                snapshots.append({
                    "project_id": project_id,
                    "month": month_str,
                    "cumulative_expenditure_cr": cumulative_exp,
                    "physical_progress_pct": physical_prog,
                    "planned_progress_pct": planned_prog,
                    "milestones_planned_to_date": ms_planned,
                    "milestones_achieved_to_date": ms_achieved,
                    "anticipated_completion_date": ant_comp,
                    "cost_revised_to_date_cr": cost_rev,
                    "revision_count_to_date": rev_count,
                    "reporting_lag_days": rep_lag,
                    "remarks": remark_text
                })

                if remark_text:
                    remarks.append({
                        "project_id": project_id,
                        "month": month_str,
                        "remark_text": remark_text,
                        "extracted_tags": tags,
                        "tag_confidence": 0.85 if tags else 0.0
                    })

                # Advance month
                if curr_month_d.month == 12:
                    curr_month_d = date(curr_month_d.year + 1, 1, 1)
                else:
                    curr_month_d = date(curr_month_d.year, curr_month_d.month + 1, 1)

        # Generate 4-6 key milestones per project
        n_ms = py_rand.randint(4, 6)
        for ms_idx in range(n_ms):
            ms_ratio = (ms_idx + 1) / (n_ms + 1)
            ms_planned_d = start_d + timedelta(days=int(planned_duration_months * ms_ratio * 30.4375))
            
            ms_achieved_d = None
            ms_status = "pending"
            if is_completed:
                ms_status = "achieved"
                slip_days = py_rand.randint(-15, 120)
                ms_achieved_d = (ms_planned_d + timedelta(days=slip_days)).strftime("%Y-%m-%d")
            else:
                if ms_planned_d < SNAPSHOT_DATE_ONGOING:
                    if py_rand.random() < 0.75:
                        ms_status = "achieved"
                        ms_achieved_d = (ms_planned_d + timedelta(days=py_rand.randint(-10, 60))).strftime("%Y-%m-%d")
                    else:
                        ms_status = "missed"

            milestones.append({
                "project_id": project_id,
                "milestone_name": f"Milestone {ms_idx+1}: Key Civil Package {chr(65+ms_idx)} Completion",
                "planned_date": ms_planned_d.strftime("%Y-%m-%d"),
                "achieved_date": ms_achieved_d,
                "status": ms_status
            })

    # Convert to DataFrames
    print("Formatting DataFrames...")
    df_projects = pd.DataFrame(projects)
    df_outcomes = pd.DataFrame(outcomes)
    df_extras = pd.DataFrame(extras)
    df_snapshots = pd.DataFrame(snapshots)
    df_remarks = pd.DataFrame(remarks)
    df_milestones = pd.DataFrame(milestones)

    # Save to data/synthetic
    out_dir = os.path.join(ROOT_DIR, "data", "synthetic")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Exporting synthetic datasets to {out_dir}...")
    df_projects.to_csv(os.path.join(out_dir, "projects.csv"), index=False)
    df_outcomes.to_csv(os.path.join(out_dir, "project_outcomes.csv"), index=False)
    df_extras.to_csv(os.path.join(out_dir, "project_extras.csv"), index=False)
    df_snapshots.to_csv(os.path.join(out_dir, "project_snapshots.csv"), index=False)
    df_remarks.to_csv(os.path.join(out_dir, "project_remarks.csv"), index=False)
    df_milestones.to_csv(os.path.join(out_dir, "milestones.csv"), index=False)
    df_external.to_csv(os.path.join(out_dir, "external_indicators.csv"), index=False)

    # Save hidden _truth.json for validation testing only
    truth_path = os.path.join(out_dir, "_truth.json")
    with open(truth_path, "w", encoding="utf-8") as f:
        json.dump(ground_truth, f, indent=2)

    stats = {
        "projects_count": len(df_projects),
        "completed_projects": len(df_projects[df_projects["status"] == "completed"]),
        "ongoing_projects": len(df_projects[df_projects["status"] == "ongoing"]),
        "snapshots_count": len(df_snapshots),
        "outcomes_count": len(df_outcomes),
        "extras_count": len(df_extras),
        "remarks_count": len(df_remarks),
        "milestones_count": len(df_milestones),
        "external_indicators_count": len(df_external),
        "missingness": {
            "sub_sector_pct": round(float(df_projects["sub_sector"].isna().mean() * 100), 2),
            "snapshots_remarks_pct": round(float(df_snapshots["remarks"].isna().mean() * 100), 2),
            "snapshots_anticipated_date_pct": round(float(df_snapshots["anticipated_completion_date"].isna().mean() * 100), 2),
            "snapshots_cost_revised_pct": round(float(df_snapshots["cost_revised_to_date_cr"].isna().mean() * 100), 2),
        },
        "cost_overrun_stats": {
            "mean_pct": round(float(df_outcomes["cost_overrun_pct"].mean()), 2),
            "median_pct": round(float(df_outcomes["cost_overrun_pct"].median()), 2),
            "max_pct": round(float(df_outcomes["cost_overrun_pct"].max()), 2),
            "high_risk_ratio": round(float(df_outcomes["high_risk_flag"].mean()), 3)
        },
        "time_overrun_stats": {
            "mean_months": round(float(df_outcomes["time_overrun_months"].mean()), 1),
            "median_months": round(float(df_outcomes["time_overrun_months"].median()), 1),
            "max_months": round(float(df_outcomes["time_overrun_months"].max()), 1)
        }
    }

    print("Synthetic data generation finished successfully!")
    return stats

def main():
    stats = generate_synthetic_dataset(n_completed=7500, n_ongoing=1981, seed=RANDOM_SEED)
    print("\n--- Synthetic Generation Summary ---")
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
