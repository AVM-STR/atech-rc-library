"""
A-Tech Appraisal Co. — Revision & Comment Library
Streamlit Web App
"""

import os, json, io, tempfile
import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image as PILImage
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, HRFlowable, PageBreak, KeepTogether,
                                 Image as RLImage)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import Flowable

LOGO_PATH = os.path.join(os.path.dirname(__file__), "atech_logo.png")

# ── Default Data ──────────────────────────────────────────────────────────────
DEFAULT_REVISIONS = [
    {"id": "r1", "category": "Rental Comp Selection — Multi-Family vs SFR", "request": "As per the report, subject is 'Multi-Family' however SFR (single family) rental comp #1-3 is used, please verify or comment.", "response": "All rental comparables provided in this report are sourced from multi-family dwellings, not single-family residences. Individual units within multi-family properties are typically marketed and leased on a per-unit basis, and the rental listings utilized reflect individually marketed units from within multi-family buildings. These represent the most recent and relevant market rent data available, as active and recent listings from multi-family properties provide the most accurate reflection of current market rents for the subject's unit type. The rental comparables are considered appropriate and consistent with the subject's property classification.", "notes": ""},
    {"id": "r2", "category": "Building Official — Verbal vs Written Documentation", "request": "The lender is asking if the appraiser received anything from the building official that stated that the kitchen needed to be removed so that they can present it to the borrower?", "response": "The appraiser did not receive written documentation from the building official; however, the appraiser contacted the building department directly and was verbally informed of the requirements necessary to bring the property into compliance. The items communicated by the building department were incorporated into the report as subject-to conditions reflecting those requirements.", "notes": "Customize the building department name to match the subject municipality."},
    {"id": "r3", "category": "Basement Discoloration — Moisture Observation", "request": "Appraiser to comment on discoloration on concrete basement floors and state whether any moisture or dampness was observed.", "response": "At the time of inspection there were no present areas of moisture or dampness observed. The discoloration noted on the concrete basement floor is consistent with normal aging and does not indicate active moisture intrusion based on the appraiser's visual observation at the time of inspection.", "notes": "If moisture was present, modify accordingly. This is a visual observation disclaimer — not a structural certification."},
    {"id": "r4", "category": "Not a PUD — Client States Subject is a PUD", "request": "Client states the subject is a PUD.", "response": "A Planned Unit Development (PUD) is generally characterized by a homeowners association that holds title to and is responsible for maintaining common areas and amenities, with individual unit owners holding fee simple title to their lots and improvements. The subject property does not meet this definition. [OPTION A — No HOA: The subject has no homeowners association, common areas, or shared amenities that would indicate a PUD classification.] [OPTION B — Minor HOA: The subject does carry a nominal HOA fee for common area maintenance; however, this fee structure alone does not constitute a PUD classification. The subject's HOA structure does not rise to that level.] The property has been appropriately classified consistent with its legal description, site ownership, and market perception.", "notes": "Use Option A if no HOA. Use Option B if minor HOA exists. Delete the option that does not apply."},
]

DEFAULT_COMMENTS = [
    {"id": "c1",  "category": "Land Condo — Classification and Market Perception", "text": "A land condominium is a form of ownership in which the unit owner holds fee simple title to the land beneath their home (the 'unit'), while certain common elements — such as roads, utilities, or shared open space — are owned collectively by the association. Unlike a traditional condominium, the land condo owner holds direct ownership of the land, and the structure is treated in a manner consistent with single-family ownership for appraisal and lending purposes. In the subject's market area, land condominiums are generally perceived by buyers and sellers as functionally equivalent to fee simple single-family homes. The market does not demonstrate a measurable valuation differential between land condo and fee simple single-family properties in this neighborhood.", "notes": "Verify that your comparable sales are also land condos where possible."},
    {"id": "c2",  "category": "Concession Adjustments — Adjusted at Cash Value", "text": "It would appear from the analysis of the market that concessions of 0-4% are typical within the subject's marketing area. There is not a prevalence of loan discounts, interest buy-downs and/or concessions which would have a negative impact on the subject property's market value, unless otherwise stated in the report. However, the appraiser has assessed adjustments to comparables in an effort to demonstrate a cash basis for adjusted value.", "notes": "Use when concessions are present but not excessive."},
    {"id": "c3",  "category": "Concession Adjustments — Adjusted Only When Excessive", "text": "The analysis of the average concessions package for homes within the sample used to determine market trends indicates a range of approximately X-X%. There is no prevalent use of loan discounts, interest rate buy-downs, or concessions that would negatively impact the subject property's market value unless otherwise stated in the report. Consequently, the appraiser has applied adjustments to comparables only when they exceed the typical threshold for the overall market.", "notes": "Use when concessions exist but are not being adjusted on every comp."},
    {"id": "c4",  "category": "Chain of Title", "text": "The appraiser has conducted a thorough search of the subject property and comparables to determine the chain of title and the number of transfers for each home. All available and customary data sources were utilized to obtain this information, including MLS, CompFlo deeds, Realist tax, and public record. However, it should be noted that data in this area can sometimes be unreliable, particularly for recent transfers. While every effort was made to identify all transfers, it is not guaranteed that every transaction was captured. The purpose of the appraiser's chain of title examination is to alert the client to any potentially compromised comparables or non-arm's length transactions.", "notes": "Update data sources to match your actual sources."},
    {"id": "c5",  "category": "Comparable Selection Criteria", "text": "In searching for comparables, the appraiser has emphasized location, lot size, gross living area, utility, design, age, and condition, with specific emphasis on sales that closed within 180 days prior to the effective date. In most cases, comparables older than six months have been eliminated from consideration. In cases where the appraiser could not locate recent sales within the immediate area, a representative sample of homes from both the subject neighborhood and competing areas was utilized. Sales that may represent outlier events have been carefully scrutinized and eliminated from consideration when appropriate.", "notes": ""},
    {"id": "c6",  "category": "Highest and Best Use", "text": "The relevant legal, physical, and economic factors were analyzed to the extent necessary and resulted in a conclusion that the current use of the subject property is the highest and best use [USPAP — Standards Rule 2-2(b)(x)].", "notes": ""},
    {"id": "c7",  "category": "Condition/Quality Adjustments — General", "text": "It should be noted that the appraiser considered numerous sales within the defined neighborhood reflecting various states of condition. In comparable selection the appraiser made a concentrated effort to locate and select homes similar in terms of physical characteristics and condition. The appraiser assessed features and condition through the use of MLS listings, interior photos (when available), and exterior inspections. Any condition/quality adjustments assessed are based on the appraiser's assessment of contributory value via paired sales analysis. Unless otherwise noted the appraiser has applied equal emphasis to all comparable sales.", "notes": ""},
    {"id": "c8",  "category": "Condition/Quality Adjustments — UAD Requirements", "text": "UAD requirements mandate that condition and quality ratings be reported on an 'absolute' basis rather than a 'relative' basis. Consequently, in some cases the appraiser will make adjustments to comparables that share the same UAD condition or quality rating due to minor differences in overall condition or quality. The appraiser assessed features and condition through the use of MLS listings, interior photos, and exterior inspections. During the course of research, the appraiser deemed that comparables #[X] and #[X] warrant a similar condition rating but were slightly superior/inferior in terms of overall condition. Consequently, an adjustment of $[X,XXX] has been assigned based on the appraiser's assessment of contributory value via paired sales analysis.", "notes": "Fill in comparable numbers and adjustment amount."},
    {"id": "c9",  "category": "Active Listing/Pending Sale — Multiple", "text": "Comparables #[X] and #[X] are active listings/pending sales and were included to demonstrate current market activity within the subject's marketing area. A conservative [X]% adjustment was assessed to the active listings in an effort to compensate for the typical differential between list price and sales price.", "notes": "Typically 5-10% depending on market."},
    {"id": "c10", "category": "Active Listing/Pending Sale — Single (with explanation)", "text": "Comparable #[X] is an active listing/pending sale and was included to demonstrate current market activity within the subject's marketing area. A conservative [X]% adjustment was assessed in an effort to compensate for the typical differential between list price and sales price. Please note that the appraiser conducted an exhaustive search for an additional listing competitive to the subject; however, none similar in terms of age, GLA, and condition were available as of the effective date.", "notes": ""},
    {"id": "c11", "category": "Predominant Value — Appraised Value Exceeds Predominant", "text": "The predominant value as stated on page 1 of this appraisal is approximately $[X]; however, this range applies to the subject's immediate marketing area as a whole. Homes within this range are considered to be inferior in terms of GLA, age, quality of construction, appeal, and utility. Consequently the appraised value exceeds the predominant value. The home is not considered to be over-improved for the marketing area.", "notes": ""},
    {"id": "c12", "category": "Effective Age — Less Than Actual Age", "text": "Please note that it is the opinion of the appraiser that the effective age is less than the actual age of the subject property. This assertion is predicated on the fact that the subject has been well-maintained and that the home's true age does not reflect the general upkeep performed over its lifetime. Although the home does show general wear and tear consistent with its age, its effective age has been estimated at [X] years.", "notes": "Fill in the estimated effective age."},
    {"id": "c13", "category": "GLA — Differs from Public Record (>10%)", "text": "Please note that the GLA for the subject may differ from public record by more than 10%. The measurements indicated within this report are considered to be highly accurate. Differentials of this nature are not uncommon and are attributed to inaccuracies within the public record data. Discrepancies commonly occur when municipalities include basement or unfinished attic area in the reported GLA figure.", "notes": ""},
    {"id": "c14", "category": "GLA — Differential Exceeds 20% Preferred Guideline", "text": "Please note that the GLA differential for some comparables exceeds the preferred 20% guideline. This is attributed to the complexity of comparable selection and the limited availability of recent comparable sales similar in terms of GLA. Consequently, the appraiser was required to utilize homes that were inferior/superior in terms of GLA and has applied the necessary adjustments accordingly.", "notes": ""},
    {"id": "c15", "category": "GLA — Subject Inferior to All Comparables", "text": "Please note that the subject is inferior in terms of GLA to all comparables utilized. The appraiser conducted an exhaustive search for recent comparables similar or superior in terms of GLA; however, very few that could be considered similar in terms of age and condition were available at the time of inspection. The subject is not considered to be inadequate for its marketing area.", "notes": ""},
    {"id": "c16", "category": "GLA — Subject Superior to All Comparables", "text": "Please note that the subject is superior in terms of GLA to all comparables utilized. The appraiser conducted an exhaustive search for recent comparables similar in terms of GLA; however, very few that could be considered similar in terms of age and condition were available. The subject is not considered to be over-improved for its marketing area.", "notes": ""},
    {"id": "c17", "category": "GLA — Split Level Threshold Method", "text": "Please note that the subject is a split-level home. For the purposes of this appraisal the appraiser has utilized the 'threshold method of entry' to report GLA and basement areas. This entails reporting 'below grade' area as all finished/unfinished area below the threshold of the front door. This method is applied consistently across all comparables. Within this market, tax records tend to be inconsistent when reporting physical characteristics for split-level homes.", "notes": ""},
    {"id": "c18", "category": "Net/Gross Adjustments Exceed 15%/25%", "text": "Please note that some comparables exceed the preferred guidelines of 15% and/or 25% for net and/or gross adjustment percentages respectively. This can be attributed to the complexity of comparable selection and the limited number of recent available comparable sales. The subject's floor plan, GLA, and lot size in conjunction with age made it necessary to utilize a variety of homes to 'bracket' the market's reaction for each contributory characteristic.", "notes": ""},
    {"id": "c19", "category": "Line Item Adjustments Exceed 10%", "text": "Please note that single line item adjustments for some comparables exceed the preferred 10% guideline. This can be attributed to the complexity of comparable selection and the limited number of recent available comparable sales. The subject's floor plan, GLA, and lot size in conjunction with age made it necessary to utilize a variety of homes to 'bracket' the market's reaction for each contributory characteristic.", "notes": ""},
    {"id": "c20", "category": "Land Value Exceeds 30%", "text": "Please note that land value for the subject exceeds 30% of indicated market value. This can be attributed to the limited availability of vacant land for development within the subject's defined neighborhood and the enhanced marketability associated with the subject's location. This is considered typical for the subject's marketing area.", "notes": "Common in coastal RI markets. Pair with land sales data when possible."},
    {"id": "c21", "category": "Pool — In-Ground Pool Adjustment", "text": "Please note that the subject has an in-ground pool. Within this market, pools are considered to affect marketability in a positive manner. Consequently an adjustment of $[XX,XXX] was assessed to all comparables without pools in an effort to compensate for the enhanced marketability considered to be inherent in such a feature.", "notes": "Fill in the dollar adjustment. Support with paired sales if challenged."},
    {"id": "c22", "category": "Waterfront / River Lot", "text": "Please note that the subject is situated on a waterfront/river-front lot. Within this market, the subject's lot influence represents a significant, positive component of the subject's marketability and appeals to a specific pool of buyers. The appraiser made a concentrated effort to locate and/or utilize homes similar in terms of lot influence. The appraiser has assessed a $[XX,000] adjustment to all comparables not situated on a lot with a similar external influence in an effort to compensate for the enhanced marketability.", "notes": "Especially relevant for Narragansett, coastal RI, and waterfront MA assignments."},
    {"id": "c23", "category": "Acreage / Large Lot", "text": "Please note that the subject is situated on approximately [XX] acres. Within this market, the subject's lot size represents a significant, positive component of the subject's marketability. Per MLS, vacant land sales and listings within the subject's defined neighborhood are selling/listing from $[X] to $[X] per acre. The appraiser has adjusted conservatively at $[X] per acre to compensate for the subject's lot size.", "notes": "Fill in acreage and per-acre values from land sales."},
    {"id": "c24", "category": "External Obsolescence — High Traffic Street", "text": "Please note that the subject suffers from incurable external obsolescence in the form of close proximity to a moderately high-traffic street. The appraiser conducted an exhaustive search for comparable sales with a similar external influence; however, none were available for review at the time of inspection. The appraiser assessed a $[X,000] adjustment to all comparables that do not share a similar external influence.", "notes": ""},
    {"id": "c25", "category": "External Obsolescence — Power Lines", "text": "Please note that the subject suffers from incurable external obsolescence in the form of close proximity to power lines. The appraiser conducted an exhaustive search for comparable sales with a similar external influence; however, none were available for review at the time of inspection. The appraiser assessed a conservative $[X,000] adjustment based on market knowledge, realtor interviews, and historical sales data.", "notes": ""},
    {"id": "c26", "category": "Flood Zone — Portion of Lot in 100-Year Flood Plain", "text": "A portion of the subject property appears to lie within the 100-year flood plain; however, improvements do not appear to lie within the flood zone. The appraiser is not an expert in this field and recommends that a flood certification be obtained to more specifically determine the subject's position relative to the flood zone.", "notes": "Add adjustment language if a flood zone adjustment was made."},
    {"id": "c27", "category": "Condition Disclaimer — Not a Home Inspection", "text": "Please note that this appraisal is not a home inspection and the appraiser is not acting as a home inspector. While observing the subject property, the appraiser visually observed areas that were readily accessible. The appraiser is not required to disturb or move obstructions to visibility. The inspection is not technically exhaustive. A formal home inspection for the subject property was not provided to the appraiser. The appraisal report should not be relied upon to disclose any conditions present in the subject property. A professional home inspection is recommended on all property purchase transactions.", "notes": "Include on any assignment with deferred maintenance, C4 or lower, or noted repairs."},
    {"id": "c28", "category": "C1 — New Construction", "text": "New Construction (C1): The subject is new construction. Due to the age of the subject, no physical inadequacies were noted at the time of inspection. For the purposes of this appraisal and to establish a basis for comparison, the appraiser has listed the home as 'new' or C1 condition.", "notes": ""},
    {"id": "c29", "category": "C2 — Remodeled", "text": "Remodeled (C2): Please note that the subject has recently been subjected to a comprehensive remodel. A detailed list of improvements has been attached to this report. The appraiser noted obvious and readily observable improvements to the property completed in a workmanlike manner. It is the opinion of the appraiser that the noted improvements have brought the home into good marketable condition. The appraiser has listed the home as 'good/remodeled' or C2 condition.", "notes": ""},
    {"id": "c30", "category": "C3 — Updated Condition", "text": "Updated Condition (C3): Please note that the subject has been well maintained and has been subjected to a series of recent improvements. The appraiser noted obvious and readily observable improvements completed in a workmanlike manner. The appraiser has listed the subject in 'updated' or C3 condition.", "notes": ""},
    {"id": "c31", "category": "C4 — Average Condition", "text": "Average Condition (C4): Please note that the subject has been adequately maintained and is considered to be in average marketable condition. The appraiser noted no recent major renovations and/or improvements to the property within the last [X] years. The appraiser has listed the home as 'average' or C4 condition.", "notes": ""},
    {"id": "c32", "category": "C5/C6 — Fair/Poor Condition", "text": "Fair Condition (C5-C6): Please note that the subject is currently in a deteriorated state of condition. An interior inspection revealed that many interior and exterior components indicate that some items may be closer to the end of their useful life than a cursory inspection might reveal. The appraiser has provided a list of repairs that represent what was readily observable at the time of inspection; however, this appraisal is not a home inspection. A professional home inspection is recommended. The property is considered to be in 'fair' or C5 condition.", "notes": ""},
    {"id": "c33", "category": "Income Approach — Not Utilized", "text": "Please note that the appraiser has considered the income approach to value for the subject; however, the approach was not feasible due to the limited availability of information regarding rental homes that have recently sold. In order to generate an income approach to value, the appraiser would require access to recently sold rental homes to develop a reliable gross rent multiplier (GRM). The data sources available within the normal course of business do not lend themselves to identifying sufficient arm's-length investment transactions of this type. Consequently, the income approach to value has not been developed.", "notes": ""},
    {"id": "c34", "category": "Adjustment Factors — GLA Methodology", "text": "Please note that adjustment factors are based on sales comparison analysis or modified cost approach to determine the contributory value of specific marketability factors for the subject. Regression analysis is not feasible during the normal course of business in this market area as MLS data does not typically provide accurate representations of all relevant physical characteristics. Consequently, adjustment factors are based on paired sales analysis, market extraction, local builder and realtor input, and building cost databases.", "notes": "This language directly addresses regression analysis pushback."},
    {"id": "c35", "category": "Gross Building Area (GBA) — Multi-Family Definition", "text": "Exterior measurements of a two-to-four family building are used to calculate the Gross Building Area (GBA). Interior finished space, including below-grade living space, interior stairways, hallways, storage rooms, and laundry rooms are part of the GBA. Exterior stairways are not included. Due to the subject's multi-family status, the total rentable area is calculated as GBA. Consequently the below-grade area has been included in the GBA.", "notes": "Use on all 2-4 family assignments."},
    {"id": "c36", "category": "Scope of Work — Conventional", "text": "In conducting this appraisal assignment, the appraiser first collected preliminary public record data and made an initial search of available market sales, trends, and influences. A physical inspection of the subject property was made in accordance with the information requirements of the URAR format. The appraiser is not an expert in matters of pest control, structural engineering, hazardous waste, survey, or title matters, and no expertise or warranty is implied in these areas.", "notes": ""},
]

DEFAULT_ZONING = [
    {'id': 'z0', 'city': 'Barrington', 'district': 'RE', 'property_type': '', 'frontage': 'See Note', 'lot_area': 'See Note', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'As consistent with the requirements of the predominant residential zoning designation of the area  surrounding the property, being either the R-25 or the R-40 District.'},
    {'id': 'z1', 'city': 'Barrington', 'district': 'AR', 'property_type': '', 'frontage': "180' / 100'", 'lot_area': '120,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z2', 'city': 'Barrington', 'district': 'R-40 CD (SF)', 'property_type': '', 'frontage': "180' SINGLE FAM / 100'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling'},
    {'id': 'z3', 'city': 'Barrington', 'district': 'R-25 (SF)', 'property_type': '', 'frontage': "90' SINGLE FAM / 60'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '25,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling'},
    {'id': 'z4', 'city': 'Barrington', 'district': 'R-10 (SF)', 'property_type': '', 'frontage': "90' SINGLE FAM", 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling'},
    {'id': 'z5', 'city': 'Barrington', 'district': 'NB/RBF', 'property_type': '', 'frontage': "90'", 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z6', 'city': 'Barrington', 'district': 'GI', 'property_type': '', 'frontage': '', 'lot_area': '', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'As consistent with the requirements of the predominant residential zoning designation of the area  surrounding the property, being either the R-25 or the R-40 District.'},
    {'id': 'z7', 'city': 'Block Island (New Shoreham)', 'district': 'RA', 'property_type': '', 'frontage': "200'", 'lot_area': '120,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z8', 'city': 'Block Island (New Shoreham)', 'district': 'RB', 'property_type': '', 'frontage': "150'", 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z9', 'city': 'Block Island (New Shoreham)', 'district': 'RC', 'property_type': '', 'frontage': "75'", 'lot_area': '20,000 SF / 40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'With Sewer / Without Sewer'},
    {'id': 'z10', 'city': 'Block Island (New Shoreham)', 'district': 'RC/M', 'property_type': '', 'frontage': "75'", 'lot_area': '20,000 SF / 40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'With Sewer / Without Sewer'},
    {'id': 'z11', 'city': 'Block Island (New Shoreham)', 'district': 'M', 'property_type': '', 'frontage': "75'", 'lot_area': '20,000 SF / 40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'With Sewer / Without Sewer'},
    {'id': 'z12', 'city': 'Block Island (New Shoreham)', 'district': 'OHC', 'property_type': '', 'frontage': "75'", 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z13', 'city': 'Block Island (New Shoreham)', 'district': 'NHC', 'property_type': '', 'frontage': "150'", 'lot_area': '20,000 SF / 40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'With Sewer / Without Sewer'},
    {'id': 'z14', 'city': 'Block Island (New Shoreham)', 'district': 'SC', 'property_type': '', 'frontage': "100'", 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z15', 'city': 'Bristol', 'district': 'R-80', 'property_type': '', 'frontage': '150', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z16', 'city': 'Bristol', 'district': 'R-40', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z17', 'city': 'Bristol', 'district': 'R-20', 'property_type': '', 'frontage': '120', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z18', 'city': 'Bristol', 'district': 'R-15', 'property_type': '', 'frontage': '100', 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z19', 'city': 'Bristol', 'district': 'R-10', 'property_type': '', 'frontage': '80', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z20', 'city': 'Bristol', 'district': 'R-10SW', 'property_type': '', 'frontage': '80', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'With public water & sewer'},
    {'id': 'z21', 'city': 'Bristol', 'district': 'R-8', 'property_type': '', 'frontage': '80', 'lot_area': '8,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z22', 'city': 'Bristol', 'district': 'R-6', 'property_type': '', 'frontage': '60', 'lot_area': '6,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '1 dwelling unit; +4,000 SF per additional unit'},
    {'id': 'z23', 'city': 'Burrillville', 'district': 'OS', 'property_type': '', 'frontage': "450'", 'lot_area': '5 acres (conservation)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z24', 'city': 'Burrillville', 'district': 'R-40', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z25', 'city': 'Burrillville', 'district': 'R-7', 'property_type': '', 'frontage': '75', 'lot_area': '7,500 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z26', 'city': 'Burrillville', 'district': 'VC', 'property_type': '', 'frontage': "125'", 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z27', 'city': 'Central Falls', 'district': 'R-1', 'property_type': '', 'frontage': '40', 'lot_area': '5,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z28', 'city': 'Central Falls', 'district': 'R-2', 'property_type': '', 'frontage': '40', 'lot_area': '5,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '+2,500 SF for 1st 2 units; +1,500 SF each additional unit'},
    {'id': 'z29', 'city': 'Central Falls', 'district': 'R-3', 'property_type': '', 'frontage': '40', 'lot_area': '5,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '+2,000 SF for 1st 3 units; +1,000 SF each additional unit; max height 30 ft / 3 stories'},
    {'id': 'z30', 'city': 'Charlestown', 'district': 'R-20', 'property_type': '', 'frontage': '120', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z31', 'city': 'Charlestown', 'district': 'R-40', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z32', 'city': 'Charlestown', 'district': 'R-40 Cluster', 'property_type': '', 'frontage': '100', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z33', 'city': 'Charlestown', 'district': 'R-2A', 'property_type': '', 'frontage': '200', 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z34', 'city': 'Charlestown', 'district': 'R-2A Multi-family', 'property_type': '', 'frontage': "200 / +10' per dwelling unit", 'lot_area': '2 acres per dwelling unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z35', 'city': 'Charlestown', 'district': 'R-3A', 'property_type': '', 'frontage': "300'", 'lot_area': '30 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z36', 'city': 'Charlestown', 'district': 'C-1', 'property_type': '', 'frontage': "120'", 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z37', 'city': 'Charlestown', 'district': 'C-2', 'property_type': '', 'frontage': "150'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z38', 'city': 'Coventry', 'district': 'Village Rural Commercial', 'property_type': '', 'frontage': '125', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z39', 'city': 'Coventry', 'district': 'Village Main Street Commercial', 'property_type': '', 'frontage': '80', 'lot_area': '7,500 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z40', 'city': 'Coventry', 'district': 'General Business', 'property_type': '', 'frontage': '125', 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z41', 'city': 'Coventry', 'district': 'General Business-1', 'property_type': '', 'frontage': '200', 'lot_area': '43,560 SF (1 acre)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z42', 'city': 'Cranston', 'district': 'A-80', 'property_type': '', 'frontage': '', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z43', 'city': 'Cranston', 'district': 'A-20', 'property_type': '', 'frontage': '', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z44', 'city': 'Cranston', 'district': 'A-12', 'property_type': '', 'frontage': '', 'lot_area': '12,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z45', 'city': 'Cranston', 'district': 'A-8', 'property_type': '', 'frontage': '', 'lot_area': '8,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z46', 'city': 'Cranston', 'district': 'A-6', 'property_type': '', 'frontage': '', 'lot_area': '6,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z47', 'city': 'Cranston', 'district': 'B-1', 'property_type': '', 'frontage': '', 'lot_area': '6,000 SF (SF); 8,000 SF (2F)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z48', 'city': 'Cranston', 'district': 'B-2', 'property_type': '', 'frontage': '', 'lot_area': '6,000 SF (SF); 8,000 SF (2F)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z49', 'city': 'East Greenwich', 'district': 'R-4', 'property_type': '', 'frontage': "100'", 'lot_area': '4,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z50', 'city': 'East Greenwich', 'district': 'R-10', 'property_type': '', 'frontage': "100'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z51', 'city': 'East Greenwich', 'district': 'R-20', 'property_type': '', 'frontage': "125'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z52', 'city': 'East Greenwich', 'district': 'R-30', 'property_type': '', 'frontage': "150'", 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z53', 'city': 'East Greenwich', 'district': 'F-1', 'property_type': '', 'frontage': "150'", 'lot_area': '1 Acre', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z54', 'city': 'East Greenwich', 'district': 'F-2', 'property_type': '', 'frontage': "150'", 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z55', 'city': 'East Providence', 'district': 'Residential 1', 'property_type': '', 'frontage': '125', 'lot_area': '18,750 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z56', 'city': 'East Providence', 'district': 'Residential 2', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z57', 'city': 'East Providence', 'district': 'Residential 3', 'property_type': '', 'frontage': '75', 'lot_area': '7,500 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z58', 'city': 'East Providence', 'district': 'Residential 4', 'property_type': '', 'frontage': '50', 'lot_area': '5,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z59', 'city': 'East Providence', 'district': 'Residential 5', 'property_type': '', 'frontage': '75', 'lot_area': '7,500 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z60', 'city': 'East Providence', 'district': 'Residential 6', 'property_type': '', 'frontage': '50', 'lot_area': '5,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z61', 'city': 'East Providence', 'district': 'Commercial 1', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z62', 'city': 'East Providence', 'district': 'Commercial 2', 'property_type': '', 'frontage': '50', 'lot_area': '5,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z63', 'city': 'East Providence', 'district': 'Industrial 1', 'property_type': '', 'frontage': '150', 'lot_area': '30,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z64', 'city': 'East Providence', 'district': 'Industrial 2', 'property_type': '', 'frontage': '175', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z65', 'city': 'Exeter', 'district': 'RE-2', 'property_type': '', 'frontage': '200', 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z66', 'city': 'Exeter', 'district': 'RU-3', 'property_type': '', 'frontage': '250', 'lot_area': '3 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z67', 'city': 'Exeter', 'district': 'RU-4', 'property_type': '', 'frontage': '300', 'lot_area': '4 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z68', 'city': 'Exeter', 'district': 'CR-5', 'property_type': '', 'frontage': '350', 'lot_area': '5 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z69', 'city': 'Exeter', 'district': 'LB-R', 'property_type': '', 'frontage': '150', 'lot_area': '2 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z70', 'city': 'Exeter', 'district': 'LI', 'property_type': '', 'frontage': '400', 'lot_area': '2 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z71', 'city': 'Foster', 'district': 'AR', 'property_type': '', 'frontage': '300', 'lot_area': '200,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z72', 'city': 'Foster', 'district': 'GB', 'property_type': '', 'frontage': '300', 'lot_area': '200,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z73', 'city': 'Foster', 'district': 'HC2', 'property_type': '', 'frontage': '300', 'lot_area': '200,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z74', 'city': 'Glocester', 'district': 'A-4', 'property_type': '', 'frontage': '350', 'lot_area': '4 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z75', 'city': 'Hopkinton', 'district': 'R-1', 'property_type': '', 'frontage': '100', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Subdivision requires 60,000 SF per lot; 2-family: 80,000 SF per unit'},
    {'id': 'z76', 'city': 'Hopkinton', 'district': 'RFR-80', 'property_type': '', 'frontage': '225', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z77', 'city': 'Hopkinton', 'district': 'Neighborhood Business', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z78', 'city': 'Hopkinton', 'district': 'Commercial', 'property_type': '', 'frontage': '150', 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z79', 'city': 'Hopkinton', 'district': 'Manufacturing', 'property_type': '', 'frontage': '225', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z80', 'city': 'Johnston', 'district': 'R-40', 'property_type': '', 'frontage': '140', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z81', 'city': 'Lincoln', 'district': 'RA-40', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z82', 'city': 'Lincoln', 'district': 'RS-20', 'property_type': '', 'frontage': '120', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z83', 'city': 'Lincoln', 'district': 'RS-12', 'property_type': '', 'frontage': '100', 'lot_area': '12,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z84', 'city': 'Lincoln', 'district': 'RL-9', 'property_type': '', 'frontage': '75 (SF)', 'lot_area': '9,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Two-family; Affordable Two-Family: 10,500 SF'},
    {'id': 'z85', 'city': 'Lincoln', 'district': 'RG-7', 'property_type': '', 'frontage': '60 (SF)', 'lot_area': '7,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Multi-family: 7,000 SF + additional per unit'},
    {'id': 'z86', 'city': 'Little Compton', 'district': 'R (Residence)', 'property_type': '', 'frontage': '175', 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Frontage extends to depth of 175 ft; cul-de-sac: 105 ft'},
    {'id': 'z87', 'city': 'Narragansett', 'district': 'R-80', 'property_type': '', 'frontage': '200', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z88', 'city': 'Narragansett', 'district': 'R-40', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling; Other uses: 20,000 SF'},
    {'id': 'z89', 'city': 'Narragansett', 'district': 'R-20', 'property_type': '', 'frontage': '100', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z90', 'city': 'Narragansett', 'district': 'R-10', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z91', 'city': 'Narragansett', 'district': 'R-10A', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z92', 'city': 'Newport', 'district': 'R-3 & LB', 'property_type': '', 'frontage': '50', 'lot_area': '3,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z93', 'city': 'Newport', 'district': 'R-4', 'property_type': '', 'frontage': '50', 'lot_area': '4,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z94', 'city': 'Newport', 'district': 'R (45,000 SF conversion)', 'property_type': '', 'frontage': '', 'lot_area': '45,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z95', 'city': 'North Kingstown', 'district': 'RR/R80', 'property_type': '', 'frontage': '200', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z96', 'city': 'North Kingstown', 'district': 'PP', 'property_type': '', 'frontage': '200', 'lot_area': '5 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z97', 'city': 'North Kingstown', 'district': 'NR/R40', 'property_type': '', 'frontage': '180', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z98', 'city': 'North Kingstown', 'district': 'VR/R20', 'property_type': '', 'frontage': '140', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z99', 'city': 'North Kingstown', 'district': 'VLDR/200', 'property_type': '', 'frontage': '300', 'lot_area': '200,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z100', 'city': 'North Kingstown', 'district': 'LDR/120', 'property_type': '', 'frontage': '250', 'lot_area': '120,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z101', 'city': 'North Providence', 'district': 'RS-8', 'property_type': '', 'frontage': '70', 'lot_area': '8,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z102', 'city': 'North Providence', 'district': 'RS-12', 'property_type': '', 'frontage': '100', 'lot_area': '12,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z103', 'city': 'North Providence', 'district': 'RL-10', 'property_type': '', 'frontage': '100', 'lot_area': '8,000 SF + 7,000 SF for 2nd unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z104', 'city': 'North Providence', 'district': 'RL-13', 'property_type': '', 'frontage': '100', 'lot_area': '8,000 SF + 8,000 SF for 2nd unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z105', 'city': 'North Providence', 'district': 'RG', 'property_type': '', 'frontage': '70 (1F); 100 (2F+)', 'lot_area': "8,000 SF (1F); +6,000 SF per add'l unit", 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z106', 'city': 'North Smithfield', 'district': 'REA', 'property_type': '', 'frontage': '300', 'lot_area': '120,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family; other uses: 120,000 SF'},
    {'id': 'z107', 'city': 'North Smithfield', 'district': 'RA', 'property_type': '', 'frontage': '200', 'lot_area': '65,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Multi-family: +20,000 SF per bedroom'},
    {'id': 'z108', 'city': 'North Smithfield', 'district': 'RS', 'property_type': '', 'frontage': '200', 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Multi-family: +6,000 SF per unit'},
    {'id': 'z109', 'city': 'Portsmouth', 'district': 'R-10', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Min lot area per DU: 10,000 SF'},
    {'id': 'z110', 'city': 'Portsmouth', 'district': 'R-20', 'property_type': '', 'frontage': '110', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Min lot area per DU: 15,000 SF'},
    {'id': 'z111', 'city': 'Providence', 'district': 'R1A', 'property_type': '', 'frontage': '75 (not RH); None (RH)', 'lot_area': 'New subdivisions (not RH): 7,500 SF; RH: None', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z112', 'city': 'Providence', 'district': 'R1', 'property_type': '', 'frontage': '50 (not RH); None (RH)', 'lot_area': 'New subdivisions (not RH): 5,000 SF; RH: None', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z113', 'city': 'Providence', 'district': 'R2', 'property_type': '', 'frontage': '50 (not RH); None (RH)', 'lot_area': 'New subdivisions (not RH): 5,000 SF; RH: None', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z114', 'city': 'Providence', 'district': 'R3', 'property_type': '', 'frontage': '35 (not RH); None (RH)', 'lot_area': 'New subdivisions (not RH): 3,500 SF; RH: None', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z115', 'city': 'Providence', 'district': 'RP', 'property_type': '', 'frontage': '50 (not RH); None (RH)', 'lot_area': 'New subdivisions (not RH): 5,000 SF; RH: None', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z116', 'city': 'Richmond', 'district': 'R3', 'property_type': '', 'frontage': '300', 'lot_area': '3 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z117', 'city': 'Richmond', 'district': 'R-2', 'property_type': '', 'frontage': '200', 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z118', 'city': 'Richmond', 'district': 'R1', 'property_type': '', 'frontage': '150', 'lot_area': '1 acre', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z119', 'city': 'Richmond', 'district': 'NB', 'property_type': '', 'frontage': '150', 'lot_area': '1 acre', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z120', 'city': 'Scituate', 'district': 'RR-120', 'property_type': '', 'frontage': '300', 'lot_area': '120,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z121', 'city': 'Scituate', 'district': 'RS-120', 'property_type': '', 'frontage': '300', 'lot_area': '120,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z122', 'city': 'Scituate', 'district': 'RRW-60/80', 'property_type': '', 'frontage': '200', 'lot_area': '80,000 SF (no public water); 60,000 SF (public water)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z123', 'city': 'Smithfield', 'district': 'R-200', 'property_type': '', 'frontage': '300', 'lot_area': '200,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z124', 'city': 'Smithfield', 'district': 'R-80', 'property_type': '', 'frontage': '200', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z125', 'city': 'Smithfield', 'district': 'R-Med', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z126', 'city': 'Smithfield', 'district': 'R-20', 'property_type': '', 'frontage': '125', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z127', 'city': 'Smithfield', 'district': 'R-20M', 'property_type': '', 'frontage': '125 (1F); 150 (2F)', 'lot_area': '20,000 SF (1F); 40,000 SF (2F)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z128', 'city': 'Smithfield', 'district': 'MU', 'property_type': '', 'frontage': '125', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z129', 'city': 'Smithfield', 'district': 'PD', 'property_type': '', 'frontage': '300', 'lot_area': '200,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z130', 'city': 'Smithfield', 'district': 'Village', 'property_type': '', 'frontage': '150', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z131', 'city': 'South Kingstown', 'district': 'R200', 'property_type': '', 'frontage': '200', 'lot_area': '200,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z132', 'city': 'South Kingstown', 'district': 'R80', 'property_type': '', 'frontage': '200', 'lot_area': '80,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z133', 'city': 'South Kingstown', 'district': 'R40', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z134', 'city': 'South Kingstown', 'district': 'R30', 'property_type': '', 'frontage': '125', 'lot_area': '30,000 SF (single use); 45,000 SF (2-unit w/sewer); 60,000 SF (2-unit w/o sewer)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z135', 'city': 'South Kingstown', 'district': 'R20', 'property_type': '', 'frontage': '100', 'lot_area': '20,000 SF (single); 30,000 SF (2-unit w/sewer); 40,000 SF (2-unit w/o sewer)', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z136', 'city': 'Tiverton', 'district': 'R-30 (single-family)', 'property_type': '', 'frontage': '150', 'lot_area': '30,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z137', 'city': 'Tiverton', 'district': 'R-30 (two-family)', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z138', 'city': 'Tiverton', 'district': 'R-30 (three-family)', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z139', 'city': 'Tiverton', 'district': 'R-30 (multi-family 4+ units)', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF + 15,000 SF/unit above 2 + 7,500 SF/bedroom above 2', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z140', 'city': 'Tiverton', 'district': 'R-60 (single-family)', 'property_type': '', 'frontage': '175', 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z141', 'city': 'Tiverton', 'district': 'R-60 (two-family)', 'property_type': '', 'frontage': '175', 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z142', 'city': 'Tiverton', 'district': 'R-60 (multi-family 4+ units)', 'property_type': '', 'frontage': '175', 'lot_area': '60,000 SF + 15,000 SF/unit above 2 + 7,500 SF/bedroom above 2/unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z143', 'city': 'Warren', 'district': 'Residence 40 (single-family)', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z144', 'city': 'Warren', 'district': 'Residence 40 (other use)', 'property_type': '', 'frontage': '135', 'lot_area': '30,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z145', 'city': 'Warren', 'district': 'Residence 20 (single-family)', 'property_type': '', 'frontage': '120', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z146', 'city': 'Warren', 'district': 'Residence 15 (single-family)', 'property_type': '', 'frontage': '110', 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z147', 'city': 'Warren', 'district': 'Residence 10 (single-family)', 'property_type': '', 'frontage': '90', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z148', 'city': 'Warwick', 'district': 'A-7 / GB', 'property_type': '', 'frontage': '70', 'lot_area': '7,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z149', 'city': 'Warwick', 'district': 'A-10', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z150', 'city': 'Warwick', 'district': 'A-15', 'property_type': '', 'frontage': '125', 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z151', 'city': 'Warwick', 'district': 'A-40 / OS', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z152', 'city': 'West Greenwich', 'district': 'RFR-2', 'property_type': '', 'frontage': '200', 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z153', 'city': 'West Warwick', 'district': 'R-10 (single-family)', 'property_type': '', 'frontage': '80', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z154', 'city': 'West Warwick', 'district': 'R-8 (single-family)', 'property_type': '', 'frontage': '70', 'lot_area': '8,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z155', 'city': 'West Warwick', 'district': 'R-7.5 (single-family)', 'property_type': '', 'frontage': '70', 'lot_area': '7,500 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z156', 'city': 'West Warwick', 'district': 'R-6 (single-family)', 'property_type': '', 'frontage': '55', 'lot_area': '6,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z157', 'city': 'West Warwick', 'district': 'R-10 (two-family)', 'property_type': '', 'frontage': '80', 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z158', 'city': 'West Warwick', 'district': 'R-8 (two-family)', 'property_type': '', 'frontage': '70', 'lot_area': '12,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z159', 'city': 'West Warwick', 'district': 'R-7.5 (two-family)', 'property_type': '', 'frontage': '70', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z160', 'city': 'West Warwick', 'district': 'R-6 (two-family)', 'property_type': '', 'frontage': '55', 'lot_area': '8,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z161', 'city': 'Westerly', 'district': 'RR-60 (single-family)', 'property_type': '', 'frontage': '200', 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z162', 'city': 'Westerly', 'district': 'LDR-43 (single-family)', 'property_type': '', 'frontage': '200', 'lot_area': '43,560 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z163', 'city': 'Westerly', 'district': 'LDR-40 (single-family)', 'property_type': '', 'frontage': '150', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z164', 'city': 'Westerly', 'district': 'MDR-30 (single-family)', 'property_type': '', 'frontage': '120', 'lot_area': '30,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z165', 'city': 'Westerly', 'district': 'MDR-20 (single-family)', 'property_type': '', 'frontage': '100', 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z166', 'city': 'Woonsocket', 'district': 'R-1', 'property_type': '', 'frontage': '135', 'lot_area': '25,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z167', 'city': 'Woonsocket', 'district': 'R-2', 'property_type': '', 'frontage': '90', 'lot_area': '10,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z172', 'city': 'Burrillville', 'district': 'F-5', 'property_type': '', 'frontage': "450'", 'lot_area': '5 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z173', 'city': 'Burrillville', 'district': 'F-2', 'property_type': '', 'frontage': "300'", 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z174', 'city': 'Burrillville', 'district': 'R-12', 'property_type': '', 'frontage': "100' / 125'", 'lot_area': '12,000 SF / 15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z176', 'city': 'Charlestown', 'district': 'R-3A Multi Family', 'property_type': '', 'frontage': "300' + 20 per dwelling unit", 'lot_area': '3 Acres per Dwelling Unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z177', 'city': 'Charlestown', 'district': 'Village District', 'property_type': '', 'frontage': "120'", 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z178', 'city': 'Charlestown', 'district': 'R-40, R-2A, R-Aa Conservative Dev', 'property_type': '', 'frontage': "50'", 'lot_area': '20,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z179', 'city': 'Charlestown', 'district': 'C-3', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z180', 'city': 'Charlestown', 'district': 'Two Family Dwelling', 'property_type': '', 'frontage': "R-2A 250' Front / R-3A 300'", 'lot_area': '2 x min. lot size', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z182', 'city': 'Coventry', 'district': 'RR5', 'property_type': '', 'frontage': "300'", 'lot_area': '5 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z183', 'city': 'Coventry', 'district': 'RR3', 'property_type': '', 'frontage': "225'", 'lot_area': '3 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z184', 'city': 'Coventry', 'district': 'RR2', 'property_type': '', 'frontage': "225'", 'lot_area': '2 acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z185', 'city': 'Coventry', 'district': 'R20 (SF)', 'property_type': '', 'frontage': "120'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z186', 'city': 'Coventry', 'district': 'R20 (No public water)', 'property_type': '', 'frontage': "150'", 'lot_area': '1 acre', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z187', 'city': 'Coventry', 'district': 'R20 (2 Fam)', 'property_type': '', 'frontage': "175'", 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z188', 'city': 'Coventry', 'district': 'R20 (2 Fam no public water)', 'property_type': '', 'frontage': "175'", 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z189', 'city': 'Coventry', 'district': 'SF Cluster Devl (W/ water Or sewer)', 'property_type': '', 'frontage': "100'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z190', 'city': 'Coventry', 'district': '2 Fam Cluster Devl (W/ water Or sewer)', 'property_type': '', 'frontage': "125'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z191', 'city': 'Coventry', 'district': 'SF Cluster Devl (W/ no water Or sewer)', 'property_type': '', 'frontage': "150'", 'lot_area': '43,560 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z192', 'city': 'Coventry', 'district': '2 Fam Cluster Devl (W/ no water Or sewer)', 'property_type': '', 'frontage': "175'", 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z193', 'city': 'Coventry', 'district': 'SF Conservation Des (W/ water Or sewer)', 'property_type': '', 'frontage': "100'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z194', 'city': 'Coventry', 'district': 'MF Conservation Des (W/ water Or sewer)', 'property_type': '', 'frontage': "125'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z195', 'city': 'Coventry', 'district': 'SF Conservation Des (W/ water Or sewer)', 'property_type': '', 'frontage': "150'", 'lot_area': '1 acre', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z196', 'city': 'Coventry', 'district': '2 Fam Conservation Des (W/ water Or sewer)', 'property_type': '', 'frontage': "175'", 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z198', 'city': 'Cumberland', 'district': 'A-1 w/o water Or sewer', 'property_type': '', 'frontage': "250'", 'lot_area': '217,800 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z199', 'city': 'Cumberland', 'district': 'A-2 w/o water Or Sewer', 'property_type': '', 'frontage': "180'", 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '217,800sf per aditional dwelling unit'},
    {'id': 'z200', 'city': 'Cumberland', 'district': 'R-1 w/o water Or Sewer', 'property_type': '', 'frontage': "180'", 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '80,000 sf per additional dwelling unit'},
    {'id': 'z201', 'city': 'Cumberland', 'district': 'A-1 w/ water Or sewer But not both', 'property_type': '', 'frontage': "250'", 'lot_area': '217,800 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '80,000 sf per additional dwelling unit'},
    {'id': 'z202', 'city': 'Cumberland', 'district': 'A-2 w/ water Or sewer But not both', 'property_type': '', 'frontage': "180'", 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '217,800sf per aditional dwelling unit'},
    {'id': 'z203', 'city': 'Cumberland', 'district': 'R-1 w/ water Or sewer But not both', 'property_type': '', 'frontage': "100'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '80,000 sf per additional dwelling unit'},
    {'id': 'z204', 'city': 'Cumberland', 'district': 'R-2 w/ water Or sewer But not both', 'property_type': '', 'frontage': "90'", 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '40,000 sf per additional dwelling unit'},
    {'id': 'z205', 'city': 'Cumberland', 'district': 'R-3 w/ water Or sewer But not both', 'property_type': '', 'frontage': "90'", 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '10,000 sf for 2nd unit'},
    {'id': 'z206', 'city': 'Cumberland', 'district': 'A-1 w/ water & sewer', 'property_type': '', 'frontage': "250'", 'lot_area': '217,800 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '10,000 sf for 2nd unit'},
    {'id': 'z207', 'city': 'Cumberland', 'district': 'A-2 w/ water & sewer', 'property_type': '', 'frontage': "180'", 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z208', 'city': 'Cumberland', 'district': 'R-1 w/ water & sewer', 'property_type': '', 'frontage': "100'", 'lot_area': '25,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z209', 'city': 'Cumberland', 'district': 'R-2 w/ water & sewer', 'property_type': '', 'frontage': "40'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z210', 'city': 'Cumberland', 'district': 'R-3 w/ water & sewer', 'property_type': '', 'frontage': "40'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': '5,000 sf for 2nd unit'},
    {'id': 'z212', 'city': 'East Greenwich', 'district': 'R-6 (SF)', 'property_type': '', 'frontage': "60'", 'lot_area': '6,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z213', 'city': 'East Greenwich', 'district': 'R-6 (2 Fam)', 'property_type': '', 'frontage': "80'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z214', 'city': 'East Greenwich', 'district': 'R-6 (Multi)', 'property_type': '', 'frontage': "100'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z216', 'city': 'Glocester', 'district': 'A-4 (Two Fam)', 'property_type': '', 'frontage': "350'", 'lot_area': '6 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z217', 'city': 'Glocester', 'district': 'A-3 (SF)', 'property_type': '', 'frontage': "300'", 'lot_area': '3 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z218', 'city': 'Glocester', 'district': 'A-3 (Two Fam)', 'property_type': '', 'frontage': "350'", 'lot_area': '6 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z219', 'city': 'Glocester', 'district': 'R-2 (SF)', 'property_type': '', 'frontage': "250'", 'lot_area': '2 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z220', 'city': 'Glocester', 'district': 'R-2 (Two Fam)', 'property_type': '', 'frontage': "300'", 'lot_area': '5 Acres', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z221', 'city': 'Glocester', 'district': 'R-2 (Multi)', 'property_type': '', 'frontage': "300'", 'lot_area': '4 Acres Per Unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z223', 'city': 'Hopkinton', 'district': 'R-1 New Sub div', 'property_type': '', 'frontage': "100'", 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z225', 'city': 'Jamestown', 'district': 'OS', 'property_type': '', 'frontage': "300'", 'lot_area': '200,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z226', 'city': 'Jamestown', 'district': 'RR-200', 'property_type': '', 'frontage': "300'", 'lot_area': '200,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z227', 'city': 'Jamestown', 'district': 'RR-80', 'property_type': '', 'frontage': "200'", 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z228', 'city': 'Jamestown', 'district': 'R-400', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z229', 'city': 'Jamestown', 'district': 'R-20', 'property_type': '', 'frontage': "100'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z230', 'city': 'Jamestown', 'district': 'R-20 2 Fam', 'property_type': '', 'frontage': "100'", 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z231', 'city': 'Jamestown', 'district': 'R-20 Multi-Fam', 'property_type': '', 'frontage': "100'", 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z232', 'city': 'Jamestown', 'district': 'R-8', 'property_type': '', 'frontage': "80'", 'lot_area': '8,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z233', 'city': 'Jamestown', 'district': 'R-8 2 Fam', 'property_type': '', 'frontage': "80'", 'lot_area': '12,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z234', 'city': 'Jamestown', 'district': 'R-8 Multi-Fam', 'property_type': '', 'frontage': "80'", 'lot_area': '25,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z235', 'city': 'Jamestown', 'district': 'CL', 'property_type': '', 'frontage': "80' min-120' max", 'lot_area': '8,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z236', 'city': 'Jamestown', 'district': 'CL 2 Fam', 'property_type': '', 'frontage': "80' min-120' max", 'lot_area': '8,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z237', 'city': 'Jamestown', 'district': 'CL Multi-Fam', 'property_type': '', 'frontage': "80' min-120' max", 'lot_area': '25,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z238', 'city': 'Jamestown', 'district': 'CD', 'property_type': '', 'frontage': "40' min- 96' max", 'lot_area': '5,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z239', 'city': 'Jamestown', 'district': 'CD 2 Fam', 'property_type': '', 'frontage': "40' min- 96' max", 'lot_area': '5,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z240', 'city': 'Jamestown', 'district': 'CS Multi-Fam', 'property_type': '', 'frontage': "40' min- 96' max", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z242', 'city': 'Johnston', 'district': 'R-20', 'property_type': '', 'frontage': "120'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z243', 'city': 'Johnston', 'district': 'R-15', 'property_type': '', 'frontage': "100'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z244', 'city': 'Johnston', 'district': 'R-10 SF', 'property_type': '', 'frontage': "100'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z245', 'city': 'Johnston', 'district': 'R-10 Duplex', 'property_type': '', 'frontage': "150'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z246', 'city': 'Johnston', 'district': 'R-10 2 Fam', 'property_type': '', 'frontage': "120'", 'lot_area': '12,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z247', 'city': 'Johnston', 'district': 'R-7 SF', 'property_type': '', 'frontage': "70'", 'lot_area': '7,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z248', 'city': 'Johnston', 'district': 'R-7 Duplex', 'property_type': '', 'frontage': "120'", 'lot_area': '12,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z249', 'city': 'Johnston', 'district': 'R-7 2 Fam', 'property_type': '', 'frontage': "85'", 'lot_area': '8,500 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z251', 'city': 'Lincoln', 'district': 'RL-9 2 Fam', 'property_type': '', 'frontage': "100'", 'lot_area': '12,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z252', 'city': 'Lincoln', 'district': 'RG-7 2 Fam', 'property_type': '', 'frontage': "70'", 'lot_area': '8,500 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z253', 'city': 'Lincoln', 'district': 'RG-7 Multi', 'property_type': '', 'frontage': "60' + 10' for ea unit over 1", 'lot_area': '7,000 sf + 1,500sf for ea unit over one', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z255', 'city': 'Middletown', 'district': 'R-60', 'property_type': '', 'frontage': "200'", 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z256', 'city': 'Middletown', 'district': 'R-30', 'property_type': '', 'frontage': "130'", 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z257', 'city': 'Middletown', 'district': 'R-20', 'property_type': '', 'frontage': "120'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z258', 'city': 'Middletown', 'district': 'R-20 2 Fam', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z259', 'city': 'Middletown', 'district': 'R-10', 'property_type': '', 'frontage': "100'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z260', 'city': 'Middletown', 'district': 'R-10 2 Fam', 'property_type': '', 'frontage': "120'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z261', 'city': 'Middletown', 'district': 'RM', 'property_type': '', 'frontage': "100'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z262', 'city': 'Middletown', 'district': 'RM 2 Fam', 'property_type': '', 'frontage': "120'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z263', 'city': 'Middletown', 'district': 'RM Multi', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z264', 'city': 'Middletown', 'district': 'LB', 'property_type': '', 'frontage': "100'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z265', 'city': 'Middletown', 'district': 'LB 2 Fam', 'property_type': '', 'frontage': "120'", 'lot_area': '15,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z266', 'city': 'Middletown', 'district': 'LB Multi', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z267', 'city': 'Middletown', 'district': 'OB', 'property_type': '', 'frontage': "120'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z268', 'city': 'Middletown', 'district': 'OB 2 Fam', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z269', 'city': 'Middletown', 'district': 'OB Multi', 'property_type': '', 'frontage': "150'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z271', 'city': 'Narragansett', 'district': 'R-80 Duplex', 'property_type': '', 'frontage': '200', 'lot_area': '100,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z272', 'city': 'Narragansett', 'district': 'R-40', 'property_type': '', 'frontage': '150', 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z274', 'city': 'Newport', 'district': 'R-6', 'property_type': '', 'frontage': "50'", 'lot_area': '6,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z275', 'city': 'Newport', 'district': 'R-10 & R10A', 'property_type': '', 'frontage': "80'", 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z276', 'city': 'Newport', 'district': 'R-20', 'property_type': '', 'frontage': "100'", 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z277', 'city': 'Newport', 'district': 'R-40A', 'property_type': '', 'frontage': "200'", 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z278', 'city': 'Newport', 'district': 'R-60', 'property_type': '', 'frontage': "200'", 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z279', 'city': 'Newport', 'district': 'R-120', 'property_type': '', 'frontage': "300'", 'lot_area': '120,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z280', 'city': 'Newport', 'district': 'R-160', 'property_type': '', 'frontage': "400'", 'lot_area': '160,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z281', 'city': 'Newport', 'district': 'WBD & GBD', 'property_type': '', 'frontage': "50'", 'lot_area': '5,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z283', 'city': 'North Kingstown', 'district': 'VR/R20 2 Fam', 'property_type': '', 'frontage': '160', 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z285', 'city': 'North Smithfield', 'district': 'RA 2 Fam', 'property_type': '', 'frontage': '200', 'lot_area': '130,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z286', 'city': 'North Smithfield', 'district': 'RS Multo', 'property_type': '', 'frontage': '175', 'lot_area': '80,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z287', 'city': 'North Smithfield', 'district': 'RA Multi', 'property_type': '', 'frontage': '200', 'lot_area': '65,000 sf + 20,000 per bedroom', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z288', 'city': 'North Smithfield', 'district': 'RS Multi', 'property_type': '', 'frontage': "200'", 'lot_area': '40,000 sf + 6,000 per bedroom', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z289', 'city': 'North Smithfield', 'district': 'RU', 'property_type': '', 'frontage': '100', 'lot_area': '20,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z290', 'city': 'North Smithfield', 'district': 'RU 2 Fam', 'property_type': '', 'frontage': '120', 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z291', 'city': 'North Smithfield', 'district': 'RU Multi', 'property_type': '', 'frontage': '200', 'lot_area': '6,000 sf + 4,000 per bedroom', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z293', 'city': 'Pawtucket', 'district': 'RL', 'property_type': '', 'frontage': "90'", 'lot_area': 'Existing Lots 0sf / New Lots 9,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z294', 'city': 'Pawtucket', 'district': 'RS Single', 'property_type': '', 'frontage': "50'", 'lot_area': 'Existing Lots 0sf / New Lots 5,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z295', 'city': 'Pawtucket', 'district': 'RS Other Res', 'property_type': '', 'frontage': '75', 'lot_area': 'Existing Lots 0 sf / New Lots 7,500 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z296', 'city': 'Pawtucket', 'district': 'RT Single', 'property_type': '', 'frontage': '50', 'lot_area': 'Existing Lots 0 sf / New Lots 5,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z297', 'city': 'Pawtucket', 'district': 'RT 2 Fam', 'property_type': '', 'frontage': '75', 'lot_area': '7,500 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z298', 'city': 'Pawtucket', 'district': 'RT Other Res', 'property_type': '', 'frontage': '75', 'lot_area': 'Existing Lots 0 sf / New Lots 7,500 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z299', 'city': 'Pawtucket', 'district': 'RM Single', 'property_type': '', 'frontage': '50', 'lot_area': 'Existing Lots 0 sf / New Lots 5,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z300', 'city': 'Pawtucket', 'district': 'RM 2 Fam', 'property_type': '', 'frontage': '75', 'lot_area': '7,500 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z301', 'city': 'Pawtucket', 'district': 'RM 3 Fam', 'property_type': '', 'frontage': '100', 'lot_area': '10,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z302', 'city': 'Pawtucket', 'district': 'RM Multi', 'property_type': '', 'frontage': '100', 'lot_area': '3,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z304', 'city': 'Portsmouth', 'district': 'R-30', 'property_type': '', 'frontage': '125', 'lot_area': '30,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z305', 'city': 'Portsmouth', 'district': 'R-40', 'property_type': '', 'frontage': '125', 'lot_area': '40,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z306', 'city': 'Portsmouth', 'district': 'R-60', 'property_type': '', 'frontage': '200', 'lot_area': '60,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z308', 'city': 'Providence', 'district': 'No Zoning For Existing Lots', 'property_type': '', 'frontage': '', 'lot_area': '', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z310', 'city': 'Warren', 'district': 'Residence 20 (2 Fam-family)', 'property_type': '', 'frontage': '140', 'lot_area': '30,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z311', 'city': 'Warren', 'district': 'Residence 10 (2 Fam-family)', 'property_type': '', 'frontage': '110', 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z312', 'city': 'Warren', 'district': 'Residence 6 (single-family)', 'property_type': '', 'frontage': '60', 'lot_area': '6,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z313', 'city': 'Warren', 'district': 'Residence 6 (2 Fam-family)', 'property_type': '', 'frontage': '70', 'lot_area': '8,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z314', 'city': 'Warren', 'district': 'Residence 6 (3 Fam-family)', 'property_type': '', 'frontage': '72', 'lot_area': '9,500 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z315', 'city': 'Warren', 'district': 'Residence 6 (4 Fam-family)', 'property_type': '', 'frontage': '74', 'lot_area': '11,000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z317', 'city': 'West Greenwich', 'district': 'RFR-1', 'property_type': '', 'frontage': '150', 'lot_area': '1 acre', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z319', 'city': 'West Warwick', 'district': 'R-7.5 (multi-family)', 'property_type': '', 'frontage': '70', 'lot_area': '10,000 SF +7,500 for ea additional unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z320', 'city': 'West Warwick', 'district': 'R-6 (multi-family)', 'property_type': '', 'frontage': '55', 'lot_area': '10,000 SF +7,500 for ea additional unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z321', 'city': 'West Warwick', 'district': 'VC', 'property_type': '', 'frontage': '', 'lot_area': '10,000 SF +7,500 for ea additional unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z323', 'city': 'Westerly', 'district': 'HDR-15 (Single Family)', 'property_type': '', 'frontage': '100', 'lot_area': '15000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z324', 'city': 'Westerly', 'district': 'HDR-15 (Multi)', 'property_type': '', 'frontage': '150', 'lot_area': '4 acres + 15,000 per unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z325', 'city': 'Westerly', 'district': 'HDR-10 (Single Family)', 'property_type': '', 'frontage': '80', 'lot_area': '10000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z326', 'city': 'Westerly', 'district': 'HDR-6 (Single Family)', 'property_type': '', 'frontage': '60', 'lot_area': '6000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z327', 'city': 'Westerly', 'district': 'HDR-6 (2 Fam)', 'property_type': '', 'frontage': '100', 'lot_area': '12000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z328', 'city': 'Westerly', 'district': 'HDR-6 (3 Fam)', 'property_type': '', 'frontage': '120', 'lot_area': '18000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z329', 'city': 'Westerly', 'district': 'HDR-6 (Multi)', 'property_type': '', 'frontage': '60', 'lot_area': '2 acres plus 6,000 per unit', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z330', 'city': 'Westerly', 'district': 'P-15 & NB', 'property_type': '', 'frontage': '', 'lot_area': 'Conforms to nearest residential zone', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z331', 'city': 'Westerly', 'district': 'Downtown Center 2', 'property_type': '', 'frontage': '', 'lot_area': 'Conforms to HDR-6', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z333', 'city': 'Barrington', 'district': 'R-40 CD (2 Fam)', 'property_type': '', 'frontage': "180' SINGLE FAM / 100'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '50,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Two-family dwellings'},
    {'id': 'z334', 'city': 'Barrington', 'district': 'R-25 (SF ADU or GH)', 'property_type': '', 'frontage': "90' SINGLE FAM / 60'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '40,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling with accessory living quarters or guest house'},
    {'id': 'z335', 'city': 'Barrington', 'district': 'R-10 (SF ADU or GH)', 'property_type': '', 'frontage': "90' SINGLE FAM", 'lot_area': 'N/A', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling with accessory living quarters or guest house'},
    {'id': 'z337', 'city': 'Barrington', 'district': 'R-40 CD (SF ADU or GH)', 'property_type': '', 'frontage': "180' SINGLE FAM / 100'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '60,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Single-family dwelling with accessory living quarters or guest house'},
    {'id': 'z338', 'city': 'Barrington', 'district': 'R-25 (2 Fam or Other)', 'property_type': '', 'frontage': "90' SINGLE FAM / 60'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '30,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Two-family dwellings or  Other permitted or special use permit uses'},
    {'id': 'z339', 'city': 'Barrington', 'district': 'R-10 (2 Fam or Other)', 'property_type': '', 'frontage': "60' TWO FAM & OTHER PERMITED USES", 'lot_area': '15,000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Two-family dwellings or  Other permitted or special use permit uses'},
    {'id': 'z341', 'city': 'Barrington', 'district': 'R-40 CD (Other)', 'property_type': '', 'frontage': "180' SINGLE FAM / 100'  Street frontage allowed where a lot abuts a cul-de-sac or an outside curb of a street", 'lot_area': '80,0000 SF', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': 'Other permitted or special use permit uses'},
    {'id': 'z343', 'city': 'Woonsocket', 'district': 'R-1', 'property_type': '', 'frontage': '135', 'lot_area': '25000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z344', 'city': 'Woonsocket', 'district': 'R-2', 'property_type': '', 'frontage': '90', 'lot_area': '10000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z345', 'city': 'Woonsocket', 'district': 'R-3', 'property_type': '', 'frontage': '70 for SF 80 for Multi', 'lot_area': '7000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z346', 'city': 'Woonsocket', 'district': 'R-4', 'property_type': '', 'frontage': '60 for SF + 10 for ea additional unit', 'lot_area': '6000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z347', 'city': 'Woonsocket', 'district': 'C-1, C-2 & MU-2', 'property_type': '', 'frontage': '', 'lot_area': '6000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
    {'id': 'z348', 'city': 'Woonsocket', 'district': 'MU-I', 'property_type': '', 'frontage': '60 for SF + 10 for ea additional unit', 'lot_area': '6000 sf', 'lot_width': '', 'front_yard': '', 'side_yard': '', 'rear_yard': '', 'max_height': '', 'max_lot_cov': '', 'max_floors': '', 'notes': ''},
]

# ── Storage ───────────────────────────────────────────────────────────────────
def load_data(key, filepath, default):
    try:
        raw = st.session_state.get(key)
        if raw:
            parsed = json.loads(raw)
            if parsed:
                return parsed
    except Exception:
        pass
    try:
        path = os.path.join(os.path.dirname(__file__), filepath)
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception:
        pass
    return [item.copy() for item in default]

def save_data(key, filepath, data):
    st.session_state[key] = json.dumps(data)
    try:
        path = os.path.join(os.path.dirname(__file__), filepath)
        with open(path, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

def load_revisions():
    return load_data("_rc_revisions", "rc_revisions.json", DEFAULT_REVISIONS)

def save_revisions(data):
    save_data("_rc_revisions", "rc_revisions.json", data)

def load_neighborhoods():
    return load_data("_rc_neighborhoods", "rc_neighborhoods.json", [])

def save_neighborhoods(data):
    save_data("_rc_neighborhoods", "rc_neighborhoods.json", data)

def load_zoning():
    return load_data("_rc_zoning", "rc_zoning.json", DEFAULT_ZONING)

def save_zoning(data):
    save_data("_rc_zoning", "rc_zoning.json", data)

def load_comments():
    return load_data("_rc_comments", "rc_comments.json", DEFAULT_COMMENTS)

def save_comments(data):
    save_data("_rc_comments", "rc_comments.json", data)

# ── Password ──────────────────────────────────────────────────────────────────
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=200)
    st.title("A-Tech Appraisal Co.")
    st.subheader("Revision & Comment Library")
    st.divider()
    pwd = st.text_input("Enter password to continue", type="password", key="pwd_input")
    if st.button("Login", use_container_width=True):
        try:
            correct = st.secrets["APP_PASSWORD"]
        except Exception:
            correct = os.environ.get("APP_PASSWORD", "atech2026")
        if pwd == correct:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="A-Tech R&C Library",
    page_icon="📚",
    layout="centered"
)

if not check_password():
    st.stop()

# ── Sidebar Navigation ────────────────────────────────────────────────────────
with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, width=180)
    st.title("A-Tech R&C Library")
    st.divider()
    selection = st.selectbox(
        "Select a Tool",
        [
            "📋 Revision Responses",
            "📝 Appraisal Comments",
            "🏘️ Neighborhood Descriptions",
            "📐 Zoning Districts",
            "🆕 UAD 3.6 Reference",
            "✅ QC Checker",
        ],
        label_visibility="collapsed"
    )
    st.divider()
    st.caption("A-Tech Appraisal Co. — Field Reference")

# ── Main Header ───────────────────────────────────────────────────────────────
st.title(selection)
st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REVISION RESPONSES
# ══════════════════════════════════════════════════════════════════════════════
if selection == "📋 Revision Responses":
    revisions = load_revisions()

    col_rs, col_ra = st.columns([4, 1])
    with col_rs:
        rev_search = st.text_input("🔍 Search", placeholder="Type keyword to filter...", key="rev_search")
    with col_ra:
        st.write("")
        st.write("")
        if st.button("➕ Add New", key="add_rev_btn", use_container_width=True):
            st.session_state["show_add_rev"] = not st.session_state.get("show_add_rev", False)

    if st.session_state.get("show_add_rev"):
        with st.container():
            st.divider()
            st.subheader("New Revision Response")
            nr_cat  = st.text_input("Category / Title *", key="nr_cat",
                                     placeholder="e.g. Comp Distance — Exceeded Guidelines")
            nr_req  = st.text_area("AMC / Lender Request (optional)", key="nr_req",
                                    height=80, placeholder="Paste the revision request here...")
            nr_resp = st.text_area("Your Response *", key="nr_resp",
                                    height=140, placeholder="Write your response here...")
            nr_note = st.text_input("Notes (optional)", key="nr_note",
                                     placeholder="e.g. Customize the distance threshold")
            rc1, rc2 = st.columns(2)
            with rc1:
                if st.button("💾 Save Revision", use_container_width=True, key="save_rev"):
                    if not nr_cat.strip() or not nr_resp.strip():
                        st.error("Category and Response are required.")
                    else:
                        import uuid
                        revisions.append({
                            "id":       str(uuid.uuid4())[:8],
                            "category": nr_cat.strip(),
                            "request":  nr_req.strip(),
                            "response": nr_resp.strip(),
                            "notes":    nr_note.strip(),
                        })
                        save_revisions(revisions)
                        st.session_state["show_add_rev"] = False
                        st.success("✅ Revision saved.")
                        st.rerun()
            with rc2:
                if st.button("Cancel", use_container_width=True, key="cancel_rev"):
                    st.session_state["show_add_rev"] = False
                    st.rerun()
            st.divider()

    filtered_revs = revisions
    if rev_search:
        q = rev_search.lower()
        filtered_revs = [r for r in revisions if
                         q in r.get("category","").lower() or
                         q in r.get("request","").lower() or
                         q in r.get("response","").lower()]

    st.write(f"**{len(filtered_revs)} entr{'y' if len(filtered_revs)==1 else 'ies'}**")
    st.divider()

    for rev in filtered_revs:
        with st.expander(f"📋 {rev.get('category','Untitled')}"):
            if rev.get("request"):
                st.markdown("**AMC / Lender Request:**")
                st.info(rev["request"])
            st.markdown("**Appraiser Response:**")
            st.text_area(
                "Copy the text below:",
                value=rev.get("response",""),
                height=160,
                key=f"rev_text_{rev['id']}"
            )
            if rev.get("notes"):
                st.caption(f"📝 Note: {rev['notes']}")
            st.write("")
            if st.button("🗑️ Delete this entry", key=f"del_rev_{rev['id']}"):
                revisions = [r for r in revisions if r["id"] != rev["id"]]
                save_revisions(revisions)
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — APPRAISAL COMMENTS
# ══════════════════════════════════════════════════════════════════════════════
elif selection == "📝 Appraisal Comments":
    comments = load_comments()

    col_cs, col_ca = st.columns([4, 1])
    with col_cs:
        com_search = st.text_input("🔍 Search", placeholder="Type keyword to filter...", key="com_search")
    with col_ca:
        st.write("")
        st.write("")
        if st.button("➕ Add New", key="add_com_btn", use_container_width=True):
            st.session_state["show_add_com"] = not st.session_state.get("show_add_com", False)

    if st.session_state.get("show_add_com"):
        with st.container():
            st.divider()
            st.subheader("New Appraisal Comment")
            nc_cat  = st.text_input("Category / Title *", key="nc_cat",
                                     placeholder="e.g. Waterfront Adjustment — Coastal RI")
            nc_text = st.text_area("Comment Text *", key="nc_text",
                                    height=140, placeholder="Write the addendum language here...")
            nc_note = st.text_input("Notes (optional)", key="nc_note",
                                     placeholder="e.g. Use on all coastal assignments")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("💾 Save Comment", use_container_width=True, key="save_com"):
                    if not nc_cat.strip() or not nc_text.strip():
                        st.error("Category and Comment text are required.")
                    else:
                        import uuid
                        comments.append({
                            "id":       str(uuid.uuid4())[:8],
                            "category": nc_cat.strip(),
                            "text":     nc_text.strip(),
                            "notes":    nc_note.strip(),
                        })
                        save_comments(comments)
                        st.session_state["show_add_com"] = False
                        st.success("✅ Comment saved.")
                        st.rerun()
            with cc2:
                if st.button("Cancel", use_container_width=True, key="cancel_com"):
                    st.session_state["show_add_com"] = False
                    st.rerun()
            st.divider()

    filtered_coms = comments
    if com_search:
        q = com_search.lower()
        filtered_coms = [c for c in comments if
                         q in c.get("category","").lower() or
                         q in c.get("text","").lower()]

    st.write(f"**{len(filtered_coms)} entr{'y' if len(filtered_coms)==1 else 'ies'}**")
    st.divider()

    for com in filtered_coms:
        with st.expander(f"📝 {com.get('category','Untitled')}"):
            st.text_area(
                "Copy the text below:",
                value=com.get("text",""),
                height=160,
                key=f"com_text_{com['id']}"
            )
            if com.get("notes"):
                st.caption(f"📝 Note: {com['notes']}")
            st.write("")
            if st.button("🗑️ Delete this entry", key=f"del_com_{com['id']}"):
                comments = [c for c in comments if c["id"] != com["id"]]
                save_comments(comments)
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — NEIGHBORHOOD DESCRIPTIONS
# ══════════════════════════════════════════════════════════════════════════════
elif selection == "🏘️ Neighborhood Descriptions":
    neighborhoods = load_neighborhoods()

    st.subheader("🏘️ Neighborhood Descriptions")
    st.caption("Sorted by City — Neighborhood. Add descriptions as you complete assignments.")

    col_hs, col_ha = st.columns([4, 1])
    with col_hs:
        hood_search = st.text_input("🔍 Search", placeholder="Type city or neighborhood...", key="hood_search")
    with col_ha:
        st.write("")
        st.write("")
        if st.button("➕ Add New", key="add_hood_btn", use_container_width=True):
            st.session_state["show_add_hood"] = not st.session_state.get("show_add_hood", False)

    if st.session_state.get("show_add_hood"):
        with st.container():
            st.divider()
            st.subheader("New Neighborhood Description")
            nh_city  = st.text_input("City *", key="nh_city", placeholder="e.g. Providence")
            nh_hood  = st.text_input("Neighborhood *", key="nh_hood", placeholder="e.g. Fox Point")
            nh_desc  = st.text_area("Description *", key="nh_desc", height=140,
                                     placeholder="Write the neighborhood description here. Include character, housing stock, amenities, market activity, etc...")
            nh_note  = st.text_input("Notes (optional)", key="nh_note",
                                      placeholder="e.g. Last updated March 2026")
            hc1, hc2 = st.columns(2)
            with hc1:
                if st.button("💾 Save Description", use_container_width=True, key="save_hood"):
                    if not nh_city.strip() or not nh_hood.strip() or not nh_desc.strip():
                        st.error("City, Neighborhood, and Description are required.")
                    else:
                        import uuid
                        neighborhoods.append({
                            "id":           str(uuid.uuid4())[:8],
                            "city":         nh_city.strip(),
                            "neighborhood": nh_hood.strip(),
                            "description":  nh_desc.strip(),
                            "notes":        nh_note.strip(),
                        })
                        save_neighborhoods(neighborhoods)
                        st.session_state["show_add_hood"] = False
                        st.success("✅ Neighborhood description saved.")
                        st.rerun()
            with hc2:
                if st.button("Cancel", use_container_width=True, key="cancel_hood"):
                    st.session_state["show_add_hood"] = False
                    st.rerun()
            st.divider()

    # Filter and sort
    filtered_hoods = sorted(neighborhoods, key=lambda x: f"{x.get('city','')} {x.get('neighborhood','')}")
    if hood_search:
        q = hood_search.lower()
        filtered_hoods = [h for h in filtered_hoods if
                          q in h.get("city","").lower() or
                          q in h.get("neighborhood","").lower() or
                          q in h.get("description","").lower()]

    st.write(f"**{len(filtered_hoods)} entr{'y' if len(filtered_hoods)==1 else 'ies'}**")
    st.divider()

    if filtered_hoods:
        for hood in filtered_hoods:
            label = f"🏘️ {hood.get('city','')} — {hood.get('neighborhood','')}"
            with st.expander(label):
                st.text_area(
                    "Copy the description below:",
                    value=hood.get("description",""),
                    height=160,
                    key=f"hood_text_{hood['id']}"
                )
                if hood.get("notes"):
                    st.caption(f"📝 Note: {hood['notes']}")
                st.write("")
                if st.button("🗑️ Delete this entry", key=f"del_hood_{hood['id']}"):
                    neighborhoods = [h for h in neighborhoods if h["id"] != hood["id"]]
                    save_neighborhoods(neighborhoods)
                    st.rerun()
    else:
        st.info("No neighborhood descriptions yet. Add your first one above.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — ZONING DISTRICTS
# ══════════════════════════════════════════════════════════════════════════════
elif selection == "📐 Zoning Districts":
    zoning = load_zoning()

    st.subheader("📐 Zoning Districts & Dimensional Regulations")
    st.caption("Sorted by City — Zoning District — Property Type.")

    col_zs, col_za = st.columns([4, 1])
    with col_zs:
        zone_search = st.text_input("🔍 Search", placeholder="Type city, district, or property type...", key="zone_search")
    with col_za:
        st.write("")
        st.write("")
        if st.button("➕ Add New", key="add_zone_btn", use_container_width=True):
            st.session_state["show_add_zone"] = not st.session_state.get("show_add_zone", False)

    if st.session_state.get("show_add_zone"):
        with st.container():
            st.divider()
            st.subheader("New Zoning District")
            zc1, zc2, zc3 = st.columns(3)
            with zc1:
                nz_city     = st.text_input("City *", key="nz_city", placeholder="e.g. Providence")
            with zc2:
                nz_district = st.text_input("Zoning District *", key="nz_district", placeholder="e.g. A-7")
            with zc3:
                nz_proptype = st.text_input("Property Type *", key="nz_proptype", placeholder="e.g. Single Family")

            st.write("**Dimensional Requirements:**")
            zd1, zd2, zd3 = st.columns(3)
            with zd1:
                nz_frontage = st.text_input("Min Frontage", key="nz_frontage", placeholder="e.g. 50 ft")
            with zd2:
                nz_lotarea  = st.text_input("Min Lot Area", key="nz_lotarea", placeholder="e.g. 6,000 sq ft")
            with zd3:
                nz_lotwidth = st.text_input("Min Lot Width", key="nz_lotwidth", placeholder="e.g. 50 ft")

            zd4, zd5, zd6 = st.columns(3)
            with zd4:
                nz_frontyard = st.text_input("Front Yard Setback", key="nz_frontyard", placeholder="e.g. 20 ft")
            with zd5:
                nz_sideyard  = st.text_input("Side Yard Setback", key="nz_sideyard", placeholder="e.g. 5 ft each")
            with zd6:
                nz_rearyard  = st.text_input("Rear Yard Setback", key="nz_rearyard", placeholder="e.g. 20 ft")

            zd7, zd8, zd9 = st.columns(3)
            with zd7:
                nz_maxheight = st.text_input("Max Building Height", key="nz_maxheight", placeholder="e.g. 35 ft")
            with zd8:
                nz_maxlotcov = st.text_input("Max Lot Coverage", key="nz_maxlotcov", placeholder="e.g. 40%")
            with zd9:
                nz_maxfloors = st.text_input("Max Stories", key="nz_maxfloors", placeholder="e.g. 2.5")

            nz_notes = st.text_input("Additional Notes (optional)", key="nz_notes",
                                      placeholder="e.g. Corner lots may have reduced side yard; source: Providence Zoning Ordinance 2024")

            zb1, zb2 = st.columns(2)
            with zb1:
                if st.button("💾 Save Zoning District", use_container_width=True, key="save_zone"):
                    if not nz_city.strip() or not nz_district.strip() or not nz_proptype.strip():
                        st.error("City, Zoning District, and Property Type are required.")
                    else:
                        import uuid
                        zoning.append({
                            "id":            str(uuid.uuid4())[:8],
                            "city":          nz_city.strip(),
                            "district":      nz_district.strip(),
                            "property_type": nz_proptype.strip(),
                            "frontage":      nz_frontage.strip(),
                            "lot_area":      nz_lotarea.strip(),
                            "lot_width":     nz_lotwidth.strip(),
                            "front_yard":    nz_frontyard.strip(),
                            "side_yard":     nz_sideyard.strip(),
                            "rear_yard":     nz_rearyard.strip(),
                            "max_height":    nz_maxheight.strip(),
                            "max_lot_cov":   nz_maxlotcov.strip(),
                            "max_floors":    nz_maxfloors.strip(),
                            "notes":         nz_notes.strip(),
                        })
                        save_zoning(zoning)
                        st.session_state["show_add_zone"] = False
                        st.success("✅ Zoning district saved.")
                        st.rerun()
            with zb2:
                if st.button("Cancel", use_container_width=True, key="cancel_zone"):
                    st.session_state["show_add_zone"] = False
                    st.rerun()
            st.divider()

    # Filter and sort
    filtered_zones = sorted(zoning, key=lambda x: f"{x.get('city','')} {x.get('district','')} {x.get('property_type','')}")
    if zone_search:
        q = zone_search.lower()
        filtered_zones = [z for z in filtered_zones if
                          q in z.get("city","").lower() or
                          q in z.get("district","").lower() or
                          q in z.get("property_type","").lower()]

    st.write(f"**{len(filtered_zones)} entr{'y' if len(filtered_zones)==1 else 'ies'}**")
    st.divider()

    if filtered_zones:
        for zone in filtered_zones:
            label = f"📐 {zone.get('city','')} — {zone.get('district','')} — {zone.get('property_type','')}"
            with st.expander(label):
                # Display only the key fields
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**Min Lot Frontage**")
                    st.write(zone.get("frontage","—") or "—")
                with col_b:
                    st.markdown("**Min Lot Area**")
                    st.write(zone.get("lot_area","—") or "—")

                if zone.get("notes"):
                    st.markdown("**📝 Notes**")
                    st.info(zone["notes"])
                st.write("")
                if st.button("🗑️ Delete this entry", key=f"del_zone_{zone['id']}"):
                    zoning = [z for z in zoning if z["id"] != zone["id"]]
                    save_zoning(zoning)
                    st.rerun()
    else:
        st.info("No zoning districts saved yet. Add your first entry above.")

# ══════════════════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — UAD 3.6 REFERENCE
# ══════════════════════════════════════════════════════════════════════════════
elif selection == "🆕 UAD 3.6 Reference":
    st.subheader("🆕 UAD 3.6 Reference Guide")
    st.caption("Key changes, inspection requirements, ratings definitions, and tool overview. Mandatory November 2, 2026.")

    st.info("⏱️ **Key Dates:** Broad Production started Jan 26, 2026 — both 2.6 and 3.6 accepted now. **Mandatory Nov 2, 2026** — all legacy forms (1004, 1073, 2055, etc.) retired. UAD 2.6 pipeline fully retired May 3, 2027.")

    uad_sub1, uad_sub2, uad_sub3, uad_sub4 = st.tabs([
        "📊 What Changed vs 2.6",
        "🔍 New Inspection Data",
        "🏠 C & Q Ratings",
        "💻 Report Writing Tools"
    ])

    # ── WHAT CHANGED ─────────────────────────────────────────────────────────
    with uad_sub1:
        st.markdown("### Overall vs UAD 2.6 — same, changed, new, or gone")

        col_leg1, col_leg2, col_leg3, col_leg4 = st.columns(4)
        with col_leg1: st.success("🟢 Same")
        with col_leg2: st.warning("🟡 Changed")
        with col_leg3: st.info("🔵 New")
        with col_leg4: st.error("🔴 Gone")

        sections = {
            "Forms & Report Structure": [
                ("🟡", "Form selection", "Single dynamic URAR replaces 1004, 1073, 2055, and all legacy forms. Sections turn on/off based on property/assignment type. No more form numbers."),
                ("🔴", "1004MC Market Conditions form", "Eliminated entirely. Market conditions are now embedded in the URAR Market section as structured fields. Time adjustments still required and must be supported with data — just not the MC grid format."),
                ("🟡", "Scope of work", "Still required. More structured fields, less free-text narrative. The analytical obligation is unchanged."),
            ],
            "Condition & Quality Ratings": [
                ("🟡", "C1–C6 Condition scale", "Now three separate ratings: Exterior Condition + Interior Condition → reconciled to Overall. Previously one rating for the whole property."),
                ("🟡", "Q1–Q6 Quality scale", "Same structure change — Exterior Quality + Interior Quality → Overall. Quality is still absolute, not relative to your market."),
                ("🟢", "C6 rule", "If any component is C6, overall must be C6. Unchanged. Fannie allows C5 as-is in some cases; Freddie requires C4 minimum for delivery."),
                ("🟡", "Defects documentation", "When C5 or C6: now requires itemized structured list — location, description, impact on soundness, recommended action, estimated repair cost. Previously narrative only."),
                ("🔵", "As-Is + Subject-to-Repair ratings", "When repairs required, must report BOTH the As-Is Overall Condition AND the Condition Subject to Repair as separate explicit ratings."),
            ],
            "Kitchen & Bathroom Reporting": [
                ("🔴", "'Not updated / Updated / Remodeled' checkbox", "Retired entirely. Replaced by structured Kitchen and Bathroom Details sections."),
                ("🟡", "Kitchen reporting", "Per-kitchen structured section: update status + approximate year of update + condition rating (C1–C6) + brief description. Every kitchen reported individually."),
                ("🟡", "Bathroom reporting", "Per-bathroom structured section: same as kitchen. Every bathroom including half baths reported individually."),
            ],
            "Site & Location": [
                ("🟡", "View / location influence", "Replaced by Site Influence section. Now captures: onsite / bordering / distant AND positive / neutral / negative. A pond on the lot vs a lake view from a distance are now distinct reportable data points."),
                ("🟡", "Zoning, utilities, site features", "Significantly expanded structured fields. The Site section is 30 pages in the URAR Reference Guide — second largest chapter after the Sales Comparison Approach."),
            ],
            "Sales Comparison Approach": [
                ("🟢", "Comparable selection and analysis", "Same process, same professional judgment required. More structured fields, less free-text narrative."),
                ("🟡", "Time adjustments", "1004MC is gone. Time adjustments still required when market warrants. Must be supported with market data. The decision to NOT adjust requires the same level of support as the decision to adjust."),
                ("🟢", "Actual age in comp grid", "Only actual age in the grid. Effective age discussion moves to narrative commentary."),
                ("🟡", "GLA measurement", "ANSI Z765-2021 formalized. Above-grade finished area must be broken out by floor. UCDP compliance rules will enforce ANSI logic on submission."),
            ],
            "Special Features": [
                ("🔵", "ADU section", "New dedicated section. Effective Mar 21, 2026: expanded ADU eligibility ONLY available with UAD 3.6 submissions. ADU rental income can count toward qualifying income under certain conditions."),
                ("🟡", "Manufactured housing terminology", "Effective Mar 31, 2026: 'single-width' and 'multi-width' replace 'single-section' and 'multi-section' in all UAD 3.6 reports."),
            ],
            "Core Appraisal Practice": [
                ("🟢", "How value is estimated", "Exactly the same. UAD 3.6 changes how work is reported, not how value is estimated."),
                ("🟢", "USPAP compliance", "Required and unchanged. UAD 3.6 is a reporting format change, not a USPAP change."),
                ("🟢", "Physical inspection process", "The inspection itself does not change. What changes is the structured way you document and report what you observed."),
                ("🟢", "Highest and best use analysis", "Same requirement, same analysis. Reporting format more structured."),
                ("🟢", "Cost and income approaches", "Same analytical requirements. More structured data fields for reporting conclusions."),
            ],
        }

        for section, items in sections.items():
            st.markdown(f"**{section}**")
            for status, title, detail in items:
                with st.expander(f"{status} {title}"):
                    st.write(detail)
            st.write("")

        st.caption("Source: Fannie Mae & Freddie Mac UAD Inspection and Reporting Tips (Oct 2025), UAD 3.6 FAQ, McKissock Learning, Working RE, Appraiser eLearning.")

    # ── NEW INSPECTION DATA ───────────────────────────────────────────────────
    with uad_sub2:
        st.markdown("### New data you must collect at the inspection")
        st.warning("UAD 3.6 requires significantly more structured data collected in the field. Plan your inspections accordingly — some of this requires new tools or conversations with the owner/agent that weren't necessary before.")

        st.markdown("#### 🔧 Bring to every inspection")
        tool_items = [
            ("Laser distance measurer", "Required for ceiling height measurement — a tape measure and ladder is not practical or safe. Ceiling height is a required field every time (Report Field ID: 10.045)."),
            ("Mobile device with UAD 3.6 software", "The volume of new structured data fields makes mobile data entry at the inspection far more efficient than clipboard + office entry. This is the workflow UAD 3.6 is built around."),
        ]
        for tool, note in tool_items:
            with st.expander(f"🔧 {tool}"):
                st.write(note)

        st.markdown("#### 🔵 New — must now measure or collect")
        new_items = [
            ("Ceiling height (required every inspection)", "Required field — always. Tied to ANSI 7-foot rule: if more than half a room's area is under 7 ft, that area cannot count as finished GLA. Measure with a laser."),
            ("Walls and ceiling materials/type", "Required structured field in Interior Features table — select from defined enumerations. Always displays, always required."),
            ("Nonstandard Finished Area (NSFA)", "Finished space that doesn't meet ANSI must be measured and reported separately from GLA. Must explain why (e.g. 'sloping ceiling under 7 ft'). Common in finished attics, bonus rooms with knee walls."),
            ("Roof replacement estimate", "New structured field — when was the roof last replaced? Ask the owner or agent at inspection. Can also pull from permit records."),
            ("Outbuilding utilities", "If outbuildings present: which utilities have been extended to each (electric, water, HVAC, etc.)."),
            ("Broadband internet availability", "Surprising new requirement. Verify via FCC broadband map or ask the owner. The GSE definition of 'broadband' is specific — check Appendix F-1 for the enumeration."),
            ("Access road type", "New structured field — type of road providing access (public paved, private paved, gravel, dirt, etc.)."),
            ("ADU detail (if present)", "New dedicated section — unit type, GLA, bed/bath count, kitchen presence, separate entrance, condition, and whether legally permitted. Collect all at inspection."),
            ("Disaster mitigation features", "If present: storm shutters, hurricane straps, flood vents, seismic retrofitting. If this section is included, the commentary field is required."),
        ]
        for title, detail in new_items:
            with st.expander(f"🔵 {title}"):
                st.write(detail)

        st.markdown("#### 🟡 Changed — process same, now structured")
        changed_items = [
            ("Above-grade finished area — per floor breakdown", "Previously reported as one total GLA number. Now must be broken out by floor — first floor, second floor, etc. UCDP will validate that floors sum to total."),
            ("Kitchen update status — per kitchen", "Previously one checkbox. Now per-kitchen: update status + approximate year + condition rating + brief description."),
            ("Bathroom update status — per bathroom", "Previously one checkbox. Now per-bathroom: same structured fields. Every bathroom including half baths."),
            ("Exterior quality — separate from interior", "Assess separately: siding, roof, foundation, windows, trim, architectural detail. Record as its own rating."),
            ("Exterior condition — separate from interior", "Assess separately: same components. Must reconcile with interior condition to reach overall rating."),
            ("Interior quality — separate from exterior", "Assess separately: flooring, trim, cabinetry, fixtures, countertops, built-ins."),
            ("Interior condition — separate from exterior", "Assess separately. If C5/C6: itemized defect list required."),
            ("Site influence (view/location)", "Now captures: onsite / bordering / distant AND positive / neutral / negative. More granular than the old View field."),
        ]
        for title, detail in changed_items:
            with st.expander(f"🟡 {title}"):
                st.write(detail)

        st.markdown("#### 🔴 Gone — no longer required")
        gone_items = [
            ("Street inspection of comparable sales", "No longer required. Front photo of comp still required but the physical drive-by has been retired. Photo can be sourced from MLS or other reliable source."),
        ]
        for title, detail in gone_items:
            with st.expander(f"🔴 {title}"):
                st.write(detail)

        st.caption("Source: GSE Inspection and Reporting Tips (Oct 2025), Appendix F-1 URAR Reference Guide, ANSI Z765-2021.")

    # ── C & Q RATINGS ────────────────────────────────────────────────────────
    with uad_sub3:
        st.markdown("### Condition Ratings (C1–C6)")
        st.info("Key change: Condition is now reported separately for Exterior and Interior, then reconciled to an Overall rating. If ANY component is C6, the overall must be C6. Fannie allows C5 as-is in some cases; Freddie requires C4 minimum for loan delivery.")

        conditions = [
            ("C1", "New / Like New", "New or nearly new. No physical wear on any component. All major and minor elements are in like-new condition. Rebuilt homes may qualify if on a completely new foundation with fully remanufactured materials.", "Use for new construction and very recent gut rehabs to the studs. Rarely seen on resale."),
            ("C2", "Extensive Renovation", "Extensively renovated to resemble new construction. Most components recently replaced or refinished. Minimal physical depreciation, no deferred maintenance, nothing requires repair.", "Component-level detail in 3.6 makes this harder to assign loosely. Every major system should be new or like-new. Kitchen and bathroom details must support it."),
            ("C3", "Well Maintained / Updated", "Well maintained with limited physical depreciation. Some components may show minor wear but all functional systems are working properly. Some updating may be present.", "Most move-in ready properties with recent updates but not full renovation. Very common in well-maintained New England stock."),
            ("C4", "Average / Adequate", "Adequately maintained with some physical depreciation. Normal wear and tear. All functional systems working. No immediate repairs required but may have deferred maintenance items.", "The baseline for typical resale. Dated but functional kitchens/baths, normal aging. Very common in pre-1970 RI/MA stock."),
            ("C5", "Fair / Deferred Maintenance", "Obvious deferred maintenance and/or physical deterioration. Some components need repair or replacement. Major systems may be functional but near end of useful life.", "Freddie Mac: C5 is NOT eligible for delivery — must be repaired to C4. Fannie allows C5 as-is in some cases. Always check lender overlays. Requires itemized defect list in 3.6."),
            ("C6", "Significant Damage / Safety Concern", "Significant damage, serious deferred maintenance, or conditions affecting safety, soundness, or structural integrity. Property may be uninhabitable or pose health/safety risks.", "If any single component is C6, the overall must be C6. Requires full itemized defect list with location, description, impact, recommended action, and estimated repair cost."),
        ]

        for code, label, definition, notes in conditions:
            with st.expander(f"**{code} — {label}**"):
                st.write(definition)
                st.caption(f"📝 Field notes: {notes}")

        st.divider()
        st.markdown("### Quality Ratings (Q1–Q6)")
        st.info("Key change: Quality is now reported separately for Exterior and Interior, then reconciled to an Overall rating. Quality is absolute — a Q3 is a Q3 whether it's in Providence or Newport. Local market norms do not determine quality rating.")

        qualities = [
            ("Q1", "Exceptional / Custom", "Custom architecture, outstanding workmanship, and premium materials throughout — often imported or specialty items. Every component shows exceptional detail and design.", "Very rare. Most markets have no Q1 properties. If you're questioning whether it's Q1, it probably isn't."),
            ("Q2", "High Quality / Custom", "Still custom but not at the absolute top tier. High-quality materials and consistently strong workmanship. May be custom-built or part of a high-quality development.", "May be the highest rating seen in many markets. Common in higher-end coastal RI and South Shore MA."),
            ("Q3", "Good Quality / Above Average", "Solidly constructed with good materials, though not custom throughout. Often includes upgraded finishes mixed with some standard components.", "The most common rating in the upper-middle price range. Upgraded kitchen and baths with standard framing and exterior."),
            ("Q4", "Average / Standard", "Standard or builder-grade materials and construction. Meets code requirements. No significant upgrades. Represents the majority of production housing.", "The baseline for most residential construction. Colonial-era New England stock typically falls here despite age — quality is about construction, not condition."),
            ("Q5", "Fair / Below Average", "Below-standard materials or workmanship. May show significant deficiencies in design, construction, or finish. Functional but lacks quality.", "Rare in typical residential lending. More common in older worker housing, self-built structures, or properties with significant deferred improvements."),
            ("Q6", "Poor / Substandard", "Construction that may not meet basic building standards. Often built without professional oversight or adherence to modern codes. May be unsuitable for year-round habitation.", "Very rarely assigned. Flag immediately — lender eligibility issues are likely."),
        ]

        for code, label, definition, notes in qualities:
            with st.expander(f"**{code} — {label}**"):
                st.write(definition)
                st.caption(f"📝 Field notes: {notes}")

        st.caption("Source: McKissock Learning, Appendix F-1 URAR Reference Guide, Working RE — UAD Quality Equation (Aug 2025).")

    # ── REPORT WRITING TOOLS ─────────────────────────────────────────────────
    with uad_sub4:
        st.markdown("### Report Writing Tools — A Guide for Newer Appraisers")

        st.markdown("""
The appraisal profession is going through its biggest technology shift in decades. UAD 3.6 changes not just what you report but how you collect data in the field — and a new generation of software tools has been built specifically around this new workflow. If you're newer to the profession, you have an advantage: you don't have 15 years of muscle memory to undo.
        """)

        st.divider()
        st.markdown("#### The two categories of report-writing software")

        col_trad, col_ai = st.columns(2)
        with col_trad:
            st.markdown("**Traditional platforms**")
            st.caption("e.g. TOTAL by a la mode, ClickForms, ACI")
            st.write("These have been the industry standard for decades. You enter data manually, build your report field by field, and write narrative addenda. They are being updated for UAD 3.6 but the core workflow — appraiser drives everything — stays the same.")
            st.markdown("✅ Full control over every field  \n✅ Deep MLS and data integration  \n✅ Established, trusted by AMCs  \n✅ Large training community  \n❌ UAD 3.6 transition still in progress  \n❌ Monthly subscription cost")

        with col_ai:
            st.markdown("**AI-assisted platforms**")
            st.caption("e.g. Automax, Aivre, ApprAIz")
            st.write("A new wave of tools built from the ground up for UAD 3.6. These use AI and structured data to auto-populate fields, generate sketches, suggest comps, and flag compliance issues in real time. Both Automax and Aivre were featured at the 2026 UAD 3.6 Bootcamp alongside Fannie Mae and Freddie Mac.")
            st.markdown("✅ Built for UAD 3.6 from day one  \n✅ Faster data entry in the field  \n✅ Real-time compliance checking  \n✅ Auto-populates structured fields  \n❌ Newer — less track record  \n❌ AMC acceptance varies by lender")

        st.divider()
        st.markdown("#### What AI actually does in appraisal software")

        ai_items = [
            ("Computer vision / scanning", "You walk through a property with your phone and the app uses the camera to measure rooms, generate a sketch, and identify features like flooring type, ceiling height, and condition. Some tools can do this in real time during the inspection walkthrough."),
            ("Auto-population", "The software pulls property data from public records, MLS, and other sources and pre-fills report fields — address, lot size, year built, zoning, etc. — so it's already there when you open the assignment."),
            ("Comp suggestion", "Algorithms scan MLS and public record data and suggest comparable sales based on proximity, size, age, condition, and other factors. You still select and verify each comp — the AI narrows the search, you make the call."),
            ("Compliance checking", "The software flags UAD 3.6 rule violations before you submit — missing required fields, inconsistent C/Q ratings, data that doesn't pass UCDP logic checks. Catches errors before the reviewer does."),
            ("What AI does NOT do", "AI does not form the opinion of value. The analysis, judgment, and professional conclusions are entirely yours. USPAP places that responsibility on the appraiser and no software changes that."),
        ]

        for title, detail in ai_items:
            with st.expander(f"{'⚠️' if 'NOT' in title else '🤖'} {title}"):
                st.write(detail)

        st.divider()
        st.markdown("#### Automax vs Aivre — balanced overview")
        st.caption("Both were UAD 3.6 software demo participants at the 2026 Appraiser eLearning Bootcamp alongside Fannie Mae and Freddie Mac.")

        col_am, col_av = st.columns(2)
        with col_am:
            st.markdown("**Automax**")
            st.caption("Free platform — hybrid order network model")
            st.write("Offers the platform at no cost in exchange for participation in their hybrid appraisal order network. Hybrid orders typically involve a reduced-scope inspection with the appraiser completing the valuation. Order acceptance is generally flexible.")
            st.markdown("""
**Features:**
- Instant sketch generation
- TOTAL data integration
- MLS + public records + Zillow comp data
- Cloud-stored USPAP-compliant workfile
- UAD 3.6 on active roadmap

**Consider if:** You want to reduce your software overhead and are open to hybrid assignments as part of your workflow.

**Watch for:** UAD 3.6 deployment timeline — confirm current status with Automax directly before committing.
            """)

        with col_av:
            st.markdown("**Aivre**")
            st.caption("~$2,500/year — standalone subscription")
            st.write("A standalone AI-assisted platform with a subscription model. Was an early mover on UAD 3.6 compliance. As of early 2026 did not include a sketch component — verify current feature set before evaluating as this space moves quickly.")
            st.markdown("""
**Features:**
- UAD 3.6 compliant early
- Purpose-built for new URAR
- No order network obligations
- Full control — standalone tool

**Consider if:** You want a UAD 3.6-native platform with no strings attached and are willing to pay the subscription.

**Watch for:** Sketch capability — this is a significant gap for UAD 3.6 field data collection. Confirm current status.
            """)

        st.divider()
        st.info("**A note for newer appraisers:** Neither tool eliminates the need to understand the appraisal process. AI-assisted platforms speed up data collection and flag compliance issues, but they work best in the hands of someone who already understands what the fields mean, why certain adjustments are made, and what USPAP requires. The foundation comes first — the technology amplifies it. Start your UAD 3.6 education with Fannie Mae's free resources at **fanniemae.com/UAD** — specifically Appendix F-1 (375 pages, worth having as a searchable PDF).")

        st.caption("Source: Appraiser eLearning 2026 UAD 3.6 Bootcamp, Working RE, McKissock Learning, Fannie Mae Appraiser Update (Jan 2026).")



# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — REPORT BUILDER (GP RESIDENTIAL)
# ══════════════════════════════════════════════════════════════════════════════



# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — QC CHECKER
# ══════════════════════════════════════════════════════════════════════════════
elif selection == "✅ QC Checker":
    st.markdown("## QC Checker")
    st.caption(
        "Upload a TOTAL XML export and optionally the PDF. "
        "The checker reads all structured data directly from XML and flags internal inconsistencies."
    )
    st.divider()

    import re
    import xml.etree.ElementTree as ET
    from datetime import datetime, date as dt_date

    try:
        import fitz
        FITZ_AVAILABLE = True
    except ImportError:
        FITZ_AVAILABLE = False

    u1, u2 = st.columns(2)
    with u1:
        qc_xml = st.file_uploader(
            "Upload TOTAL XML Export (required)",
            type=["xml"],
            key="qc_xml_upload",
            help="File > Export > XML from TOTAL. Contains all structured report data."
        )
    with u2:
        qc_pdf = st.file_uploader(
            "Upload TOTAL PDF (optional)",
            type=["pdf"],
            key="qc_pdf_upload",
            help="Adds addendum narrative text checks — adjustment support language, prior sale commentary."
        )

    if not qc_xml:
        st.info("Upload a TOTAL XML export to run QC checks.")
        st.stop()

    # ── Parse XML ─────────────────────────────────────────────────────────
    @st.cache_data(show_spinner="Parsing XML...")
    def parse_xml(xml_bytes):
        root = ET.fromstring(xml_bytes.decode("utf-8", errors="ignore"))
        return root

    @st.cache_data(show_spinner="Reading PDF...")
    def parse_pdf(pdf_bytes):
        if not FITZ_AVAILABLE:
            return ""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        return "\n".join(p.get_text() for p in doc)

    xml_root = parse_xml(qc_xml.read())
    pdf_text = ""
    if qc_pdf:
        pdf_text = parse_pdf(qc_pdf.read())
        st.success("XML + PDF loaded.")
    else:
        st.success("XML loaded.")

    # ── XML helpers ───────────────────────────────────────────────────────
    def find_elem(root, tag):
        for e in root.iter():
            t = e.tag.split('}')[-1] if '}' in e.tag else e.tag
            if t == tag:
                return e
        return None

    def find_all_elems(root, tag):
        results = []
        for e in root.iter():
            t = e.tag.split('}')[-1] if '}' in e.tag else e.tag
            if t == tag:
                results.append(e)
        return results

    def attr(elem, key, default=""):
        if elem is None:
            return default
        return elem.get(key, default).strip()

    def to_int(val):
        if not val:
            return None
        try:
            return int(float(str(val).replace("$","").replace(",","").replace("+","").strip()))
        except Exception:
            return None

    def to_float(val):
        if not val:
            return None
        try:
            return float(str(val).replace("%","").replace("$","").replace(",","").strip())
        except Exception:
            return None

    def parse_date(val):
        if not val:
            return None
        for fmt in ["%Y-%m-%d","%m/%d/%Y","%Y/%m/%d"]:
            try:
                return datetime.strptime(val.strip(), fmt).date()
            except Exception:
                pass
        return None

    # ── Extract subject data ──────────────────────────────────────────────
    prop    = find_elem(xml_root, "PROPERTY")
    struct  = find_elem(xml_root, "STRUCTURE")
    site    = find_elem(xml_root, "SITE")
    nbhd    = find_elem(xml_root, "NEIGHBORHOOD")
    val_elem= find_elem(xml_root, "VALUATION")
    recon   = find_elem(xml_root, "_RECONCILIATION")
    report  = find_elem(xml_root, "REPORT")

    subj_addr    = attr(prop, "_StreetAddress")
    subj_city    = attr(prop, "_City")
    subj_state   = attr(prop, "_State")
    subj_rights  = attr(prop, "_RightsType")

    subj_gla     = to_int(attr(struct, "GrossLivingAreaSquareFeetCount"))
    subj_rooms   = to_int(attr(struct, "TotalRoomCount"))
    subj_beds    = to_int(attr(struct, "TotalBedroomCount"))
    subj_baths   = to_float(attr(struct, "TotalBathroomCount"))
    subj_yr      = to_int(attr(struct, "PropertyStructureBuiltYear"))
    subj_stories = to_float(attr(struct, "StoriesCount"))
    subj_style   = attr(struct, "_DesignDescription")

    subj_site    = attr(site, "_AreaDescription")
    subj_zone    = attr(site, "_ZoningClassificationIdentifier")
    subj_zcomp   = attr(site, "_ZoningComplianceType")

    nbhd_value_trend = attr(nbhd, "_PropertyValueTrendType")
    nbhd_supply      = attr(nbhd, "_DemandSupplyType")
    nbhd_mkt_time    = attr(nbhd, "_TypicalMarketingTimeDurationType")
    nbhd_growth      = attr(nbhd, "_GrowthPaceType")
    nbhd_builtup     = attr(nbhd, "_BuiltupRangeType")
    nbhd_desc        = attr(nbhd, "_Description")

    appraised_value  = to_int(attr(val_elem, "PropertyAppraisedValueAmount"))
    eff_date         = parse_date(attr(val_elem, "AppraisalEffectiveDate"))
    recon_comment    = attr(recon, "_SummaryComment")

    report_signed    = parse_date(attr(report, "AppraiserReportSignedDate"))
    file_num         = attr(report, "AppraiserFileIdentifier")
    purpose          = attr(report, "AppraisalPurposeType")

    # Appraiser license
    lic_elem  = find_elem(xml_root, "APPRAISER_LICENSE")
    lic_num   = attr(lic_elem, "_Identifier")
    lic_exp   = parse_date(attr(lic_elem, "_ExpirationDate"))
    lic_state = attr(lic_elem, "_State")

    appraiser_elem = find_elem(xml_root, "APPRAISER")
    appraiser_name = attr(appraiser_elem, "_Name")

    insp_elem = find_elem(xml_root, "INSPECTION")
    insp_date = parse_date(attr(insp_elem, "InspectionDate"))

    supervisor_elem = find_elem(xml_root, "SUPERVISOR")
    supervisor_name = attr(supervisor_elem, "_Name")

    # Borrower / intended user
    borrower_elem = find_elem(xml_root, "BORROWER")
    borrower_name = attr(borrower_elem, "_UnparsedName")

    lender_elem = find_elem(xml_root, "LENDER")
    lender_name = attr(lender_elem, "_UnparsedName")

    # ── Extract comparable sales ──────────────────────────────────────────
    comp_elems = find_all_elems(xml_root, "COMPARABLE_SALE")
    # First comp (seq 0) is the subject — skip it
    actual_comps = [c for c in comp_elems
                    if attr(c,"PropertySequenceIdentifier") != "0"]

    comps = []
    for c in actual_comps:
        seq      = to_int(attr(c, "PropertySequenceIdentifier"))
        price    = to_int(attr(c, "PropertySalesAmount"))
        net_pct  = to_float(attr(c, "SalePriceTotalAdjustmentNetPercent"))
        gross_pct= to_float(attr(c, "SalesPriceTotalAdjustmentGrossPercent"))
        net_amt  = to_int(attr(c, "SalePriceTotalAdjustmentAmount"))
        adj_val  = to_int(attr(c, "AdjustedSalesPriceAmount"))
        net_pos  = attr(c, "SalesPriceTotalAdjustmentPositiveIndicator")  # Y/N

        # Location
        loc = find_elem(c, "LOCATION")
        comp_addr   = attr(loc, "PropertyStreetAddress")
        comp_city   = attr(loc, "PropertyCity")
        proximity   = attr(loc, "ProximityToSubjectDescription")

        # Extract miles from proximity
        prox_miles  = None
        pm = re.search(r'([\d.]+)\s*miles?', proximity or "", re.IGNORECASE)
        if pm:
            prox_miles = float(pm.group(1))

        # Room data
        room_adj = find_elem(c, "ROOM_ADJUSTMENT")
        comp_rooms= to_int(attr(room_adj, "TotalRoomCount"))
        comp_beds = to_int(attr(room_adj, "TotalBedroomCount"))
        comp_baths= to_float(attr(room_adj, "TotalBathroomCount"))

        # Sale price adjustments — build dict by type
        adj_map = {}
        for spa in find_all_elems(c, "SALE_PRICE_ADJUSTMENT"):
            atype = attr(spa, "_Type")
            adesc = attr(spa, "_Description")
            aamt  = attr(spa, "_Amount")
            adj_map[atype] = {"desc": adesc, "amount": to_int(aamt) if aamt else None}

        # Other feature adjustments
        other_adjs = []
        for ofa in find_all_elems(c, "OTHER_FEATURE_ADJUSTMENT"):
            desc = attr(ofa, "PropertyFeatureDescription")
            amt  = to_int(attr(ofa, "PropertyFeatureAdjustmentAmount"))
            if desc or amt:
                other_adjs.append({"desc": desc, "amount": amt})

        # Prior sale
        prior = find_elem(c, "PRIOR_SALES")
        prior_date = attr(prior, "PropertySalesDate")
        prior_amt  = to_int(attr(prior, "PropertySalesAmount"))

        # Parse comp GLA from GrossLivingArea adjustment description
        comp_gla = None
        if "GrossLivingArea" in adj_map:
            gla_desc = adj_map["GrossLivingArea"]["desc"]
            gm = re.match(r'(\d+)', gla_desc or "")
            if gm:
                comp_gla = to_int(gm.group(1))

        # Parse date of sale
        sale_date_str = adj_map.get("DateOfSale",{}).get("desc","")
        # Format: s08/25;c06/25 — settled date first
        sale_date = None
        sdm = re.search(r's(\d{2}/\d{2})', sale_date_str or "")
        if sdm:
            # Convert MM/YY to approximate date
            parts = sdm.group(1).split("/")
            try:
                sale_date = dt_date(2000 + int(parts[1]), int(parts[0]), 1)
            except Exception:
                pass

        # Parse financing concessions amount
        fin_desc = adj_map.get("FinancingConcessions",{}).get("desc","")
        fin_amt = None
        fm = re.search(r';(\d+)', fin_desc or "")
        if fm:
            fin_amt = to_int(fm.group(1))

        comps.append({
            "num": seq, "address": comp_addr, "city": comp_city,
            "proximity": proximity, "prox_miles": prox_miles,
            "price": price, "net_pct": net_pct, "gross_pct": gross_pct,
            "net_amt": net_amt, "net_pos": net_pos, "adj_value": adj_val,
            "rooms": comp_rooms, "beds": comp_beds, "baths": comp_baths,
            "gla": comp_gla, "adj_map": adj_map, "other_adjs": other_adjs,
            "prior_date": prior_date, "prior_amt": prior_amt,
            "sale_date": sale_date, "fin_amt": fin_amt,
        })

    # ── Display extracted summary ─────────────────────────────────────────
    with st.expander("Extracted Data — expand to review", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Subject**")
            st.write(f"Address: {subj_addr}, {subj_city}, {subj_state}")
            st.write(f"GLA: {subj_gla:,} sf" if subj_gla else "GLA: not found")
            st.write(f"Rooms: {subj_rooms} | Beds: {subj_beds} | Baths: {subj_baths}")
            st.write(f"Year Built: {subj_yr}")
            st.write(f"Style: {subj_style}")
            st.write(f"Property Rights: {subj_rights}")
            st.write(f"Appraised Value: ${appraised_value:,}" if appraised_value else "Value: not found")
            st.write(f"Effective Date: {eff_date}")
        with c2:
            st.markdown("**Appraiser / License**")
            st.write(f"Name: {appraiser_name}")
            st.write(f"License: {lic_num} ({lic_state})")
            st.write(f"License Exp: {lic_exp}")
            st.write(f"Inspection Date: {insp_date}")
            st.write(f"Report Signed: {report_signed or 'not found'}")
            st.write(f"Supervisor: {supervisor_name or '(none)'}")
            st.write(f"File #: {file_num or '(blank)'}")
        with c3:
            st.markdown("**Market / Neighborhood**")
            st.write(f"Value Trend: {nbhd_value_trend}")
            st.write(f"Supply/Demand: {nbhd_supply}")
            st.write(f"Marketing Time: {nbhd_mkt_time}")
            st.write(f"Growth Rate: {nbhd_growth}")
            st.write(f"Built-Up: {nbhd_builtup}")

        if comps:
            st.markdown("**Comparable Sales**")
            for c in comps:
                p   = f"${c['price']:,}" if c['price'] else "—"
                av  = f"${c['adj_value']:,}" if c['adj_value'] else "—"
                np  = f"{c['net_pct']}%" if c['net_pct'] is not None else "—"
                gp  = f"{c['gross_pct']}%" if c['gross_pct'] is not None else "—"
                gla = f"{c['gla']:,} sf" if c['gla'] else "—"
                st.write(f"Comp #{c['num']}: {c['address']} | {p} → {av} "
                          f"| Net {np} | Gross {gp} | GLA {gla} | {c['proximity']}")

    # ── Sketch input (still manual — images not parseable) ────────────────
    st.divider()
    st.markdown("### Sketch Input")
    st.caption("Sketch room count and GLA can't be extracted from image-based sketch pages.")
    sk1, sk2 = st.columns(2)
    with sk1:
        sketch_rooms = st.number_input("Sketch room count (above grade)",
                                        min_value=0, max_value=20,
                                        value=subj_rooms or 0, key="qc_sketch_rooms")
    with sk2:
        sketch_gla   = st.number_input("Sketch GLA (sq ft)",
                                        min_value=0, max_value=10000,
                                        value=subj_gla or 0, key="qc_sketch_gla")

    # ── Run QC ────────────────────────────────────────────────────────────
    st.divider()
    if st.button("Run QC Checks", type="primary", use_container_width=True, key="qc_run"):

        flags  = []
        passes = []

        def flag(cat, msg, sev="warning"):
            flags.append({"cat": cat, "msg": msg, "sev": sev})
        def ok(cat, msg):
            passes.append({"cat": cat, "msg": msg})

        # ── 1. License expiration vs effective date ───────────────────────
        if lic_exp and eff_date:
            if lic_exp < eff_date:
                flag("License Expired",
                     f"License expired {lic_exp} but effective date is {eff_date}.",
                     "critical")
            else:
                ok("License",
                   f"License {lic_num} valid through {lic_exp} — effective date {eff_date}.")
        elif not lic_exp:
            flag("License", "License expiration date not found in XML.", "critical")

        # ── 2. License state matches property state ───────────────────────
        if lic_state and subj_state:
            if lic_state.upper() != subj_state.upper():
                flag("License State",
                     f"License is for {lic_state} but property is in {subj_state}.",
                     "critical")
            else:
                ok("License State",
                   f"License state ({lic_state}) matches property state ({subj_state}).")

        # ── 3. Inspection date not after effective date ───────────────────
        if insp_date and eff_date:
            if insp_date > eff_date:
                flag("Inspection Date",
                     f"Inspection date {insp_date} is after effective date {eff_date}.",
                     "critical")
            else:
                ok("Inspection Date",
                   f"Inspection date {insp_date} is on or before effective date {eff_date}.")

        # ── 4. File number blank ──────────────────────────────────────────
        if not file_num:
            flag("File Number", "File number is blank.", "warning")
        else:
            ok("File Number", f"File number present: {file_num}")

        # ── 5. Room count — form vs sketch ────────────────────────────────
        if subj_rooms and sketch_rooms > 0:
            if subj_rooms != sketch_rooms:
                flag("Room Count",
                     f"Form states {subj_rooms} rooms but sketch shows {sketch_rooms}.",
                     "critical")
            else:
                ok("Room Count", f"Form and sketch agree: {subj_rooms} rooms.")

        # ── 6. GLA — form vs sketch ───────────────────────────────────────
        if subj_gla and sketch_gla > 0:
            diff = abs(subj_gla - sketch_gla)
            pct  = diff / subj_gla * 100
            if diff > 20:
                flag("GLA Discrepancy",
                     f"Form GLA {subj_gla:,} sf vs sketch GLA {sketch_gla:,} sf "
                     f"— difference of {diff} sf ({pct:.1f}%).",
                     "critical" if pct > 5 else "warning")
            else:
                ok("GLA", f"Form and sketch GLA agree within 20 sf ({subj_gla:,} sf).")

        # ── 7. Net adjustment per comp > 15% ─────────────────────────────
        net_issues = []
        for c in comps:
            if c["net_pct"] is not None and abs(c["net_pct"]) > 15:
                net_issues.append(
                    f"Comp #{c['num']} ({c['address'][:25]}): "
                    f"net adj {c['net_pct']:+.1f}% exceeds 15% guideline")
        if net_issues:
            for iss in net_issues:
                flag("Net Adjustment >15%", iss)
        else:
            ok("Net Adjustments", "All comp net adjustments within 15% guideline.")

        # ── 8. Gross adjustment per comp > 25% ───────────────────────────
        gross_issues = []
        for c in comps:
            if c["gross_pct"] is not None and c["gross_pct"] > 25:
                gross_issues.append(
                    f"Comp #{c['num']} ({c['address'][:25]}): "
                    f"gross adj {c['gross_pct']:.1f}% exceeds 25% guideline")
        if gross_issues:
            for iss in gross_issues:
                flag("Gross Adjustment >25%", iss)
        else:
            ok("Gross Adjustments", "All comp gross adjustments within 25% guideline.")

        # ── 9. All comps adjusted same direction ─────────────────────────
        net_directions = [c["net_pos"] for c in comps
                          if c["net_pos"] and c["net_pct"] and abs(c["net_pct"]) > 0.5]
        if len(net_directions) >= 3:
            if all(d == "Y" for d in net_directions):
                flag("Adjustment Direction",
                     "All comps have net positive adjustments — subject may be "
                     "priced below comparable sales without adequate explanation.")
            elif all(d == "N" for d in net_directions):
                flag("Adjustment Direction",
                     "All comps have net negative adjustments — subject may be "
                     "priced above comparable sales without adequate explanation.")
            else:
                ok("Adjustment Direction",
                   "Comps have mixed net adjustment directions — no bracketing concern.")

        # ── 10. Subject value vs adjusted comp range ──────────────────────
        adj_values = [c["adj_value"] for c in comps if c["adj_value"]]
        if adj_values and appraised_value:
            low_adj  = min(adj_values)
            high_adj = max(adj_values)
            if appraised_value < low_adj:
                flag("Value Outside Comp Range",
                     f"Appraised value ${appraised_value:,} is below lowest adjusted "
                     f"comp value ${low_adj:,}.")
            elif appraised_value > high_adj:
                flag("Value Outside Comp Range",
                     f"Appraised value ${appraised_value:,} is above highest adjusted "
                     f"comp value ${high_adj:,}.")
            else:
                ok("Value Within Range",
                   f"Appraised value ${appraised_value:,} is within adjusted "
                   f"comp range ${low_adj:,}–${high_adj:,}.")

        # ── 11. GLA bracketing ────────────────────────────────────────────
        comp_glas = [c["gla"] for c in comps if c["gla"]]
        if comp_glas and subj_gla:
            low_gla  = min(comp_glas)
            high_gla = max(comp_glas)
            if subj_gla < low_gla:
                flag("GLA Bracketing",
                     f"Subject GLA {subj_gla:,} sf is below all comp GLAs "
                     f"(range: {low_gla:,}–{high_gla:,} sf). Consider adding a smaller comp.")
            elif subj_gla > high_gla:
                flag("GLA Bracketing",
                     f"Subject GLA {subj_gla:,} sf is above all comp GLAs "
                     f"(range: {low_gla:,}–{high_gla:,} sf). Consider adding a larger comp.")
            else:
                ok("GLA Bracketing",
                   f"Subject GLA {subj_gla:,} sf is bracketed by comps "
                   f"({low_gla:,}–{high_gla:,} sf).")

        # ── 12. GLA adjustment rate consistency ───────────────────────────
        if subj_gla and comps:
            implied_rates = []
            for c in comps:
                if c["gla"] and c["adj_map"].get("GrossLivingArea",{}).get("amount") is not None:
                    diff = subj_gla - c["gla"]
                    adj  = c["adj_map"]["GrossLivingArea"]["amount"]
                    if adj and diff and abs(diff) > 30:
                        rate = round(abs(adj / diff))
                        implied_rates.append((c["num"], c["address"][:25], diff, adj, rate))

            if len(implied_rates) >= 2:
                rates = [r[4] for r in implied_rates]
                rate_range = max(rates) - min(rates)
                if rate_range > 5:
                    detail = ", ".join([f"Comp #{n}: ${r}/sf" for n,_,_,_,r in implied_rates])
                    flag("GLA Adj Rate Inconsistency",
                         f"Implied GLA adjustment rates vary: {detail}. "
                         f"Verify consistent rate is applied.")
                else:
                    ok("GLA Adj Rate",
                       f"GLA adj rate consistent across comps (~${rates[0]}/sf).")

        # ── 13. Condition adjustment consistency ──────────────────────────
        cond_adj_map = {}
        for c in comps:
            cond = c["adj_map"].get("Condition",{}).get("desc","")
            amt  = c["adj_map"].get("Condition",{}).get("amount")
            if cond and amt is not None:
                cond_adj_map.setdefault(cond,[]).append((c["num"], amt))

        cond_issues = []
        for cond, entries in cond_adj_map.items():
            amts = set(e[1] for e in entries)
            if len(amts) > 1:
                detail = ", ".join([f"Comp #{n}: ${a:,}" for n,a in entries])
                cond_issues.append(
                    f"Comps rated '{cond}' have different adjustments: {detail}")
        if cond_issues:
            for iss in cond_issues:
                flag("Condition Adj Consistency", iss)
        elif cond_adj_map:
            ok("Condition Adjustments",
               "Condition adjustments consistent for comps with matching ratings.")

        # ── 14. Comp proximity flags ──────────────────────────────────────
        far_comps = [c for c in comps
                     if c["prox_miles"] and c["prox_miles"] > 1.0]
        if far_comps:
            for c in far_comps:
                flag("Comp Distance",
                     f"Comp #{c['num']} ({c['address'][:25]}) is {c['prox_miles']:.2f} miles "
                     f"from subject. Verify extended search explanation is in addendum.")
        else:
            ok("Comp Distance", "All comps within 1 mile of subject.")

        # ── 15. Comp date — older than 12 months ─────────────────────────
        if eff_date:
            old_comps = []
            for c in comps:
                if c["sale_date"]:
                    months_old = (eff_date.year - c["sale_date"].year)*12 + \
                                  (eff_date.month - c["sale_date"].month)
                    if months_old > 12:
                        old_comps.append((c["num"], c["address"][:25], months_old))
            if old_comps:
                for n, addr, mo in old_comps:
                    flag("Comp Date Range",
                         f"Comp #{n} ({addr}) is approximately {mo} months old. "
                         f"Verify extended search explanation is in addendum.")
            else:
                ok("Comp Dates", "All comps appear within 12 months of effective date.")

        # ── 16. Concessions — disclosed but not adjusted ──────────────────
        concession_issues = []
        for c in comps:
            if c["fin_amt"] and c["fin_amt"] > 0:
                # Check if there's a corresponding adjustment amount for concessions
                sales_con_amt = c["adj_map"].get("SalesConcessions",{}).get("amount")
                fin_con_amt   = c["adj_map"].get("FinancingConcessions",{}).get("amount")
                if sales_con_amt is None and fin_con_amt is None:
                    concession_issues.append(
                        f"Comp #{c['num']} ({c['address'][:25]}) shows concessions "
                        f"of ${c['fin_amt']:,} with no adjustment applied.")
        if concession_issues:
            for iss in concession_issues:
                flag("Concessions", iss)
        else:
            ok("Concessions", "No unadjusted concession issues detected.")

        # ── 17. Prior sale flip check ─────────────────────────────────────
        flip_issues = []
        for c in comps:
            if c["prior_date"] and c["prior_amt"] and c["price"]:
                try:
                    prior_dt = datetime.strptime(c["prior_date"], "%m/%d/%Y").date()
                    if c["sale_date"]:
                        months_between = (c["sale_date"].year - prior_dt.year)*12 + \
                                          (c["sale_date"].month - prior_dt.month)
                        pct_change = (c["price"] - c["prior_amt"]) / c["prior_amt"] * 100
                        if months_between <= 24 and pct_change > 20:
                            flip_issues.append(
                                f"Comp #{c['num']} ({c['address'][:25]}) sold for "
                                f"${c['prior_amt']:,} {months_between} months prior then "
                                f"${c['price']:,} — {pct_change:.0f}% increase. "
                                f"Verify arm's length transaction.")
                except Exception:
                    pass
        if flip_issues:
            for iss in flip_issues:
                flag("Prior Sale Flip", iss)
        elif any(c["prior_date"] for c in comps):
            ok("Prior Sales", "No flip/rapid appreciation issues detected in comp prior sales.")

        # ── 18. Market conditions consistency ────────────────────────────
        if nbhd_supply and nbhd_mkt_time:
            supply_lower = nbhd_supply.lower()
            mkt_lower    = nbhd_mkt_time.lower()
            if "shortage" in supply_lower and "overthree" in mkt_lower.replace(" ",""):
                flag("Market Consistency",
                     f"Supply/Demand is '{nbhd_supply}' but marketing time is "
                     f"'{nbhd_mkt_time}' — these are inconsistent.")
            elif "oversupply" in supply_lower.replace(" ","") and "underthree" in mkt_lower.replace(" ",""):
                flag("Market Consistency",
                     f"Supply/Demand is '{nbhd_supply}' but marketing time is "
                     f"'{nbhd_mkt_time}' — these are inconsistent.")
            else:
                ok("Market Consistency",
                   f"Supply/Demand ({nbhd_supply}) and marketing time ({nbhd_mkt_time}) appear consistent.")

        # ── 19. Supervisor blank when trainee signs ───────────────────────
        if not supervisor_name:
            ok("Supervisor", "No supervisory appraiser — solo assignment.")
        else:
            ok("Supervisor", f"Supervisory appraiser present: {supervisor_name}")

        # ── 20. Addendum checks (PDF only) ────────────────────────────────
        if pdf_text:
            adj_support = any(m in pdf_text for m in
                               ["Adjustments made:", "adj @", "adj@", "per SF GLA"])
            if not adj_support:
                flag("Adjustment Support",
                     "No adjustment rate statement found in addendum. "
                     "Verify adjustment support language is present.")
            else:
                ok("Adjustment Support",
                   "Adjustment rate statement present in addendum.")

            prior_language = any(p in pdf_text for p in
                                  ["No other prior sales", "no prior sales",
                                   "prior sale", "did not reveal"])
            if not prior_language:
                flag("Prior Sale Language",
                     "No prior sale/transfer history language found in addendum.")
            else:
                ok("Prior Sale Language",
                   "Prior sale/transfer history addressed in addendum.")

            if subj_state and lic_state and subj_state.upper() != lic_state.upper():
                pass  # Already flagged above
        else:
            st.caption("Upload PDF to enable addendum text checks.")

        # ── Display results ───────────────────────────────────────────────
        st.markdown("---")
        st.markdown(f"## QC Results — {subj_addr}, {subj_city} {subj_state}")

        critical_flags = [f for f in flags if f["sev"] == "critical"]
        warning_flags  = [f for f in flags if f["sev"] == "warning"]

        r1, r2, r3 = st.columns(3)
        with r1:
            if critical_flags:
                st.error(f"🔴 {len(critical_flags)} Critical Issue(s)")
            else:
                st.success("🔴 No Critical Issues")
        with r2:
            if warning_flags:
                st.warning(f"⚠️ {len(warning_flags)} Warning(s)")
            else:
                st.success("⚠️ No Warnings")
        with r3:
            st.success(f"✅ {len(passes)} Passed")

        st.divider()

        if critical_flags:
            st.markdown("### 🔴 Critical Issues")
            for f in critical_flags:
                st.error(f"**{f['cat']}:** {f['msg']}")

        if warning_flags:
            st.markdown("### ⚠️ Warnings")
            for f in warning_flags:
                st.warning(f"**{f['cat']}:** {f['msg']}")

        if passes:
            st.markdown("### ✅ Passed")
            for p in passes:
                st.success(f"**{p['cat']}:** {p['msg']}")
