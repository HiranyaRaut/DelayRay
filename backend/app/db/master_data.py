"""
DelayRay Master Data Catalog
Defines 17 Ministries, 22 Infrastructure Sectors, 36 States/UTs, and ~60 Implementing Agencies.
"""

from typing import List, Dict, Any

MINISTRIES: List[Dict[str, str]] = [
    {"code": "MOR", "name": "Ministry of Railways"},
    {"code": "MORTH", "name": "Ministry of Road Transport and Highways"},
    {"code": "MOP", "name": "Ministry of Power"},
    {"code": "MOPNG", "name": "Ministry of Petroleum and Natural Gas"},
    {"code": "MOT", "name": "Ministry of Communications (Telecommunications)"},
    {"code": "MOCA", "name": "Ministry of Civil Aviation"},
    {"code": "MOHUA", "name": "Ministry of Housing and Urban Affairs"},
    {"code": "MOSHIP", "name": "Ministry of Ports, Shipping and Waterways"},
    {"code": "MNRE", "name": "Ministry of New and Renewable Energy"},
    {"code": "MOCOAL", "name": "Ministry of Coal"},
    {"code": "MOSTEEL", "name": "Ministry of Steel"},
    {"code": "DOM", "name": "Ministry of Mines"},
    {"code": "DOD", "name": "Ministry of Defence"},
    {"code": "DAE", "name": "Department of Atomic Energy"},
    {"code": "DOS", "name": "Department of Space"},
    {"code": "MOCHEM", "name": "Ministry of Chemicals and Fertilizers"},
    {"code": "MOJS", "name": "Ministry of Jal Shakti"}
]

SECTORS: List[Dict[str, Any]] = [
    {"code": "SEC-RAIL", "name": "Railways", "ministry_code": "MOR", "median_cost": 2200.0},
    {"code": "SEC-ROADS", "name": "Road Transport & Highways", "ministry_code": "MORTH", "median_cost": 1450.0},
    {"code": "SEC-POWER-TH", "name": "Thermal Power", "ministry_code": "MOP", "median_cost": 5500.0},
    {"code": "SEC-POWER-HY", "name": "Hydro Power", "ministry_code": "MOP", "median_cost": 4200.0},
    {"code": "SEC-POWER-TR", "name": "Power Transmission", "ministry_code": "MOP", "median_cost": 1200.0},
    {"code": "SEC-RENEW", "name": "Renewable Energy (Solar/Wind)", "ministry_code": "MNRE", "median_cost": 950.0},
    {"code": "SEC-PETRO-REF", "name": "Petroleum Refining", "ministry_code": "MOPNG", "median_cost": 8500.0},
    {"code": "SEC-PETRO-PIPE", "name": "Oil & Gas Pipelines", "ministry_code": "MOPNG", "median_cost": 2800.0},
    {"code": "SEC-TELECOM", "name": "Telecommunications", "ministry_code": "MOT", "median_cost": 1600.0},
    {"code": "SEC-AVIATION", "name": "Civil Aviation & Airports", "ministry_code": "MOCA", "median_cost": 2100.0},
    {"code": "SEC-METRO", "name": "Metro Rail Transit", "ministry_code": "MOHUA", "median_cost": 7200.0},
    {"code": "SEC-URBAN-INF", "name": "Urban Infrastructure & Water", "ministry_code": "MOHUA", "median_cost": 650.0},
    {"code": "SEC-PORTS", "name": "Ports & Harbours", "ministry_code": "MOSHIP", "median_cost": 1800.0},
    {"code": "SEC-SHIPPING", "name": "Inland Waterways", "ministry_code": "MOSHIP", "median_cost": 450.0},
    {"code": "SEC-COAL", "name": "Coal Mining & Washeries", "ministry_code": "MOCOAL", "median_cost": 3100.0},
    {"code": "SEC-STEEL", "name": "Steel Production", "ministry_code": "MOSTEEL", "median_cost": 4800.0},
    {"code": "SEC-MINES", "name": "Mines & Minerals", "ministry_code": "DOM", "median_cost": 1900.0},
    {"code": "SEC-DEFENCE", "name": "Strategic & Defence Roads/Infra", "ministry_code": "DOD", "median_cost": 1500.0},
    {"code": "SEC-ATOMIC", "name": "Atomic Energy", "ministry_code": "DAE", "median_cost": 12500.0},
    {"code": "SEC-SPACE", "name": "Space Technology Infrastructure", "ministry_code": "DOS", "median_cost": 850.0},
    {"code": "SEC-FERT", "name": "Fertilizers & Chemicals", "ministry_code": "MOCHEM", "median_cost": 3800.0},
    {"code": "SEC-WATER", "name": "Irrigation & Water Resources", "ministry_code": "MOJS", "median_cost": 2400.0}
]

STATES: List[Dict[str, str]] = [
    {"code": "AP", "name": "Andhra Pradesh", "region": "South"},
    {"code": "AR", "name": "Arunachal Pradesh", "region": "North-East"},
    {"code": "AS", "name": "Assam", "region": "North-East"},
    {"code": "BR", "name": "Bihar", "region": "East"},
    {"code": "CG", "name": "Chhattisgarh", "region": "Central"},
    {"code": "GA", "name": "Goa", "region": "West"},
    {"code": "GJ", "name": "Gujarat", "region": "West"},
    {"code": "HR", "name": "Haryana", "region": "North"},
    {"code": "HP", "name": "Himachal Pradesh", "region": "North"},
    {"code": "JH", "name": "Jharkhand", "region": "East"},
    {"code": "KA", "name": "Karnataka", "region": "South"},
    {"code": "KL", "name": "Kerala", "region": "South"},
    {"code": "MP", "name": "Madhya Pradesh", "region": "Central"},
    {"code": "MH", "name": "Maharashtra", "region": "West"},
    {"code": "MN", "name": "Manipur", "region": "North-East"},
    {"code": "ML", "name": "Meghalaya", "region": "North-East"},
    {"code": "MZ", "name": "Mizoram", "region": "North-East"},
    {"code": "NL", "name": "Nagaland", "region": "North-East"},
    {"code": "OD", "name": "Odisha", "region": "East"},
    {"code": "PB", "name": "Punjab", "region": "North"},
    {"code": "RJ", "name": "Rajasthan", "region": "North"},
    {"code": "SK", "name": "Sikkim", "region": "North-East"},
    {"code": "TN", "name": "Tamil Nadu", "region": "South"},
    {"code": "TS", "name": "Telangana", "region": "South"},
    {"code": "TR", "name": "Tripura", "region": "North-East"},
    {"code": "UP", "name": "Uttar Pradesh", "region": "North"},
    {"code": "UK", "name": "Uttarakhand", "region": "North"},
    {"code": "WB", "name": "West Bengal", "region": "East"},
    {"code": "AN", "name": "Andaman & Nicobar", "region": "South"},
    {"code": "CH", "name": "Chandigarh", "region": "North"},
    {"code": "DN", "name": "Dadra & Nagar Haveli and Daman & Diu", "region": "West"},
    {"code": "DL", "name": "Delhi", "region": "North"},
    {"code": "JK", "name": "Jammu & Kashmir", "region": "North"},
    {"code": "LA", "name": "Ladakh", "region": "North"},
    {"code": "LD", "name": "Lakshadweep", "region": "South"},
    {"code": "PY", "name": "Puducherry", "region": "South"}
]

AGENCIES: List[Dict[str, str]] = [
    # Central PSUs (Railways & Transport)
    {"code": "AG-RVNL", "name": "Rail Vikas Nigam Limited", "agency_type": "central_psu"},
    {"code": "AG-IRCON", "name": "Ircon International Limited", "agency_type": "central_psu"},
    {"code": "AG-DFCCIL", "name": "Dedicated Freight Corridor Corp", "agency_type": "central_psu"},
    {"code": "AG-NHAI", "name": "National Highways Authority of India", "agency_type": "central_psu"},
    {"code": "AG-NHIDCL", "name": "National Highways & Infra Dev Corp", "agency_type": "central_psu"},
    {"code": "AG-KRCL", "name": "Konkan Railway Corporation", "agency_type": "central_psu"},
    {"code": "AG-MRVC", "name": "Mumbai Railway Vikas Corporation", "agency_type": "central_psu"},
    {"code": "AG-RLDA", "name": "Rail Land Development Authority", "agency_type": "central_psu"},

    # Energy & Mining PSUs
    {"code": "AG-NTPC", "name": "NTPC Limited", "agency_type": "central_psu"},
    {"code": "AG-NHPC", "name": "NHPC Limited", "agency_type": "central_psu"},
    {"code": "AG-PGCIL", "name": "Power Grid Corporation of India", "agency_type": "central_psu"},
    {"code": "AG-SJVN", "name": "SJVN Limited", "agency_type": "central_psu"},
    {"code": "AG-THDC", "name": "THDC India Limited", "agency_type": "central_psu"},
    {"code": "AG-ONGC", "name": "Oil & Natural Gas Corporation", "agency_type": "central_psu"},
    {"code": "AG-IOCL", "name": "Indian Oil Corporation Limited", "agency_type": "central_psu"},
    {"code": "AG-BPCL", "name": "Bharat Petroleum Corporation Limited", "agency_type": "central_psu"},
    {"code": "AG-GAIL", "name": "GAIL (India) Limited", "agency_type": "central_psu"},
    {"code": "AG-OIL", "name": "Oil India Limited", "agency_type": "central_psu"},
    {"code": "AG-CIL", "name": "Coal India Limited", "agency_type": "central_psu"},
    {"code": "AG-SAIL", "name": "Steel Authority of India Limited", "agency_type": "central_psu"},
    {"code": "AG-NMDC", "name": "NMDC Limited", "agency_type": "central_psu"},
    {"code": "AG-NPCIL", "name": "Nuclear Power Corporation of India", "agency_type": "central_psu"},
    {"code": "AG-SECI", "name": "Solar Energy Corporation of India", "agency_type": "central_psu"},

    # Aviation, Maritime & Urban
    {"code": "AG-AAI", "name": "Airports Authority of India", "agency_type": "central_psu"},
    {"code": "AG-DMRC", "name": "Delhi Metro Rail Corporation", "agency_type": "spv"},
    {"code": "AG-BMRCL", "name": "Bangalore Metro Rail Corporation", "agency_type": "spv"},
    {"code": "AG-MMRDA", "name": "Mumbai Metropolitan Region Dev Authority", "agency_type": "state_agency"},
    {"code": "AG-CMRL", "name": "Chennai Metro Rail Limited", "agency_type": "spv"},
    {"code": "AG-KMRL", "name": "Kochi Metro Rail Limited", "agency_type": "spv"},
    {"code": "AG-NCRTC", "name": "National Capital Region Transport Corp", "agency_type": "spv"},
    {"code": "AG-JNPA", "name": "Jawaharlal Nehru Port Authority", "agency_type": "central_psu"},
    {"code": "AG-DPA", "name": "Deendayal Port Authority", "agency_type": "central_psu"},
    {"code": "AG-IWAI", "name": "Inland Waterways Authority of India", "agency_type": "central_psu"},

    # Strategic & Communications
    {"code": "AG-BRO", "name": "Border Roads Organisation", "agency_type": "central_psu"},
    {"code": "AG-BSNL", "name": "Bharat Sanchar Nigam Limited", "agency_type": "central_psu"},
    {"code": "AG-BBNL", "name": "Bharat Broadband Network Limited", "agency_type": "central_psu"},

    # State Agencies
    {"code": "AG-UPRRN", "name": "UP State Bridge Corporation", "agency_type": "state_agency"},
    {"code": "AG-MSRDC", "name": "Maharashtra State Road Dev Corp", "agency_type": "state_agency"},
    {"code": "AG-KRDCL", "name": "Karnataka Road Dev Corp", "agency_type": "state_agency"},
    {"code": "AG-GSRDC", "name": "Gujarat State Road Dev Corp", "agency_type": "state_agency"},
    {"code": "AG-TNRDC", "name": "Tamil Nadu Road Dev Company", "agency_type": "state_agency"},
    {"code": "AG-APCRDA", "name": "AP Capital Region Dev Authority", "agency_type": "state_agency"},
    {"code": "AG-WBHDCL", "name": "West Bengal Highway Dev Corp", "agency_type": "state_agency"},
    {"code": "AG-BRPNNL", "name": "Bihar Rajya Pul Nirman Nigam", "agency_type": "state_agency"},

    # Major Private EPC Contractors & Concessionaires
    {"code": "AG-LNT", "name": "Larsen & Toubro Infrastructure", "agency_type": "private_epc"},
    {"code": "AG-TATAPROJ", "name": "Tata Projects Limited", "agency_type": "private_epc"},
    {"code": "AG-AFCONS", "name": "Afcons Infrastructure Limited", "agency_type": "private_epc"},
    {"code": "AG-DILIP", "name": "Dilip Buildcon Limited", "agency_type": "private_epc"},
    {"code": "AG-HCC", "name": "Hindustan Construction Company", "agency_type": "private_epc"},
    {"code": "AG-PNC", "name": "PNC Infratech Limited", "agency_type": "private_epc"},
    {"code": "AG-KNR", "name": "KNR Constructions Limited", "agency_type": "private_epc"},
    {"code": "AG-GRINFRA", "name": "G R Infraprojects Limited", "agency_type": "private_epc"},
    {"code": "AG-ASHOKA", "name": "Ashoka Buildcon Limited", "agency_type": "private_epc"},
    {"code": "AG-MEIL", "name": "Megha Engineering & Infrastructures", "agency_type": "private_epc"},
    {"code": "AG-NCC", "name": "NCC Limited", "agency_type": "private_epc"},
    {"code": "AG-SHAPOORJI", "name": "Shapoorji Pallonji EPC", "agency_type": "private_epc"},
    {"code": "AG-ADANIINFRA", "name": "Adani Road Transport Limited", "agency_type": "private_epc"},
    {"code": "AG-JMC", "name": "Kalpataru Projects International", "agency_type": "private_epc"}
]
