# atp-import

This is the Github repository where I'll keep files and scripts to process the All the Places information. Check out the [OSM wiki page](https://wiki.openstreetmap.org/wiki/Import/All_the_Places_US_data) for more information. The primary goal for this import is to add additional data to existing OSM objects in the US, not to validate existing data or add missing objects. The files are hosted in the `/data` folder to increase transparency and help with community quality assurance.

### Changeset tags

```
import=yes
source=All the Places
source:url=https://www.alltheplaces.xyz/
import:page=https://wiki.openstreetmap.org/wiki/Import/All_the_Places_US_data
source:license=CC0-1.0
```

## All the Places

All the Places is a set of web scrapers that retreives location and other data from the websites of large businesses. The data that All the Places has retrieved has been placed into the public domain. Check out the project's [homepage](https://www.alltheplaces.xyz/) and [repository](https://github.com/alltheplaces/alltheplaces) for more information.

## MapRoulette export

I will export any POIs that are not matched to existing OSM objects into a MapRoulette challenge for users to add on their own time, with their own local knowledge and tools.

## Maintaining objects

I may use external tooling to run periodic checks to ensure the ATP data is up-to-date.

This repository is licensed under the MIT License.
