"""
A-Tech Appraisal Co. — Revision & Comment Library
Streamlit Web App
"""

import os, json
import streamlit as st

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
st.title("Revision & Comment Library")
st.caption("Search, copy, and manage revision responses and appraisal addendum comments.")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_rev, tab_com, tab_hood, tab_zone = st.tabs([
    "📋 Revision Responses",
    "📝 Appraisal Comments",
    "🏘️ Neighborhood Descriptions",
    "📐 Zoning Districts"
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
