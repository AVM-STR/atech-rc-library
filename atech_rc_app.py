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

# ── Storage ───────────────────────────────────────────────────────────────────
def load_data(key, filepath, default):
    try:
        raw = st.session_state.get(key)
        if raw:
            return json.loads(raw)
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
    return load_data("_rc_zoning", "rc_zoning.json", [])

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

# ── Header ────────────────────────────────────────────────────────────────────
if os.path.exists(LOGO_PATH):
    st.image(LOGO_PATH, width=200)
st.title("A-Tech Appraisal Co. — Field Reference")
st.caption("Revision responses, addendum comments, neighborhood descriptions, zoning data, and UAD 3.6 reference.")
st.divider()


tab_rev, tab_com, tab_hood, tab_zone, tab_uad, tab_qc = st.tabs([
    "📋 Revision Responses",
    "📝 Appraisal Comments",
    "🏘️ Neighborhood Descriptions",
    "📐 Zoning Districts",
    "🆕 UAD 3.6 Reference",
    "✅ QC Checker"
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — REVISION RESPONSES
# ══════════════════════════════════════════════════════════════════════════════
with tab_rev:
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
with tab_com:
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
with tab_hood:
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
with tab_zone:
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
                # Display as a clean grid
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric("Min Frontage",      zone.get("frontage","—")   or "—")
                    st.metric("Front Yard",         zone.get("front_yard","—") or "—")
                    st.metric("Max Height",         zone.get("max_height","—") or "—")
                with col_b:
                    st.metric("Min Lot Area",       zone.get("lot_area","—")   or "—")
                    st.metric("Side Yard",          zone.get("side_yard","—")  or "—")
                    st.metric("Max Lot Coverage",   zone.get("max_lot_cov","—")or "—")
                with col_c:
                    st.metric("Min Lot Width",      zone.get("lot_width","—")  or "—")
                    st.metric("Rear Yard",          zone.get("rear_yard","—")  or "—")
                    st.metric("Max Stories",        zone.get("max_floors","—") or "—")

                if zone.get("notes"):
                    st.caption(f"📝 Note: {zone['notes']}")
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
with tab_uad:
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
with tab_qc:
    st.markdown("## QC Checker")
    st.caption(
        "Upload a completed TOTAL PDF. The checker extracts adjustment rates, "
        "comp data, and addendum text then flags internal inconsistencies."
    )
    st.divider()

    import re
    import fitz  # PyMuPDF

    u1, u2 = st.columns(2)
    with u1:
        qc_pdf = st.file_uploader(
            "Upload TOTAL Appraisal PDF",
            type=["pdf"],
            key="qc_pdf_upload",
            help="For addendum text, comp data, and adjustment rates."
        )
    with u2:
        qc_html = st.file_uploader(
            "Upload TOTAL Appraisal XML (optional but recommended)",
            type=["xml"],
            key="qc_html_upload",
            help="Export from TOTAL as XML (MISMO format). Provides cleaner structured data extraction."
        )

    if not qc_pdf:
        st.info("Upload a TOTAL appraisal PDF to run QC checks. Adding the HTML export improves accuracy.")
        st.stop()

    @st.cache_data(show_spinner="Reading PDF...")
    def read_pdf(pdf_bytes):
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        return "\n".join(pages), pages

    def read_html(xml_bytes):
        """Extract plain text from TOTAL XML (MISMO) export."""
        try:
            import xml.etree.ElementTree as ET
            raw = xml_bytes.decode("utf-8", errors="ignore")
            # Strip XML tags to get plain text with values
            import re as _re
            # Keep tag names adjacent to values for label matching
            # Convert <TagName>Value</TagName> to "TagName Value\n"
            raw = _re.sub(r'<([A-Za-z][A-Za-z0-9_]+)[^>]*>([^<]{1,200})</\1>',
                          lambda m: f"{m.group(1)} {m.group(2).strip()}\n", raw)
            raw = _re.sub(r'<[^>]+>', ' ', raw)
            raw = _re.sub(r'[ \t]+', ' ', raw)
            raw = _re.sub(r'\n{3,}', '\n\n', raw)
            return raw.strip()
        except Exception:
            return ""

    pdf_bytes = qc_pdf.read()
    full_text, pages = read_pdf(pdf_bytes)

    # HTML text supplements PDF — use it where available for cleaner extraction
    html_text = ""
    if qc_html:
        html_text = read_html(qc_html.read())
        st.success("PDF + XML loaded — combined extraction active.")
    else:
        st.success("PDF loaded. Add XML export for improved accuracy.")

    # Use HTML text when available, fall back to PDF text
    structured_text = html_text if html_text else full_text
    # Always use full_text for addendum (narrative) — PDF is better for that
    narrative_text  = full_text

    def extract_int(text):
        if text is None:
            return None
        clean = re.sub(r'[$,+]', '', str(text).strip())
        try:
            return int(float(clean))
        except Exception:
            return None

    def find_adj_rate(text, label_pattern):
        m = re.search(label_pattern, text, re.IGNORECASE)
        if m:
            return extract_int(m.group(1))
        return None

    # Extract adjustment rates from addendum
    adj_section = ""
    for marker in ["Adjustments made:", "Adjustment rates:", "adjustments are"]:
        idx = narrative_text.find(marker)
        if idx != -1:
            adj_section = narrative_text[idx:idx+600]
            break

    stated_gla_rate  = find_adj_rate(adj_section, r'\$([\d,]+)\s*per\s*SF\s*GLA')
    stated_bed_rate  = find_adj_rate(adj_section, r'[Bb]edroom[s]?\s*adj\s*[@\$]\s*\$?([\d,]+)')
    stated_bath_rate = find_adj_rate(adj_section, r'Full\s*[Bb]ath\s*adj\s*[@\$]\s*\$?([\d,]+)')
    stated_gar_rate  = find_adj_rate(adj_section, r'[Gg]arage\s*adj\s*[@\$]\s*\$?([\d,]+)')
    stated_bsmt_rate = find_adj_rate(adj_section, r'[Bb]asement\s*adj\s*[@\$]\s*\$?([\d,]+)')

    # Subject data
    subj_gla = None
    size_idx = structured_text.find("Size (Square Feet)")
    if size_idx != -1:
        m = re.search(r'(\d[,\d]+)', structured_text[size_idx:size_idx+100])
        if m:
            subj_gla = extract_int(m.group(1))

    cond_match = re.search(
        r'(C[1-6]|Average-Above|Above Average|Average|Below Average|Good|Fair)',
        structured_text[:5000])
    subj_condition = cond_match.group(1) if cond_match else ""

    rooms_match = re.search(r'(\d)\s+Rooms\s+(\d)\s+Bedrooms\s+(\d)\s+Bath', structured_text)
    form_rooms = int(rooms_match.group(1)) if rooms_match else None

    # Comp extraction
    comps = []
    comp_sections = re.split(r'COMPARABLE SALE #?\s*\d', structured_text)
    for i, block in enumerate(comp_sections[1:6], 1):
        addr_m  = re.search(r'(\d+\s+[A-Za-z][^\n]+(?:Ave|St|Dr|Rd|Ln|Blvd|Way|Ct)[^\n]*)', block)
        price_m = re.search(r'\n([\d,]{5,})\n', block[:200])
        gla_m   = re.search(r'\n(\d{3,4})\n([+\-][\d,]+)\n', block)
        cond_m  = re.search(
            r'(C[1-6]|Average-Above|Above Average|Average|Below Average)\n([+\-][\d,]+|0)\n',
            block)
        net_matches = re.findall(r'([+\-][\d,]+)\n([\d,]+)\n', block[-300:])

        comps.append({
            "num":       i,
            "address":   addr_m.group(1).strip() if addr_m else f"Comp #{i}",
            "price":     extract_int(price_m.group(1)) if price_m else None,
            "gla":       extract_int(gla_m.group(1)) if gla_m else None,
            "gla_adj":   extract_int(gla_m.group(2)) if gla_m else None,
            "condition": cond_m.group(1) if cond_m else "",
            "cond_adj":  extract_int(cond_m.group(2)) if cond_m else None,
            "net_adj":   extract_int(net_matches[-1][0]) if net_matches else None,
            "adj_value": extract_int(net_matches[-1][1]) if net_matches else None,
        })

    # Display extracted data
    with st.expander("Extracted Data — expand to review", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Stated Adjustment Rates**")
            st.write(f"GLA: ${stated_gla_rate:,}/sf" if stated_gla_rate else "GLA rate: not found")
            st.write(f"Bedroom: ${stated_bed_rate:,}" if stated_bed_rate else "Bedroom rate: not found")
            st.write(f"Full Bath: ${stated_bath_rate:,}" if stated_bath_rate else "Bath rate: not found")
            st.write(f"Garage: ${stated_gar_rate:,}/stall" if stated_gar_rate else "Garage rate: not found")
            st.write(f"Basement: ${stated_bsmt_rate:,}" if stated_bsmt_rate else "Basement rate: not found")
        with col2:
            st.markdown("**Subject**")
            st.write(f"GLA: {subj_gla:,} sf" if subj_gla else "GLA: not found")
            st.write(f"Condition: {subj_condition}" if subj_condition else "Condition: not found")
            st.write(f"Rooms: {form_rooms}" if form_rooms else "Room count: not found")
        if comps:
            st.markdown("**Comps Found**")
            for c in comps:
                p = f"${c['price']:,}" if c['price'] else "—"
                g = f"{c['gla']:,} sf" if c['gla'] else "—"
                st.write(f"Comp #{c['num']}: {c['address'][:35]} | {p} | GLA {g} | {c['condition']}")

    # Manual inputs
    st.divider()
    st.markdown("### Manual Inputs")
    st.caption("Sketch rooms can't be extracted from image-based sketch pages — enter manually.")

    mi1, mi2 = st.columns(2)
    with mi1:
        sketch_rooms  = st.number_input("Sketch room count (above grade)",
                                         min_value=0, max_value=20,
                                         value=form_rooms or 0, key="qc_sketch_rooms")
        sketch_gla    = st.number_input("Sketch GLA (sq ft)",
                                         min_value=0, max_value=10000,
                                         value=subj_gla or 0, key="qc_sketch_gla")
    with mi2:
        form_rooms_in = st.number_input("Form stated room count",
                                         min_value=0, max_value=20,
                                         value=form_rooms or 0, key="qc_form_rooms")
        form_gla_in   = st.number_input("Form stated GLA (sq ft)",
                                         min_value=0, max_value=10000,
                                         value=subj_gla or 0, key="qc_form_gla")

    with st.expander("Override extracted adjustment rates"):
        or1, or2, or3 = st.columns(3)
        with or1:
            gla_rate  = st.number_input("GLA rate ($/sf)",
                                         value=float(stated_gla_rate or 35), key="qc_gla_rate")
            bed_rate  = st.number_input("Bedroom rate ($)",
                                         value=float(stated_bed_rate or 5000), key="qc_bed_rate")
        with or2:
            bath_rate = st.number_input("Full Bath rate ($)",
                                         value=float(stated_bath_rate or 3000), key="qc_bath_rate")
            gar_rate  = st.number_input("Garage rate ($/stall)",
                                         value=float(stated_gar_rate or 10000), key="qc_gar_rate")
        with or3:
            bsmt_rate     = st.number_input("Basement rate ($)",
                                              value=float(stated_bsmt_rate or 10000), key="qc_bsmt_rate")
            gla_threshold = st.number_input("GLA threshold (sf, adj only above this)",
                                              value=50.0, key="qc_gla_thresh")

    # Run checks
    st.divider()
    if st.button("Run QC Checks", type="primary", use_container_width=True, key="qc_run"):

        flags  = []
        passes = []

        def flag(cat, msg, sev="warning"):
            flags.append({"cat": cat, "msg": msg, "sev": sev})

        def ok(cat, msg):
            passes.append({"cat": cat, "msg": msg})

        # 1 — Room count vs sketch
        if form_rooms_in > 0 and sketch_rooms > 0:
            if form_rooms_in != sketch_rooms:
                flag("Room Count",
                     f"Form states {form_rooms_in} rooms above grade but "
                     f"sketch shows {sketch_rooms} rooms.", "critical")
            else:
                ok("Room Count", f"Form and sketch agree: {form_rooms_in} rooms.")

        # 2 — GLA form vs sketch
        if form_gla_in > 0 and sketch_gla > 0:
            diff = abs(form_gla_in - sketch_gla)
            pct  = diff / form_gla_in * 100
            if diff > 20:
                sev = "critical" if pct > 5 else "warning"
                flag("GLA Discrepancy",
                     f"Form GLA {form_gla_in:,} sf vs sketch GLA {sketch_gla:,} sf "
                     f"— difference of {diff} sf ({pct:.1f}%).", sev)
            else:
                ok("GLA", "Form and sketch GLA agree within 20 sf.")

        # 3 — GLA adjustment rate consistency
        if subj_gla and gla_rate and comps:
            gla_issues = []
            for c in comps:
                if c["gla"] and c["gla_adj"] is not None and c["gla_adj"] != 0:
                    diff = subj_gla - c["gla"]
                    adj_diff = diff - gla_threshold if diff > 0 else diff + gla_threshold if diff < 0 else 0
                    expected = int(adj_diff * gla_rate)
                    actual   = c["gla_adj"]
                    variance = abs(actual - expected)
                    if variance > 500:
                        gla_issues.append(
                            f"Comp #{c['num']} ({c['address'][:25]}): "
                            f"GLA diff {diff:+,} sf → expected ~${expected:,} "
                            f"but report shows ${actual:,} (off by ${variance:,})"
                        )
            if gla_issues:
                for iss in gla_issues:
                    flag("GLA Adj Rate", iss)
            else:
                ok("GLA Adj Rate",
                   f"GLA adjustments consistent with stated ${int(gla_rate)}/sf rate.")

        # 4 — Condition adjustment consistency
        if comps:
            cond_map = {}
            for c in comps:
                if c["condition"] and c["cond_adj"] is not None:
                    cond_map.setdefault(c["condition"], []).append((c["num"], c["cond_adj"]))
            issues = []
            for cond, entries in cond_map.items():
                adjs = set(e[1] for e in entries)
                if len(adjs) > 1:
                    detail = ", ".join([f"Comp #{n}: ${a:,}" for n,a in entries])
                    issues.append(
                        f"Comps rated '{cond}' have different adjustments: {detail}"
                    )
            if issues:
                for iss in issues:
                    flag("Condition Adj Consistency", iss)
            elif cond_map:
                ok("Condition Adj Consistency",
                   "Condition adjustments consistent for comps with matching ratings.")

        # 5 — Condition rating vs narrative language
        if subj_condition:
            addendum_lower = narrative_text.lower()
            cond_conflicts = {
                "deferred maintenance": ["C4","C5","C6","Average","Below Average","Fair"],
                "needs repair": ["C5","C6","Below Average"],
                "significant deterioration": ["C5","C6"],
            }
            for phrase, expected in cond_conflicts.items():
                if phrase in addendum_lower:
                    if not any(e.lower() in subj_condition.lower() for e in expected):
                        flag("Condition vs Narrative",
                             f"Addendum mentions '{phrase}' but condition "
                             f"rated '{subj_condition}'.")
            ok("Condition vs Narrative",
               "No major conflicts between condition rating and narrative.")

        # 6 — Prior sale addressed
        prior_phrases = ["No other prior sales", "no prior sales", "prior sale",
                          "prior transfer", "1st Prior Subject", "did not reveal"]
        if any(p in narrative_text for p in prior_phrases):
            ok("Prior Sale", "Prior sale / transfer history addressed.")
        else:
            flag("Prior Sale",
                 "No prior sale or transfer history language found. "
                 "Verify transfer history section is complete.")

        # 7 — Market conditions narrative consistency
        mkt_idx = structured_text.find("Market Area Boundaries")
        if mkt_idx != -1:
            mkt_chunk = structured_text[mkt_idx:mkt_idx+300].lower()
            if "shortage" in mkt_chunk and "over 6" in narrative_text.lower():
                flag("Market Conditions",
                     "Supply/demand shows 'Shortage' but marketing time may indicate 'Over 6 Months'.")
            elif "over supply" in mkt_chunk and "under 3" in narrative_text.lower():
                flag("Market Conditions",
                     "Supply/demand shows 'Over Supply' but marketing time may indicate 'Under 3 Months'.")
            else:
                ok("Market Conditions", "Market conditions checkboxes appear internally consistent.")

        # 8 — Adjustment support language in addendum
        if not adj_section:
            flag("Adjustment Support",
                 "No adjustment rate statement found in addendum. "
                 "Verify adjustment support language is present.", "critical")
        else:
            ok("Adjustment Support", "Adjustment rate statement present in addendum.")

        # 9 — Comp date range
        dates_in_report = re.findall(r'\d{2}/\d{2}/(\d{4})', structured_text)
        years = sorted(set(int(y) for y in dates_in_report if 2000 < int(y) < 2030))
        if years:
            span = max(years) - min(years)
            if span > 2:
                flag("Comp Date Range",
                     f"Report contains dates spanning {span} years. "
                     f"Verify extended search explanation is in addendum.")
            else:
                ok("Comp Date Range", "Comp dates appear within acceptable range.")

        # ── Results display ───────────────────────────────────────────────
        st.markdown("---")
        st.markdown("## QC Results")

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

        if adj_section:
            with st.expander("Addendum adjustment text (as extracted)"):
                st.text(adj_section[:500])
