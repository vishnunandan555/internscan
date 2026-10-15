"""India location filter and city classifier.

Location strings come in many ATS shapes ("Bengaluru, Karnataka, India",
"Bangalore", "Hyderabad, Telangana", "Remote - India", "India, Multiple Locations", ...).

Algorithm per location:
1. Explicit NON-India country / state / city -> reject
   (Prevents false positives like "Indiana, USA", "Indianapolis", "Indonesia", "London, UK")
2. Explicit India keyword / country / ISO code / Indian State -> accept
3. Well-known Indian city / tech hub -> accept
4. Otherwise -> reject

A job counts as an India job when ANY of its locations passes.
"""
import re


def _rx(words):
    return re.compile(r"\b(" + "|".join(re.escape(w) for w in words) + r")\b", re.IGNORECASE)


# Exclude words that could conflict with "IN" / "Ind" or resemble India
NON_INDIA = re.compile(
    r"\b("
    r"Indiana|Indianapolis|Indio|Indonesia|Jakarta|Bali|Indo[- ]?Pacific|"
    r"United States|USA|U\.S\.|Canada|United Kingdom|UK|England|London|"
    r"Germany|Deutschland|Berlin|Munich|France|Paris|Australia|Sydney|Melbourne|"
    r"Singapore|Japan|Tokyo|China|Beijing|Shanghai|Ireland|Dublin|"
    r"Netherlands|Amsterdam|Switzerland|Zurich|Poland|Warsaw|Sweden|Stockholm|"
    r"Brazil|Sao Paulo|Mexico|Israel|Tel Aviv|Spain|Madrid|Barcelona|"
    r"Taiwan|South Korea|Seoul|Hong Kong|Dubai|UAE|Saudi Arabia|"
    r"CAN|USA|GBR|DEU|FRA|AUS|SGP|JPN|CHN|IRL|NLD|CHE|POL|SWE|BRA|MEX|ISR|ESP|TWN|KOR|HKG|ARE|SAU"
    r")\b",
    re.IGNORECASE,
)

INDIA_COUNTRY_OR_STATE = _rx([
    "India", "IND", "Bharat",
    # States & Union Territories
    "Karnataka", "Telangana", "Maharashtra", "Tamil Nadu", "Tamilnadu",
    "Haryana", "Uttar Pradesh", "UP", "Delhi", "New Delhi", "Delhi NCR", "NCR",
    "Kerala", "West Bengal", "Gujarat", "Rajasthan", "Punjab", "Madhya Pradesh",
    "Andhra Pradesh", "AP", "Odisha", "Orissa", "Assam", "Goa", "Chandigarh",
    "Uttarakhand", "Jharkhand", "Bihar",
])

INDIA_CITIES = _rx([
    # Tier 1 Tech Hubs
    "Bengaluru", "Bangalore", "BLR",
    "Hyderabad", "HYD", "Secunderabad", "Cyberabad",
    "Pune", "PUN",
    "Gurugram", "Gurgaon", "GGN",
    "Noida", "Greater Noida",
    "Delhi", "New Delhi",
    "Chennai", "Madras", "MAA",
    "Mumbai", "Bombay", "BOM", "Navi Mumbai", "Thane",
    # Tier 2 Tech Hubs
    "Kolkata", "Calcutta",
    "Ahmedabad", "Gandhinagar",
    "Kochi", "Cochin",
    "Thiruvananthapuram", "Trivandrum",
    "Coimbatore",
    "Indore",
    "Jaipur",
    "Chandigarh", "Mohali", "Panchkula",
    "Bhubaneswar",
    "Mysuru", "Mysore",
    "Nagpur",
    "Visakhapatnam", "Vizag",
    "Vadodara", "Baroda",
    "Surat",
    "Mangalore", "Mangaluru",
    "Vijayawada",
    "Lucknow",
    "Kanpur",
    "Bhopal",
    "Dehradun",
])

REMOTE_INDIA = re.compile(
    r"\b(remote\s*[-–—]?\s*india|india\s*[-–—]?\s*remote|anywhere\s+in\s+india|work\s+from\s+home\s*[-–—]?\s*india)\b",
    re.IGNORECASE,
)


def _is_indian_location(text):
    if not text or not text.strip():
        return False
    text = text.strip()

    # Remote explicitly in India
    if REMOTE_INDIA.search(text):
        return True

    # If it contains an explicit foreign country without mentioning India
    if NON_INDIA.search(text) and not re.search(r"\b(india|ind)\b", text, re.IGNORECASE):
        return False

    if INDIA_COUNTRY_OR_STATE.search(text):
        return True

    return bool(INDIA_CITIES.search(text))


def is_india_job(locations):
    return any(_is_indian_location(loc) for loc in locations if loc)


# Ordered mapping of target UI hub tags to identifying location keywords.
CITY_TAG_RULES: tuple = (
    ("Bengaluru", ("bengaluru", "bangalore", "blr")),
    ("Hyderabad", ("hyderabad", "secunderabad", "cyberabad")),
    ("Pune", ("pune",)),
    ("Delhi-NCR", ("gurugram", "gurgaon", "noida", "delhi", "ncr")),
    ("Chennai", ("chennai",)),
    ("Mumbai", ("mumbai", "thane", "navi mumbai")),
)


def get_city_tag(locations):
    """Classify into standard UI filter tags: bengaluru, hyderabad, pune, ncr, chennai, mumbai, remote, other."""
    combined = " ".join(locations or []).lower()
    # Explicit parentheses: REMOTE_INDIA pattern matches directly, OR a generic "remote" string
    # is verified to actually be an Indian location (avoiding matching US/global-only remote roles).
    if REMOTE_INDIA.search(combined) or ("remote" in combined and is_india_job(locations)):
        return "Remote (India)"

    for tag, keywords in CITY_TAG_RULES:
        if any(kw in combined for kw in keywords):
            return tag

    return "India (Multiple/Other)"


# =============================================================================
# Global Country & Regional Hub Classifier
# =============================================================================

US_COUNTRY = re.compile(r"\b(United States|USA|U\.S\.A\.|U\.S\.)\b", re.IGNORECASE)
US_REMOTE = re.compile(
    r"\b(remote\s*[-–—]?\s*(us|usa|united states)|(us|usa|united states)\s*[-–—]?\s*remote|anywhere\s+in\s+(the\s+)?(us|usa))\b",
    re.IGNORECASE,
)
US_STATES_FULL = _rx([
    "California", "Washington", "New York", "Texas", "Massachusetts", "Colorado",
    "Illinois", "Georgia", "North Carolina", "Pennsylvania", "Virginia", "Ohio",
    "Michigan", "Florida", "Utah", "Oregon", "Maryland", "New Jersey", "Minnesota",
    "Arizona", "Indiana", "Wisconsin", "Missouri", "Tennessee", "Connecticut",
    "Iowa", "Kansas", "Kentucky", "Louisiana", "Nevada", "Oklahoma", "Alabama",
    "Arkansas", "Idaho", "Mississippi", "Montana", "Nebraska", "New Hampshire",
    "New Mexico", "Rhode Island", "South Carolina", "South Dakota", "Vermont",
    "West Virginia", "Wyoming", "District of Columbia",
])
US_STATE_CODES = re.compile(
    r"(?:,\s*|\b)("
    r"CA|WA|NY|TX|MA|CO|IL|GA|NC|PA|VA|OH|MI|FL|UT|OR|MD|NJ|MN|AZ|WI|MO|TN|CT|IA|KS|KY|LA|NV|OK|AL|AR|ID|MS|MT|NE|NH|NM|RI|SC|SD|VT|WV|WY|DC"
    r")\b",
)

US_HUB_RULES: tuple = (
    ("SF Bay Area", (
        "san francisco", "sf", "bay area", "mountain view", "sunnyvale", "palo alto",
        "san jose", "santa clara", "menlo park", "cupertino", "redwood city", "san mateo",
        "oakland", "berkeley", "fremont", "pleasanton", "san bruno", "south san francisco",
    )),
    ("Seattle", ("seattle", "redmond", "bellevue", "kirkland")),
    ("New York", ("new york", "nyc", "manhattan", "brooklyn")),
    ("Austin", ("austin", "round rock")),
    ("Boston", ("boston", "cambridge", "waltham")),
)

# Canada
CA_COUNTRY = re.compile(r"\b(Canada|CAN)\b", re.IGNORECASE)
CA_PROVINCES = _rx(["Ontario", "British Columbia", "Quebec", "Alberta", "Nova Scotia", "Manitoba", "Saskatchewan"])
CA_CITIES = _rx(["Toronto", "Vancouver", "Waterloo", "Kitchener", "Montreal", "Ottawa", "Calgary", "Edmonton"])

# United Kingdom
UK_COUNTRY = re.compile(r"\b(United Kingdom|UK|Great Britain|GBR|England|Scotland|Wales|Northern Ireland)\b", re.IGNORECASE)
UK_CITIES = _rx(["London", "Cambridge", "Oxford", "Edinburgh", "Manchester", "Bristol", "Glasgow", "Belfast"])

# Europe
EU_COUNTRIES = _rx([
    "Germany", "Deutschland", "Ireland", "Netherlands", "Switzerland", "France",
    "Sweden", "Poland", "Spain", "Italy", "Denmark", "Austria", "Finland", "Norway",
    "Czech Republic", "Czechia", "Estonia", "Portugal", "Belgium", "Romania",
])
EU_CITIES = _rx([
    "Berlin", "Munich", "München", "Dublin", "Amsterdam", "Zurich", "Zürich",
    "Paris", "Stockholm", "Warsaw", "Madrid", "Barcelona", "Krakow", "Prague",
    "Tallinn", "Copenhagen", "Vienna", "Lisbon", "Bucharest",
])

# Singapore / APAC
SG_COUNTRY = re.compile(r"\b(Singapore|SGP)\b", re.IGNORECASE)

GENERIC_REMOTE = re.compile(r"\b(remote|virtual|work\s+from\s+home|anywhere)\b", re.IGNORECASE)


def get_us_hub(locations):
    combined = " ".join(locations or []).lower()
    if US_REMOTE.search(combined) or ("remote" in combined and is_us_location(combined)):
        return "Remote (US)"
    for hub, keywords in US_HUB_RULES:
        if any(kw in combined for kw in keywords):
            return hub
    return "US (Other)"


def get_ca_hub(locations):
    combined = " ".join(locations or []).lower()
    if "waterloo" in combined or "kitchener" in combined:
        return "Waterloo"
    if "toronto" in combined:
        return "Toronto"
    if "vancouver" in combined:
        return "Vancouver"
    if "montreal" in combined:
        return "Montreal"
    if "remote" in combined:
        return "Remote (Canada)"
    return "Canada (Other)"


def get_uk_hub(locations):
    combined = " ".join(locations or []).lower()
    if "london" in combined:
        return "London"
    if "cambridge" in combined or "oxford" in combined:
        return "Cambridge / Oxford"
    if "remote" in combined:
        return "Remote (UK)"
    return "UK (Other)"


def get_eu_hub(locations):
    combined = " ".join(locations or []).lower()
    if "dublin" in combined:
        return "Dublin"
    if "berlin" in combined:
        return "Berlin"
    if "munich" in combined or "münchen" in combined:
        return "Munich"
    if "amsterdam" in combined:
        return "Amsterdam"
    if "zurich" in combined or "zürich" in combined:
        return "Zurich"
    if "remote" in combined:
        return "Remote (EU)"
    return "Europe (Other)"


NON_US_COUNTRIES = re.compile(
    r"\b(Mexico|Baja California|Brazil|Australia|Japan|China|South Korea|Israel|New Zealand|South Africa)\b",
    re.IGNORECASE,
)


def is_us_location(text):
    if not text:
        return False
    # If explicitly India, not US
    if _is_indian_location(text):
        return False
    # If explicit foreign country and not mentioning USA, not US
    if NON_US_COUNTRIES.search(text) and not US_COUNTRY.search(text):
        return False
    if (UK_COUNTRY.search(text) or CA_COUNTRY.search(text) or EU_COUNTRIES.search(text) or SG_COUNTRY.search(text)) and not US_COUNTRY.search(text):
        return False
    if US_COUNTRY.search(text) or US_REMOTE.search(text):
        return True
    if US_STATES_FULL.search(text):
        return True
    if US_STATE_CODES.search(text):
        return True
    for _, kws in US_HUB_RULES:
        if any(kw in text.lower() for kw in kws):
            return True
    return False


def classify_location(locations):
    """Classify a list of location strings into (country_code, region, city_hub).

    Returns:
        (country_code, region, city_hub)
        country_code: "in", "us", "ca", "uk", "eu", "sg", "remote", or "other"
        region: "APAC", "AMER", "EMEA", "Remote", or "Other"
        city_hub: e.g. "Bengaluru", "SF Bay Area", "Seattle", "London", etc.
    """
    if not locations:
        return ("other", "Other", "Unknown")

    # 1. India check
    if is_india_job(locations):
        return ("in", "APAC", get_city_tag(locations))

    combined = " ".join(locations)

    # 2. US check
    if any(is_us_location(loc) for loc in locations):
        return ("us", "AMER", get_us_hub(locations))

    # 3. Canada check
    if CA_COUNTRY.search(combined) or CA_PROVINCES.search(combined) or CA_CITIES.search(combined):
        return ("ca", "AMER", get_ca_hub(locations))

    # 4. UK check
    if UK_COUNTRY.search(combined) or UK_CITIES.search(combined):
        return ("uk", "EMEA", get_uk_hub(locations))

    # 5. Europe check
    if EU_COUNTRIES.search(combined) or EU_CITIES.search(combined):
        return ("eu", "EMEA", get_eu_hub(locations))

    # 6. Singapore check
    if SG_COUNTRY.search(combined):
        return ("sg", "APAC", "Singapore")

    # 7. Generic Global Remote check
    if GENERIC_REMOTE.search(combined):
        return ("remote", "Remote", "Global Remote")

    return ("other", "Other", "Other")

