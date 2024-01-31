"""Hold info for the cleaning script."""

useless_tags = [
    "@spider",
    "nsi_id",
    "ownership_type",
    "store_type",
    "departments",
    "retail_id",
    "store_format",
    "display_name",
    "number",
    "image",
]

repeat_tags = [
    "image",
    "phone",
    "contact:phone",
    "contact:facebook",
    "contact:twitter",
    "contact:email",
]

overlap_tags = [
    ["website", "contact:website", "url"],
    ["phone", "contact:phone"],
]

direction_expand = {
    "NE": "Northeast",
    "SE": "Southeast",
    "NW": "Northwest",
    "SW": "Southwest",
    "N": "North",
    "E": "East",
    "S": "South",
    "W": "West",
}

name_expand = {
    "ARPT": "airport",
    "BLDG": "building",
    "CONF": "conference",
    "CONV": "convention",
    "CNTR": "center",
    "CTR": "center",
    "DWTN": "downtown",
    "INTL": "international",
    "SHPG": "shopping",
}

street_expand = {
    "ACC": "ACCESS",
    "ALY": "ALLEY",
    "ANX": "ANEX",
    "ARC": "ARCADE",
    "AV": "AVENUE",
    "AVE": "AVENUE",
    "BYU": "BAYOU",
    "BCH": "BEACH",
    "BND": "BEND",
    "BLF": "BLUFF",
    "BLFS": "BLUFFS",
    "BTM": "BOTTOM",
    "BLVD": "BOULEVARD",
    "BR": "BRANCH",
    "BRG": "BRIDGE",
    "BRK": "BROOK",
    "BRKS": "BROOKS",
    "BG": "BURG",
    "BGS": "BURGS",
    "BYP": "BYPASS",
    "CP": "CAMP",
    "CYN": "CANYON",
    "CPE": "CAPE",
    "CTR": "CENTER",
    "CTRS": "CENTERS",
    "CIR": "CIRCLE",
    "CIRS": "CIRCLES",
    "CLF": "CLIFF",
    "CLFS": "CLIFFS",
    "CLB": "CLUB",
    "CMN": "COMMON",
    "CMNS": "COMMONS",
    "COR": "CORNER",
    "CORS": "CORNERS",
    "CRSE": "COURSE",
    "CT": "COURT",
    "CTS": "COURTS",
    "CV": "COVE",
    "CVS": "COVES",
    "CRK": "CREEK",
    "CRES": "CRESCENT",
    "CRST": "CREST",
    "CSWY": "CAUSEWAY",
    "CURV": "CURVE",
    "DL": "DALE",
    "DM": "DAM",
    "DV": "DIVIDE",
    "DR": "DRIVE",
    "DRS": "DRIVES",
    "EXPY": "EXPRESSWAY",
    "EXPWY": "EXPRESSWAY",
    "EXT": "EXTENSION",
    "EXTS": "EXTENSIONS",
    "FLS": "FALLS",
    "FLD": "FIELD",
    "FLDS": "FIELDS",
    "FLT": "FLAT",
    "FLTS": "FLATS",
    "FRD": "FORD",
    "FRDS": "FORDS",
    "FRST": "FOREST",
    "FRG": "FORGE",
    "FRGS": "FORGES",
    "FRK": "FORK",
    "FRKS": "FORKS",
    "FT": "FORT",
    "FWY": "FREEWAY",
    "GD": "GRADE",
    "GDN": "GARDEN",
    "GDNS": "GARDENS",
    "GTWY": "GATEWAY",
    "GLN": "GLEN",
    "GLNS": "GLENS",
    "GRN": "GREEN",
    "GRNS": "GREENS",
    "GRV": "GROVE",
    "GRVS": "GROVES",
    "HBR": "HARBOR",
    "HBRS": "HARBORS",
    "HGWY": "HIGHWAY",
    "HVN": "HAVEN",
    "HTS": "HEIGHTS",
    "HWY": "HIGHWAY",
    "HL": "HILL",
    "HLS": "HILLS",
    "HOLW": "HOLLOW",
    "INLT": "INLET",
    "IS": "ISLAND",
    "ISS": "ISLANDS",
    "JCT": "JUNCTION",
    "JCTS": "JUNCTIONS",
    "KY": "KEY",
    "KYS": "KEYS",
    "KNL": "KNOLL",
    "KNLS": "KNOLLS",
    "LK": "LAKE",
    "LKS": "LAKES",
    "LNDG": "LANDING",
    "LN": "LANE",
    "LGT": "LIGHT",
    "LGTS": "LIGHTS",
    "LF": "LOAF",
    "LCK": "LOCK",
    "LCKS": "LOCKS",
    "LDG": "LODGE",
    "LP": "LOOP",
    "MNR": "MANOR",
    "MNRS": "MANORS",
    "MDW": "MEADOW",
    "MDWS": "MEADOWS",
    "ML": "MILL",
    "MLS": "MILLS",
    "MSN": "MISSION",
    "MTWY": "MOTORWAY",
    "MT": "MOUNT",
    "MTN": "MOUNTAIN",
    "MTNS": "MOUNTAINS",
    "NCK": "NECK",
    "ORCH": "ORCHARD",
    "OPAS": "OVERPASS",
    "PKY": "PARKWAY",
    "PKWY": "PARKWAY",
    "PSGE": "PASSAGE",
    "PNE": "PINE",
    "PNES": "PINES",
    "PL": "PLACE",
    "PLN": "PLAIN",
    "PLNS": "PLAINS",
    "PLZ": "PLAZA",
    "PT": "POINT",
    "PTS": "POINTS",
    "PRT": "PORT",
    "PRTS": "PORTS",
    "PR": "PRAIRIE",
    "PVT": "PRIVATE",
    "RADL": "RADIAL",
    "RNCH": "RANCH",
    "RPD": "RAPID",
    "RPDS": "RAPIDS",
    "RST": "REST",
    "RDG": "RIDGE",
    "RDGS": "RIDGES",
    "RIV": "RIVER",
    "RD": "ROAD",
    "RDS": "ROADS",
    "RT": "ROUTE",
    "RTE": "ROUTE",
    "SHL": "SHOAL",
    "SHLS": "SHOALS",
    "SHR": "SHORE",
    "SHRS": "SHORES",
    "SKWY": "SKYWAY",
    "SPG": "SPRING",
    "SPGS": "SPRINGS",
    "SQ": "SQUARE",
    "SQS": "SQUARES",
    "STA": "STATION",
    "STRA": "STRAVENUE",
    "STRM": "STREAM",
    "STS": "STREETS",
    "SMT": "SUMMIT",
    "SRVC": "SERVICE",
    "TER": "TERRACE",
    "TRWY": "THROUGHWAY",
    "THFR": "THOROUGHFARE",
    "TRCE": "TRACE",
    "TRAK": "TRACK",
    "TRFY": "TRAFFICWAY",
    "TRL": "TRAIL",
    "TRLR": "TRAILER",
    "TUNL": "TUNNEL",
    "TPKE": "TURNPIKE",
    "UPAS": "UNDERPASS",
    "UN": "UNION",
    "UNP": "UNDERPASS",
    "UNS": "UNIONS",
    "VLY": "VALLEY",
    "VLYS": "VALLEYS",
    "VW": "VIEW",
    "VWS": "VIEWS",
    "VLG": "VILLAGE",
    "VL": "VILLE",
    "VIS": "VISTA",
    "WKWY": "WALKWAY",
    "WL": "WELL",
    "WLS": "WELLS",
    "XING": "CROSSING",
    "XRD": "CROSSROAD",
    "XRDS": "CROSSROADS",
}

saints = [
    "Andrew",
    "John",
    "Mary",
    "Paul",
    "Peter",
    "Charles",
    "Mark",
    "Joseph",
    "James",
    "Luke",
    "Louis",
    "Francis",
    "Augustine",
    "Vincent",
    "Rose",
    "Lucie",
    "Cloud",
]
