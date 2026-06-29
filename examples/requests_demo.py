# tplib is TurboPython's standard library: packages for
# common tasks, built for a statically compiled language.
import tplib.requests as requests
from tplib.json.model import model

@model  # inspired by pydantic
class Geo:
    query: str      # the caller's IP
    city: str
    country: str
    lat: float
    lon: float

def main() -> None:
    url = "http://ip-api.com/json"
    # inspired by requests, a popular Python package
    body = requests.get(url).text
    geo = Geo.from_json(body)
    print(f"{geo.query} in {geo.city}, {geo.country}")
    print(f"at {geo.lat:.2f}, {geo.lon:.2f}")

main()
