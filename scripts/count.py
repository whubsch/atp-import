import datetime
import json
from collections import Counter
import sys
import requests

import polars

state_abbreviations = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


def get_state(props: dict) -> str:
    return props.get("addr:state", None)


CHALLENGE_URL = "https://maproulette.org/api/v2/challenge/view/43561"
CHALLENGE_FILE = "challenge.geojson"

try:
    req = requests.get(CHALLENGE_URL, timeout=5)
    data = req.json()
except TimeoutError as e:
    print(e)
    sys.exit()

with open(CHALLENGE_FILE, "w+", encoding="utf-8") as f:
    json.dump({"dt": str(datetime.datetime.now())} | data, f, indent=2)

with open(CHALLENGE_FILE, "r", encoding="utf-8") as f:
    contents: dict = json.load(f)

    state_list = []
    touched_list = []
    for i in contents["features"]:
        prop = i["properties"]
        if prop.get("mr_taskStatus") == "Created":
            state_list.append(get_state(prop))
        else:
            touched_list.append(get_state(prop))

    state = Counter(state_list)
    touched = Counter(touched_list)

    comb = [
        {
            "state": state_abbreviations.get(k),
            "unfixed": v,
            "fixed": touched.get(k, 0),
            "pct_fixed": touched.get(k, 0) / (touched.get(k, 0) + v),
        }
        for k, v in state.items()
        if k
    ]
    table = polars.from_dicts(comb).sort("unfixed", descending=True).sort("pct_fixed")
    print(table)
    x, y = table.get_column("fixed").sum(), table.get_column("unfixed").sum()
    print(x, y, x / (x + y))
