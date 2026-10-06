# Corpus manifest

Load these before you trust a citation. US government works are not copyrighted. NWSS original ORNL text is public domain; Kearny's 1986 additions are copyrighted and marked in the OISM edition — prefer the 1979 ORNL text or clearly skip the copyrighted additions.

Do not add commercial survival books, current medical textbooks, or "Where There Is No Doctor" until you have checked the license. Hesperian allows free distribution under its own terms; it is not public domain.

| id | document | status | get it |
| --- | --- | --- | --- |
| FM21-76 | US Army FM 21-76 Survival (1992 issue is the common one; older issues differ) | US government work | https://archive.org/details/Fm21-76SurvivalManual |
| FM3-05.70 | Survival (successor manual) | US government work | Army Publishing Directorate / commonly mirrored |
| FM4-25.11 | First Aid | US government work | Army Publishing Directorate |
| FM21-10 | Field Hygiene and Sanitation | US government work | Army Publishing Directorate |
| ST31-91B | Special Forces Medical Handbook | US government work, dated, not current medicine | widely mirrored; treat as historical |
| NWSS-1979 | Kearny, Nuclear War Survival Skills, ORNL 1979 | public domain technical report ADA328301 | https://apps.dtic.mil/sti/html/tr/ADA328301/ |
| FEMA-AYR | Are You Ready? citizen preparedness | US government work | fema.gov |
| CDC-WATER | How to Make Water Safe in an Emergency | US government work, page reviewed 2025-12-17 | https://www.cdc.gov/water-emergency/about/index.html |
| CDC-KI | Potassium Iodide (KI) | US government work, page reviewed 2025-01-29 | https://www.cdc.gov/radiation-emergencies/treatment/potassium-iodide.html |
| EPA-WATER | Emergency disinfection of drinking water | US government work | epa.gov |

survivalRAG (github.com/bdkoeh/survivalRAG) already chunked about 70 public-domain PDFs plus CC-BY-SA medical articles. Using it is faster than rebuilding. Their Wikipedia tier is not a dosing authority. Keep it out of the dose path.

## Index rules

- Chunk by section heading, not by fixed 512 tokens, or procedures split mid-step.
- Store source id, edition year, and page or section in metadata. A citation without those is unscored.
- Do not embed the pinned dose tables into the vector index as just another passage. Inject them into the prompt on every dose question so retrieval cannot outrank them.
