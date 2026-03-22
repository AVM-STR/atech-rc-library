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


def generate_gp_res_pdf(ss):
    """Generate GP Residential PDF from session state."""
    buf = io.BytesIO()

    # Colors
    BLACK      = colors.HexColor("#0A0A0A")
    DARK_GRAY  = colors.HexColor("#222222")
    MID_GRAY   = colors.HexColor("#666666")
    LIGHT_GRAY = colors.HexColor("#CCCCCC")
    VERY_LIGHT = colors.HexColor("#F2F2F2")
    WHITE      = colors.white
    W, H       = letter

    def S(name, **kw):
        return ParagraphStyle(name, **kw)

    body  = S("body", fontName="Helvetica", fontSize=9.5, textColor=DARK_GRAY,
               leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
    fl    = S("fl", fontName="Helvetica-Bold", fontSize=8, textColor=MID_GRAY, spaceAfter=1)
    fv    = S("fv", fontName="Helvetica", fontSize=10, textColor=DARK_GRAY, spaceAfter=5)
    sl    = S("sl", fontName="Helvetica", fontSize=7.5, textColor=MID_GRAY, spaceAfter=1)
    sv    = S("sv", fontName="Helvetica-Bold", fontSize=8.5, textColor=DARK_GRAY, spaceAfter=3)

    def banner(text, dark=True, w=7.2*inch):
        bg = BLACK if dark else DARK_GRAY
        t = Table([[Paragraph(text, S("bh", fontName="Helvetica-Bold",
                    fontSize=11, textColor=WHITE))]], colWidths=[w])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),bg),
            ("LEFTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),7),
            ("BOTTOMPADDING",(0,0),(-1,-1),7),
        ]))
        return t

    def sub_banner(text, w=7.2*inch):
        t = Table([[Paragraph(text, S("sbh", fontName="Helvetica-Bold",
                    fontSize=10, textColor=WHITE))]], colWidths=[w])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),MID_GRAY),
            ("LEFTPADDING",(0,0),(-1,-1),10),
            ("TOPPADDING",(0,0),(-1,-1),6),
            ("BOTTOMPADDING",(0,0),(-1,-1),6),
        ]))
        return t

    def stat_card(label, value, width=1.75*inch):
        t = Table([[Paragraph(label, S("sclabel", fontName="Helvetica", fontSize=7.5,
                               textColor=MID_GRAY, alignment=TA_CENTER))],
                   [Paragraph(value, S("scvalue", fontName="Helvetica-Bold", fontSize=10,
                               textColor=BLACK, alignment=TA_CENTER))]],
                  colWidths=[width])
        t.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1),VERY_LIGHT),
            ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
            ("BOX",(0,0),(-1,-1),0.75,LIGHT_GRAY),
        ]))
        return t

    def four_stats(items):
        row = [stat_card(l, v, 1.8*inch) for l,v in items]
        t = Table([row], colWidths=[1.8*inch]*4)
        t.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),
                                ("RIGHTPADDING",(0,0),(-1,-1),3)]))
        return t

    def detail_grid(left, right):
        rows = []
        for i in range(max(len(left), len(right))):
            ll, lv = left[i]  if i < len(left)  else ("","")
            rl, rv = right[i] if i < len(right) else ("","")
            rows.append([Paragraph(ll,fl), Paragraph(lv,fv),
                         Paragraph(rl,fl), Paragraph(rv,fv)])
        t = Table(rows, colWidths=[1.35*inch, 2.2*inch, 1.35*inch, 2.2*inch])
        t.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"TOP"),
            ("LEFTPADDING",(0,0),(-1,-1),0),
            ("LEFTPADDING",(2,0),(2,-1),16),
        ]))
        return t

    def img_cell(file_obj, w, h, label="[ PHOTO ]"):
        """Convert uploaded file to RLImage or placeholder."""
        class PhotoBox(Flowable):
            def __init__(self, width, height, lbl):
                Flowable.__init__(self)
                self.width = width; self.height = height; self.lbl = lbl
            def draw(self):
                c = self.canv
                c.setFillColor(colors.HexColor("#DDDDDD"))
                c.setStrokeColor(colors.HexColor("#BBBBBB"))
                c.setLineWidth(0.5)
                c.roundRect(0, 0, self.width, self.height, 3, fill=1, stroke=1)
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.HexColor("#888888"))
                c.drawCentredString(self.width/2, self.height/2-5, self.lbl)

        if file_obj is None:
            return PhotoBox(w, h, label)
        try:
            file_obj.seek(0)
            img_data = file_obj.read()
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            tmp.write(img_data)
            tmp.close()
            return RLImage(tmp.name, width=w, height=h)
        except Exception:
            return PhotoBox(w, h, label)

    doc = SimpleDocTemplate(buf, pagesize=letter,
        rightMargin=0.65*inch, leftMargin=0.65*inch,
        topMargin=0.65*inch, bottomMargin=0.65*inch)

    story = []
    addr1  = ss.get("rb_address1","")
    addr2  = ss.get("rb_address2","")
    eff_dt = ss.get("rb_effective_date","")
    value  = ss.get("rb_opinion_value","")
    value_str = f"${value}" if value and not value.startswith("$") else value

    # ══ PAGE 1: COVER ══════════════════════════════════════════════════════
    # Logo header
    logo_path = os.path.join(os.path.dirname(__file__), "atech_logo.png")
    if os.path.exists(logo_path):
        logo = RLImage(logo_path, width=2.2*inch, height=0.48*inch)
    else:
        logo = Paragraph("A-TECH APPRAISAL CO., LLC",
                          S("lgf", fontName="Helvetica-Bold", fontSize=12, textColor=BLACK))

    contact = Table([
        [Paragraph("P.O. Box 9464, Warwick, RI 02889",
                   S("c1", fontName="Helvetica", fontSize=8.5,
                     textColor=DARK_GRAY, alignment=TA_RIGHT))],
        [Paragraph("(401) 921-4055  |  www.a-techappraisal.com",
                   S("c2", fontName="Helvetica", fontSize=8.5,
                     textColor=DARK_GRAY, alignment=TA_RIGHT))],
    ], colWidths=[4.9*inch])
    contact.setStyle(TableStyle([
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
    ]))

    hdr = Table([[logo, contact]], colWidths=[2.3*inch, 4.9*inch])
    hdr.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
    ]))
    story.append(hdr)
    story.append(HRFlowable(width="100%", thickness=0.75, color=LIGHT_GRAY,
                            spaceBefore=8, spaceAfter=10))

    # Report title
    story.append(Paragraph("Residential Appraisal Report",
        S("title", fontName="Helvetica-Bold", fontSize=16,
          textColor=BLACK, spaceAfter=2)))
    story.append(Paragraph("Opinion of Market Value — Fee Simple Interest",
        S("sub", fontName="Helvetica", fontSize=10,
          textColor=MID_GRAY, spaceAfter=8)))
    story.append(HRFlowable(width="100%", thickness=0.75, color=LIGHT_GRAY, spaceAfter=12))

    # Photo left + info right
    front_file = ss.get("rb_photo_front")
    photo_cell = img_cell(front_file, 3.1*inch, 2.2*inch, "[ FRONT EXTERIOR ]")

    lk = S("lk2", fontName="Helvetica-Bold", fontSize=8.5, textColor=DARK_GRAY,
            spaceAfter=1, spaceBefore=3)
    lv2 = S("lv2", fontName="Helvetica", fontSize=9, textColor=BLACK,
             spaceAfter=0)

    style_text = f"{ss.get('rb_style_attach','')} {ss.get('rb_style_floors','')} Story {ss.get('rb_style_type','')}"
    beds  = ss.get("rb_bedrooms","—")
    baths = ss.get("rb_bathrooms_full","—")
    half  = ss.get("rb_bathrooms_half","0")
    bath_str = f"{baths} Full" + (f"  |  {half} Half" if half and half != "0" else "")

    info_rows = [
        [Paragraph("<b>Subject Property:</b>", lk), ""],
        [Paragraph(addr1, S("adr", fontName="Helvetica-Bold", fontSize=13,
                             textColor=BLACK, spaceAfter=1)), ""],
        [Paragraph(addr2, lv2), ""],
        [Paragraph("<b>Style:</b>", lk), Paragraph(style_text.strip(), lv2)],
        [Paragraph("<b>Living Area:</b>", lk), Paragraph(f"{ss.get('rb_gla','—')} sq ft", lv2)],
        [Paragraph("<b>Bedrooms / Baths:</b>", lk), Paragraph(f"{beds} Bedrooms  |  {bath_str}", lv2)],
        [Paragraph("<b>Year Built:</b>", lk), Paragraph(ss.get("rb_year_built","—"), lv2)],
        [Paragraph("<b>Property Rights:</b>", lk), Paragraph(ss.get("rb_property_rights","Fee Simple"), lv2)],
        [Paragraph("<b>Tax Year / Amount:</b>", lk),
         Paragraph(f"{ss.get('rb_tax_year','—')}  |  ${ss.get('rb_tax_amount','—')}", lv2)],
        [Paragraph("<b>Effective Date:</b>", lk), Paragraph(eff_dt, lv2)],
        [Paragraph("<b>Prepared By:</b>", lk),
         Paragraph("Spencer Webb, CRA  |  A-Tech Appraisal Co., LLC", lv2)],
    ]
    info_t = Table(info_rows, colWidths=[1.5*inch, 2.35*inch])
    info_t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),4),
    ]))

    top_t = Table([[photo_cell, info_t]], colWidths=[3.2*inch, 4.0*inch])
    top_t.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),0),("RIGHTPADDING",(0,0),(-1,-1),0),
        ("TOPPADDING",(0,0),(-1,-1),0),("BOTTOMPADDING",(0,0),(-1,-1),0),
        ("RIGHTPADDING",(0,0),(0,-1),16),
        ("LEFTPADDING",(1,0),(1,-1),6),
    ]))
    story.append(top_t)
    story.append(Spacer(1, 12))

    # Summary metrics box
    story.append(Paragraph("Appraisal Summary",
        S("h1s", fontName="Helvetica-Bold", fontSize=11,
          textColor=BLACK, spaceAfter=6)))

    ml = S("ml2", fontName="Helvetica", fontSize=8, textColor=MID_GRAY, alignment=TA_CENTER)
    mv = S("mv2", fontName="Helvetica-Bold", fontSize=14, textColor=BLACK,
            alignment=TA_CENTER, leading=18)
    cw = 7.2*inch/3
    cond  = ss.get("rb_condition_rating","—")
    gla   = ss.get("rb_gla","")
    try:
        ppsf = f"${int(value.replace(',','').replace('$','')) / int(gla.replace(',','')):.0f}/sf" if value and gla else "—"
    except Exception:
        ppsf = "—"

    mx = Table([
        [Paragraph("Opinion of Market Value", ml),
         Paragraph("Price Per Sq Ft", ml),
         Paragraph("Condition", ml)],
        [Paragraph(value_str or "—", mv),
         Paragraph(ppsf, mv),
         Paragraph(cond.split(" — ")[0] if "—" in cond else cond, mv)],
        [Paragraph("Intended Use", ml),
         Paragraph("Effective Date", ml),
         Paragraph("Inspection Type", ml)],
        [Paragraph(ss.get("rb_intended_use","Market Value")[:30], mv),
         Paragraph(eff_dt, mv),
         Paragraph(ss.get("rb_inspection_type","Interior & Exterior"), mv)],
    ], colWidths=[cw]*3)
    mx.setStyle(TableStyle([
        ("BOX",(0,0),(-1,-1),0.75,LIGHT_GRAY),
        ("INNERGRID",(0,0),(-1,-1),0.5,LIGHT_GRAY),
        ("BACKGROUND",(0,0),(-1,-1),VERY_LIGHT),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LEFTPADDING",(0,0),(-1,-1),6),("RIGHTPADDING",(0,0),(-1,-1),6),
    ]))
    story.append(mx)
    story.append(Spacer(1, 10))

    # Prepared for / USPAP footer
    story.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY, spaceAfter=6))
    story.append(Paragraph(
        f"Prepared for: <b>{ss.get('rb_intended_user','')}</b>  |  "
        f"Intended Use: <b>{ss.get('rb_intended_use','')}</b>  |  "
        f"Property Rights: <b>{ss.get('rb_property_rights','Fee Simple')}</b>",
        S("pfooter", fontName="Helvetica", fontSize=8, textColor=MID_GRAY,
          leading=12)))
    story.append(Paragraph(
        "This appraisal was developed in conformity with USPAP. The opinion of value is as of the "
        "stated effective date and is contingent upon the certification and limiting conditions attached.",
        S("ufooter", fontName="Helvetica", fontSize=8, textColor=MID_GRAY,
          alignment=TA_JUSTIFY, leading=12)))

    story.append(PageBreak())

    # ══ PAGE 2: SUBJECT PHOTOS & IMPROVEMENTS ════════════════════════════
    story.append(banner("SUBJECT PROPERTY PHOTOS"))
    story.append(Spacer(1, 0.12*inch))

    # Exterior 3-up
    ext_row = Table([[
        img_cell(ss.get("rb_photo_front"), 2.3*inch, 1.7*inch, "[ FRONT EXTERIOR ]"),
        img_cell(ss.get("rb_photo_rear"),  2.3*inch, 1.7*inch, "[ REAR EXTERIOR ]"),
        img_cell(ss.get("rb_photo_street"),2.3*inch, 1.7*inch, "[ STREET SCENE ]"),
    ]], colWidths=[2.4*inch]*3)
    ext_row.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
    story.append(ext_row)
    story.append(Spacer(1, 0.1*inch))

    # Interior room photos
    room_photos = ss.get("rb_room_photos", [])
    if room_photos:
        for i in range(0, len(room_photos), 3):
            batch = room_photos[i:i+3]
            while len(batch) < 3:
                batch.append({"label":"","file":None})
            row = Table([[
                Table([[img_cell(b["file"], 2.25*inch, 1.65*inch, f'[ {b["label"].upper()} ]')],
                       [Paragraph(b["label"],
                                   S("rl", fontName="Helvetica", fontSize=7.5,
                                     textColor=MID_GRAY, alignment=TA_CENTER))]],
                      colWidths=[2.35*inch])
                for b in batch
            ]], colWidths=[2.4*inch]*3)
            row.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
            story.append(row)
            story.append(Spacer(1, 0.08*inch))

    story.append(Spacer(1, 0.1*inch))
    story.append(sub_banner("IMPROVEMENTS DESCRIPTION"))
    story.append(Spacer(1, 0.12*inch))

    amenities_str = ", ".join(ss.get("rb_amenities",[]) or ["None noted"])
    bsmt_type = ss.get("rb_basement_type","—")
    bsmt_sf   = ss.get("rb_basement_sf","")
    bsmt_fin  = ss.get("rb_basement_fin_sf","")
    bsmt_rms  = ss.get("rb_basement_fin_rooms","")
    bsmt_str  = bsmt_type
    if bsmt_sf:
        bsmt_str += f" — {bsmt_sf} sf"
    if bsmt_fin and bsmt_fin != "0":
        bsmt_str += f" / {bsmt_fin} sf finished"
        if bsmt_rms:
            bsmt_str += f" ({bsmt_rms} rooms)"

    story.append(detail_grid(
        [("STYLE / DESIGN", f"{ss.get('rb_style_attach','')} — {ss.get('rb_style_floors','')} Story {ss.get('rb_style_type','')}"),
         ("GROSS LIVING AREA", f"{ss.get('rb_gla','—')} sq ft above grade"),
         ("ROOM COUNT", f"{ss.get('rb_total_rooms','—')} rooms — {ss.get('rb_bedrooms','—')} bed, {ss.get('rb_bathrooms_full','—')} full bath, {ss.get('rb_bathrooms_half','0')} half bath"),
         ("BASEMENT", bsmt_str),
         ("AMENITIES", amenities_str)],
        [("YEAR BUILT", ss.get("rb_year_built","—")),
         ("PARKING", ss.get("rb_parking","—")),
         ("LOT SIZE", ss.get("rb_lot_size","—")),
         ("ZONING", f"{ss.get('rb_zoning','')} — {ss.get('rb_zoning_req','')}"),
         ("ZONING STATUS", ss.get("rb_zoning_comments","—"))]
    ))

    story.append(PageBreak())

    # ══ PAGE 3: CONDITION & NEIGHBORHOOD ═════════════════════════════════
    story.append(banner("PROPERTY DESCRIPTION & RATING"))
    story.append(Spacer(1, 0.12*inch))

    cond_text = ss.get("rb_condition_narrative","")
    if cond_text:
        story.append(Paragraph(cond_text, body))

    story.append(Spacer(1, 0.1*inch))
    story.append(four_stats([
        ("CONDITION RATING", ss.get("rb_condition_rating","—").split(" — ")[0]),
        ("QUALITY RATING",   ss.get("rb_quality_rating","—").split(" — ")[0]),
        ("YEAR BUILT",       ss.get("rb_year_built","—")),
        ("GROSS LIVING AREA",f"{ss.get('rb_gla','—')} sf"),
    ]))
    story.append(Spacer(1, 0.18*inch))

    story.append(sub_banner("NEIGHBORHOOD & MARKET CONDITIONS"))
    story.append(Spacer(1, 0.1*inch))

    hood = ss.get("rb_neighborhood_desc","")
    if hood:
        story.append(Paragraph(hood, body))
    mkt = ss.get("rb_market_desc","")
    if mkt:
        story.append(Paragraph(mkt, body))

    story.append(Spacer(1, 0.1*inch))
    story.append(four_stats([
        ("MARKET CONDITIONS", ss.get("rb_market_conditions","Stable")),
        ("SUPPLY / DEMAND",   ss.get("rb_supply_demand","—")),
        ("MARKETING TIME",    ss.get("rb_marketing_time","—")),
        ("GROWTH RATE",       ss.get("rb_growth_rate","—")),
    ]))
    story.append(Spacer(1, 0.12*inch))

    # Housing trends
    pl = ss.get("rb_price_low","")
    ph = ss.get("rb_price_high","")
    pp = ss.get("rb_price_pred","")
    al = ss.get("rb_age_low","")
    ah = ss.get("rb_age_high","")
    ap = ss.get("rb_age_pred","")
    if any([pl, ph, pp, al, ah, ap]):
        story.append(sub_banner("ONE-UNIT HOUSING TRENDS"))
        story.append(Spacer(1,0.08*inch))
        story.append(detail_grid(
            [("PRICE LOW", pl), ("PRICE HIGH", ph), ("PRICE PREDOMINANT", pp)],
            [("AGE LOW (YRS)", al), ("AGE HIGH (YRS)", ah), ("AGE PREDOMINANT (YRS)", ap)]
        ))
    story.append(PageBreak())

    # ══ PAGE 4: COMPS ══════════════════════════════════════════════════════
    story.append(banner("COMPARABLE SALES ANALYSIS"))
    story.append(Spacer(1, 0.12*inch))

    comp_df_json = ss.get("rb_comp_df")
    if comp_df_json:
        try:
            import pandas as pd
            df = pd.read_json(comp_df_json)
            # Build a clean table from the CSV
            cols = list(df.columns)
            header = [Paragraph(str(c)[:20], S("ch2", fontName="Helvetica-Bold",
                        fontSize=7, textColor=WHITE, alignment=TA_CENTER))
                      for c in cols[:8]]
            rows = [header]
            for _, row in df.head(6).iterrows():
                rows.append([Paragraph(str(row[c])[:25],
                              S("cd2", fontName="Helvetica", fontSize=7.5,
                                textColor=DARK_GRAY))
                             for c in cols[:8]])
            cw_comp = 7.2*inch / min(8, len(cols))
            ct = Table(rows, colWidths=[cw_comp]*min(8,len(cols)), repeatRows=1)
            ct.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),BLACK),
                ("ROWBACKGROUNDS",(0,1),(-1,-1),[WHITE, VERY_LIGHT]),
                ("BOX",(0,0),(-1,-1),0.5,LIGHT_GRAY),
                ("INNERGRID",(0,0),(-1,-1),0.3,LIGHT_GRAY),
                ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
                ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ]))
            story.append(ct)
        except Exception as e:
            story.append(Paragraph(f"Comp data error: {e}", body))
    else:
        story.append(Paragraph("No comparable sales CSV uploaded.", body))

    # Comp photos
    story.append(Spacer(1, 0.15*inch))
    story.append(sub_banner("COMPARABLE SALE PHOTOS"))
    story.append(Spacer(1, 0.1*inch))
    comp_batch = []
    for i in range(5):
        f = ss.get(f"rb_comp_photo_{i}")
        addr = ss.get(f"rb_comp_addr_{i}", f"Comparable #{i+1}")
        comp_batch.append({"file":f, "label":addr})
    for i in range(0, 5, 3):
        batch = comp_batch[i:i+3]
        while len(batch) < 3:
            batch.append({"file":None,"label":""})
        row = Table([[
            Table([[img_cell(b["file"], 2.25*inch, 1.65*inch, f"[ COMP #{i+j+1} ]")],
                   [Paragraph(b["label"][:30],
                               S("cl2", fontName="Helvetica", fontSize=7,
                                 textColor=MID_GRAY, alignment=TA_CENTER))]],
                  colWidths=[2.35*inch])
            for j, b in enumerate(batch)
        ]], colWidths=[2.4*inch]*3)
        row.setStyle(TableStyle([("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3)]))
        story.append(row)
        story.append(Spacer(1, 0.08*inch))

    story.append(PageBreak())

    # ══ PAGE 5: MAPS ══════════════════════════════════════════════════════
    story.append(banner("MAPS"))
    story.append(Spacer(1, 0.12*inch))

    maps_row = Table([[
        Table([[Paragraph("Plat Map", S("maplbl", fontName="Helvetica-Bold", fontSize=8,
                           textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=4))],
               [img_cell(ss.get("rb_plat_map_file"), 3.4*inch, 2.5*inch, "[ PLAT MAP ]")]],
              colWidths=[3.5*inch]),
        Table([[Paragraph("Comparable Sales Map", S("maplbl2", fontName="Helvetica-Bold",
                           fontSize=8, textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=4))],
               [img_cell(ss.get("rb_comp_map_file"), 3.4*inch, 2.5*inch, "[ COMP MAP ]")]],
              colWidths=[3.5*inch]),
    ]], colWidths=[3.6*inch, 3.6*inch])
    maps_row.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(maps_row)
    story.append(PageBreak())

    # ══ PAGE 6: RECONCILIATION & VALUE ════════════════════════════════════
    story.append(banner("FINAL VALUE CONCLUSION & RECONCILIATION"))
    story.append(Spacer(1, 0.12*inch))

    recon = ss.get("rb_reconciliation","")
    if recon:
        story.append(Paragraph(recon, body))

    # Final value banner
    fv_t = Table([[
        Paragraph("FINAL OPINION OF MARKET VALUE",
                  S("fvl2", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE)),
        Paragraph(f"AS OF {eff_dt.upper()}",
                  S("fvd2", fontName="Helvetica", fontSize=9,
                    textColor=colors.HexColor("#BBBBBB"), alignment=TA_RIGHT)),
    ],[
        Paragraph(value_str or "—",
                  S("fvv2", fontName="Helvetica-Bold", fontSize=26, textColor=WHITE)),
        Paragraph("",S("fvw2", fontName="Helvetica", fontSize=9, textColor=WHITE)),
    ]], colWidths=[4.8*inch, 2.4*inch])
    fv_t.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),BLACK),
        ("TOPPADDING",(0,0),(-1,0),12),("BOTTOMPADDING",(0,0),(-1,0),6),
        ("TOPPADDING",(0,1),(-1,1),4),("BOTTOMPADDING",(0,1),(-1,1),14),
        ("LEFTPADDING",(0,0),(-1,-1),14),("RIGHTPADDING",(0,0),(-1,-1),14),
        ("VALIGN",(0,0),(-1,0),"BOTTOM"),("VALIGN",(0,1),(-1,1),"TOP"),
    ]))
    story.append(fv_t)
    story.append(PageBreak())

    # ══ PAGE 7: SKETCH ════════════════════════════════════════════════════
    story.append(banner("FLOOR PLAN / SKETCH"))
    story.append(Spacer(1, 0.12*inch))

    sketch_row = Table([[
        Table([[Paragraph("Above Grade", S("sktl", fontName="Helvetica-Bold", fontSize=8,
                           textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=4))],
               [img_cell(ss.get("rb_sketch_ag_file"), 3.4*inch, 3.0*inch, "[ ABOVE GRADE FLOOR PLAN ]")]],
              colWidths=[3.5*inch]),
        Table([[Paragraph("Basement / Below Grade", S("sktl2", fontName="Helvetica-Bold",
                           fontSize=8, textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=4))],
               [img_cell(ss.get("rb_sketch_bg_file"), 3.4*inch, 3.0*inch, "[ BASEMENT FLOOR PLAN ]")]],
              colWidths=[3.5*inch]),
    ]], colWidths=[3.6*inch, 3.6*inch])
    sketch_row.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("LEFTPADDING",(0,0),(-1,-1),3),("RIGHTPADDING",(0,0),(-1,-1),3),
    ]))
    story.append(sketch_row)
    story.append(PageBreak())

    # ══ PAGE 8: SCOPE & LIMITING CONDITIONS ═══════════════════════════════
    story.append(banner("SCOPE OF WORK"))
    story.append(Spacer(1, 0.1*inch))
    sow = ss.get("rb_scope_of_work","")
    if sow:
        story.append(Paragraph(sow, body))

    story.append(Spacer(1, 0.15*inch))
    story.append(sub_banner("LIMITING CONDITIONS"))
    story.append(Spacer(1, 0.1*inch))

    lc_text = ss.get("rb_limiting_conditions","")
    for para in lc_text.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), body))
    story.append(PageBreak())

    # ══ FINAL PAGE: CERTIFICATION & SIGNATURE ═════════════════════════════
    story.append(banner("APPRAISER CERTIFICATION & SIGNATURE"))
    story.append(Spacer(1, 0.15*inch))

    # USPAP certification text
    cert_text = (
        "I certify that, to the best of my knowledge and belief: the statements of fact contained in this "
        "report are true and correct; the reported analyses, opinions, and conclusions are limited only by "
        "the reported assumptions and limiting conditions and are my personal, impartial, and unbiased "
        "professional analyses, opinions, and conclusions; I have no present or prospective interest in the "
        "property that is the subject of this report; my engagement in this assignment was not contingent "
        "upon developing or reporting predetermined results; my compensation is not contingent upon the "
        "development or reporting of a predetermined value; and this report was prepared in conformity with "
        "the Uniform Standards of Professional Appraisal Practice."
    )
    story.append(Paragraph(cert_text, body))
    story.append(Spacer(1, 0.15*inch))

    rpt_date  = ss.get("rb_report_date","")
    insp_date = ss.get("rb_inspection_date","")
    insp_type = ss.get("rb_inspection_type","Interior & Exterior")

    sig_left = Table([
        [Paragraph("APPRAISER", fl)],
        [Spacer(1, 0.35*inch)],
        [HRFlowable(width=2.8*inch, thickness=0.75, color=BLACK)],
        [Paragraph("Spencer Webb", S("sn3", fontName="Helvetica-Bold", fontSize=12, textColor=BLACK))],
        [Paragraph("A-Tech Appraisal Co., LLC", fv)],
        [Paragraph("License #CRA.0060031  |  State of Rhode Island", fv)],
        [Paragraph("Expires: 05/03/2026", fv)],
        [Paragraph(f"Date of Report: {rpt_date}", fv)],
        [Paragraph(f"Inspection: {insp_type}  |  {insp_date}", fv)],
        [Spacer(1, 0.12*inch)],
        [Paragraph("CLIENT / INTENDED USER", fl)],
        [Paragraph(ss.get("rb_intended_user",""), S("cn3", fontName="Helvetica-Bold",
                    fontSize=11, textColor=BLACK))],
    ], colWidths=[3.4*inch])
    sig_left.setStyle(TableStyle([
        ("VALIGN",(0,0),(-1,-1),"TOP"),
        ("TOPPADDING",(0,0),(-1,-1),1),("BOTTOMPADDING",(0,0),(-1,-1),1),
    ]))

    lic_file = ss.get("rb_license_file")
    lic_img  = img_cell(lic_file, 3.3*inch, 2.3*inch, "[ APPRAISER LICENSE ]")
    lic_note = Paragraph(
        "Rhode Island Department of Business Regulation\nDivision of Commercial Licensing",
        S("ln2", fontName="Helvetica", fontSize=7.5, textColor=MID_GRAY,
          alignment=TA_CENTER, leading=11, spaceBefore=5))

    sig_right = Table([
        [Paragraph("STATE LICENSE", S("ll2", fontName="Helvetica-Bold", fontSize=8,
                    textColor=MID_GRAY, alignment=TA_CENTER, spaceAfter=6))],
        [lic_img],
        [lic_note],
    ], colWidths=[3.5*inch])
    sig_right.setStyle(TableStyle([
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("TOPPADDING",(0,0),(-1,-1),2),("BOTTOMPADDING",(0,0),(-1,-1),2),
    ]))

    story.append(Table([[sig_left, sig_right]], colWidths=[3.6*inch, 3.6*inch]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MID_GRAY)
        canvas.drawString(0.65*inch, 0.38*inch,
            f"A-Tech Appraisal Co., LLC  |  CRA.0060031  |  {addr1}, {addr2}  |  Confidential Appraisal Report")
        canvas.drawRightString(W-0.65*inch, 0.38*inch, f"Page {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    buf.seek(0)
    return buf.read()


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_rev, tab_com, tab_hood, tab_zone, tab_uad, tab_report = st.tabs([
    "📋 Revision Responses",
    "📝 Appraisal Comments",
    "🏘️ Neighborhood Descriptions",
    "📐 Zoning Districts",
    "🆕 UAD 3.6 Reference",
    "🏠 Report Builder"
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
with tab_report:
    st.markdown("## 🏠 GP Residential Report Builder")
    st.caption("Build a clean client-facing appraisal report section by section. Pull saved language from your library or type fresh. Generate PDF when complete.")
    st.divider()

    # ── Session state init ─────────────────────────────────────────────────
    def rb_init(key, default):
        if f"rb_{key}" not in st.session_state:
            st.session_state[f"rb_{key}"] = default

    rb_init("address1", "")
    rb_init("address2", "")
    rb_init("effective_date", date.today().isoformat())
    rb_init("opinion_value", "")
    rb_init("intended_use", "Market Value as of the Effective Date")
    rb_init("intended_user", "")
    rb_init("property_type", "Single Family")
    rb_init("property_rights", "Fee Simple")
    rb_init("tax_year", str(date.today().year))
    rb_init("tax_amount", "")
    rb_init("style_attach", "Detached")
    rb_init("style_floors", "1")
    rb_init("style_type", "Ranch")
    rb_init("year_built", "")
    rb_init("gla", "")
    rb_init("total_rooms", "")
    rb_init("bedrooms", "")
    rb_init("bathrooms_full", "")
    rb_init("bathrooms_half", "")
    rb_init("basement_type", "Full")
    rb_init("basement_sf", "")
    rb_init("basement_fin_sf", "")
    rb_init("basement_fin_rooms", "")
    rb_init("amenities", [])
    rb_init("lot_size", "")
    rb_init("parking", "1 Car Garage")
    rb_init("zoning", "")
    rb_init("zoning_req", "")
    rb_init("zoning_comments", "Legal")
    rb_init("condition_narrative", "")
    rb_init("condition_rating", "Average-Above")
    rb_init("quality_rating", "Average")
    rb_init("neighborhood_desc", "")
    rb_init("market_desc", "")
    rb_init("market_conditions", "Stable")
    rb_init("supply_demand", "Shortage")
    rb_init("marketing_time", "Under 3 Months")
    rb_init("growth_rate", "Stable")
    rb_init("price_low", "")
    rb_init("price_high", "")
    rb_init("price_pred", "")
    rb_init("age_low", "")
    rb_init("age_high", "")
    rb_init("age_pred", "")
    rb_init("reconciliation", "")
    rb_init("scope_of_work", "The appraiser performed an interior and exterior inspection of the subject property at the client's request. A thorough investigation of available data was completed including public records, multiple listing services, brokers, owners, the inspection of the subject property itself, and other qualified sources where applicable. When conflicting information was collected, the source deemed most reliable by industry standards was utilized. All dimensions taken from assessor's field card of subject.")
    rb_init("limiting_conditions", "Not a Home Inspection: This appraisal is not a home inspection. The appraiser performed a visual inspection of accessible areas only and cannot be relied upon to disclose conditions or defects. A professional home inspection is recommended.\n\nAdverse Environmental Conditions: No apparent adverse environmental conditions were observed on the date of inspection. The presence of hazardous substances such as radon or lead paint cannot be determined during an appraisal inspection.\n\nAge Adjustments: Comparables were not adjusted for actual age differences. In this market, buyers base purchase decisions on condition rather than actual age. Condition ratings reflect effective age.\n\nMechanical Systems: Heating, plumbing, and electrical systems appear in proper working order based on visual observation only.")
    rb_init("inspection_type", "Interior & Exterior")
    rb_init("inspection_date", date.today().isoformat())
    rb_init("report_date", date.today().isoformat())

    # ── Section navigation ─────────────────────────────────────────────────
    sections = [
        "1 · Cover & Assignment",
        "2 · Improvements",
        "3 · Property Description & Rating",
        "4 · Neighborhood & Market",
        "5 · Comparable Sales",
        "6 · Maps",
        "7 · Reconciliation & Value",
        "8 · Sketch",
        "9 · Scope of Work",
        "10 · Limiting Conditions",
        "11 · Certification & Signature",
    ]
    active = st.selectbox("Jump to section", sections, key="rb_section")
    st.divider()

    # Helper: library pull button
    def lib_pull(label, lib_items, target_key):
        """Show saved library items as clickable insert buttons."""
        if lib_items:
            with st.expander(f"📚 Insert from library — {label}"):
                for item in lib_items:
                    cat = item.get("category","") or item.get("city","") or ""
                    txt = item.get("text","") or item.get("description","") or ""
                    if st.button(f"↩ {cat[:60]}", key=f"lib_{target_key}_{item.get('id',cat[:10])}"):
                        st.session_state[f"rb_{target_key}"] = txt
                        st.rerun()

    # ── SECTION 1: COVER & ASSIGNMENT ─────────────────────────────────────
    if active.startswith("1"):
        st.markdown("### Cover & Assignment Summary")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Subject Property**")
            st.session_state.rb_address1 = st.text_input(
                "Street Address", st.session_state.rb_address1)
            st.session_state.rb_address2 = st.text_input(
                "City, State  ZIP", st.session_state.rb_address2)
            st.session_state.rb_effective_date = st.date_input(
                "Effective Date",
                value=date.fromisoformat(st.session_state.rb_effective_date)
            ).isoformat()
            st.session_state.rb_opinion_value = st.text_input(
                "Opinion of Value ($)", st.session_state.rb_opinion_value,
                placeholder="e.g. 685,000")

        with col2:
            st.markdown("**Assignment Details**")
            st.session_state.rb_intended_use = st.text_input(
                "Intended Use", st.session_state.rb_intended_use)
            st.session_state.rb_intended_user = st.text_input(
                "Intended User", st.session_state.rb_intended_user)
            st.session_state.rb_property_type = st.selectbox(
                "Property Type",
                ["Single Family", "Condominium", "2-4 Unit", "Vacant Land"],
                index=["Single Family","Condominium","2-4 Unit","Vacant Land"].index(
                    st.session_state.rb_property_type))
            st.session_state.rb_property_rights = st.selectbox(
                "Property Rights",
                ["Fee Simple", "Leasehold", "Leased Fee"],
                index=["Fee Simple","Leasehold","Leased Fee"].index(
                    st.session_state.rb_property_rights))
            col_ty, col_ta = st.columns(2)
            with col_ty:
                st.session_state.rb_tax_year = st.text_input(
                    "Tax Year", st.session_state.rb_tax_year)
            with col_ta:
                st.session_state.rb_tax_amount = st.text_input(
                    "Tax Amount ($)", st.session_state.rb_tax_amount,
                    placeholder="e.g. 3,789")

        st.divider()
        st.markdown("**Subject Photos**")
        st.caption("Upload front, rear, and street scene. Additional interior photos added in Section 2.")
        cp1, cp2, cp3 = st.columns(3)
        with cp1:
            st.session_state["rb_photo_front"] = st.file_uploader(
                "Front Exterior", type=["jpg","jpeg","png"], key="up_front")
            if st.session_state.get("rb_photo_front"):
                st.image(st.session_state["rb_photo_front"], use_container_width=True)
        with cp2:
            st.session_state["rb_photo_rear"] = st.file_uploader(
                "Rear Exterior", type=["jpg","jpeg","png"], key="up_rear")
            if st.session_state.get("rb_photo_rear"):
                st.image(st.session_state["rb_photo_rear"], use_container_width=True)
        with cp3:
            st.session_state["rb_photo_street"] = st.file_uploader(
                "Street Scene", type=["jpg","jpeg","png"], key="up_street")
            if st.session_state.get("rb_photo_street"):
                st.image(st.session_state["rb_photo_street"], use_container_width=True)

    # ── SECTION 2: IMPROVEMENTS ───────────────────────────────────────────
    elif active.startswith("2"):
        st.markdown("### Improvements Description")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.session_state.rb_style_attach = st.selectbox(
                "Attached/Detached", ["Detached", "Attached"],
                index=["Detached","Attached"].index(st.session_state.rb_style_attach))
            st.session_state.rb_style_floors = st.selectbox(
                "Number of Floors", ["1", "1.5", "2", "2.5", "3", "Split Level"],
                index=["1","1.5","2","2.5","3","Split Level"].index(
                    st.session_state.rb_style_floors))
            st.session_state.rb_style_type = st.selectbox(
                "House Style",
                ["Ranch","Cape Cod","Colonial","Raised Ranch","Split Level",
                 "Contemporary","Victorian","Bungalow","Craftsman","Tudor",
                 "Gambrel","Other"],
                index=["Ranch","Cape Cod","Colonial","Raised Ranch","Split Level",
                 "Contemporary","Victorian","Bungalow","Craftsman","Tudor",
                 "Gambrel","Other"].index(st.session_state.rb_style_type)
                 if st.session_state.rb_style_type in
                 ["Ranch","Cape Cod","Colonial","Raised Ranch","Split Level",
                  "Contemporary","Victorian","Bungalow","Craftsman","Tudor",
                  "Gambrel","Other"] else 0)
        with col2:
            st.session_state.rb_year_built = st.text_input(
                "Year Built", st.session_state.rb_year_built)
            st.session_state.rb_gla = st.text_input(
                "Gross Living Area (sq ft)", st.session_state.rb_gla)
            st.session_state.rb_total_rooms = st.text_input(
                "Total Rooms", st.session_state.rb_total_rooms)
        with col3:
            st.session_state.rb_bedrooms = st.text_input(
                "Bedrooms", st.session_state.rb_bedrooms)
            st.session_state.rb_bathrooms_full = st.text_input(
                "Full Baths", st.session_state.rb_bathrooms_full)
            st.session_state.rb_bathrooms_half = st.text_input(
                "Half Baths", st.session_state.rb_bathrooms_half)

        st.divider()
        st.markdown("**Basement**")
        bc1, bc2, bc3, bc4 = st.columns(4)
        with bc1:
            st.session_state.rb_basement_type = st.selectbox(
                "Basement Type",
                ["Full", "Partial", "Crawl Space", "Slab", "None"],
                index=["Full","Partial","Crawl Space","Slab","None"].index(
                    st.session_state.rb_basement_type))
        with bc2:
            st.session_state.rb_basement_sf = st.text_input(
                "Basement SF", st.session_state.rb_basement_sf)
        with bc3:
            st.session_state.rb_basement_fin_sf = st.text_input(
                "Finished SF", st.session_state.rb_basement_fin_sf)
        with bc4:
            st.session_state.rb_basement_fin_rooms = st.text_input(
                "Finished Rooms", st.session_state.rb_basement_fin_rooms)

        st.divider()
        st.markdown("**Amenities**")
        amenity_options = [
            "Fireplace","Woodstove","Deck","Patio","Open Porch",
            "Enclosed Porch","Screen Porch","In-Ground Pool",
            "Above-Ground Pool","Solar","ADU","Outbuilding"
        ]
        st.session_state.rb_amenities = st.multiselect(
            "Select all that apply",
            amenity_options,
            default=st.session_state.rb_amenities)

        st.divider()
        st.markdown("**Site & Parking**")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.session_state.rb_lot_size = st.text_input(
                "Lot Size", st.session_state.rb_lot_size,
                placeholder="e.g. 9,100 sf or 0.45 acres")
            st.session_state.rb_parking = st.selectbox(
                "Parking",
                ["Street","Off Street","1 Car Garage","2 Car Garage",
                 "3 Car Garage","Carport","1 Car Attached","2 Car Attached",
                 "1 Car Detached","2 Car Detached"],
                index=["Street","Off Street","1 Car Garage","2 Car Garage",
                 "3 Car Garage","Carport","1 Car Attached","2 Car Attached",
                 "1 Car Detached","2 Car Detached"].index(st.session_state.rb_parking)
                 if st.session_state.rb_parking in
                 ["Street","Off Street","1 Car Garage","2 Car Garage",
                  "3 Car Garage","Carport","1 Car Attached","2 Car Attached",
                  "1 Car Detached","2 Car Detached"] else 0)
        with sc2:
            st.session_state.rb_zoning = st.text_input(
                "Zoning Classification", st.session_state.rb_zoning,
                placeholder="e.g. R-20")
            st.session_state.rb_zoning_req = st.text_input(
                "Zoning Requirements", st.session_state.rb_zoning_req,
                placeholder="e.g. 100' Frontage / 20,000 sf min")
            st.session_state.rb_zoning_comments = st.selectbox(
                "Zoning Compliance",
                ["Legal","Legal Non-Conforming","Illegal","No Zoning"],
                index=["Legal","Legal Non-Conforming","Illegal","No Zoning"].index(
                    st.session_state.rb_zoning_comments)
                    if st.session_state.rb_zoning_comments in
                    ["Legal","Legal Non-Conforming","Illegal","No Zoning"] else 0)

        # ── Dynamic photo uploads based on room count ──────────────────────
        st.divider()
        st.markdown("**Interior Room Photos**")

        try:
            n_rooms = int(st.session_state.rb_total_rooms or 0)
            n_bsmt  = int(st.session_state.rb_basement_fin_rooms or 0)
        except ValueError:
            n_rooms = 0
            n_bsmt  = 0

        if n_rooms > 0:
            st.caption(f"{n_rooms} above-grade rooms detected — upload a photo for each.")
            room_labels = ["Kitchen","Living Room","Dining Room","Primary Bedroom",
                           "Bedroom 2","Bedroom 3","Bedroom 4","Den","Office",
                           "Sunroom","Family Room","Other Room"]
            cols_per_row = 3
            room_photos = []
            for i in range(n_rooms):
                if i % cols_per_row == 0:
                    photo_cols = st.columns(cols_per_row)
                label = room_labels[i] if i < len(room_labels) else f"Room {i+1}"
                with photo_cols[i % cols_per_row]:
                    default_label = st.text_input(
                        f"Room {i+1} Label", label,
                        key=f"rb_room_label_{i}")
                    uploaded = st.file_uploader(
                        f"Photo — {default_label}",
                        type=["jpg","jpeg","png"],
                        key=f"rb_room_photo_{i}")
                    if uploaded:
                        st.image(uploaded, use_container_width=True)
                    room_photos.append({"label": default_label, "file": uploaded})
            st.session_state["rb_room_photos"] = room_photos

        if n_bsmt > 0:
            st.markdown(f"**Basement Room Photos** ({n_bsmt} finished rooms)")
            bsmt_photos = []
            for i in range(n_bsmt):
                if i % 3 == 0:
                    b_cols = st.columns(3)
                with b_cols[i % 3]:
                    bl = st.text_input(f"Basement Room {i+1} Label",
                                        f"Basement Room {i+1}",
                                        key=f"rb_bsmt_label_{i}")
                    bu = st.file_uploader(f"Photo — {bl}",
                                           type=["jpg","jpeg","png"],
                                           key=f"rb_bsmt_photo_{i}")
                    if bu:
                        st.image(bu, use_container_width=True)
                    bsmt_photos.append({"label": bl, "file": bu})
            st.session_state["rb_bsmt_photos"] = bsmt_photos

        if n_rooms == 0:
            st.info("Enter Total Rooms above to activate dynamic photo uploads.")

    # ── SECTION 3: CONDITION & RATING ─────────────────────────────────────
    elif active.startswith("3"):
        st.markdown("### Property Description & Rating")

        neighborhoods = load_data("neighborhoods_data", "rc_neighborhoods.json", [])
        comments = load_data("comments_data", "rc_comments.json", DEFAULT_COMMENTS)
        cond_comments = [c for c in comments if any(x in c["category"]
                         for x in ["C1","C2","C3","C4","C5","C6","Condition"])]
        lib_pull("Condition Comments", cond_comments, "condition_narrative")

        st.session_state.rb_condition_narrative = st.text_area(
            "Condition & Updates Narrative",
            st.session_state.rb_condition_narrative,
            height=160,
            placeholder="Describe the condition, recent updates, and any items noted at inspection...")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.rb_condition_rating = st.selectbox(
                "Overall Condition Rating",
                ["C1 — New","C2 — Remodeled","C3 — Updated",
                 "C4 — Average","C5 — Fair","C6 — Poor",
                 "Average","Average-Above","Above Average","Below Average","Good"],
                index=["C1 — New","C2 — Remodeled","C3 — Updated",
                 "C4 — Average","C5 — Fair","C6 — Poor",
                 "Average","Average-Above","Above Average","Below Average","Good"].index(
                    st.session_state.rb_condition_rating)
                    if st.session_state.rb_condition_rating in
                    ["C1 — New","C2 — Remodeled","C3 — Updated",
                     "C4 — Average","C5 — Fair","C6 — Poor",
                     "Average","Average-Above","Above Average","Below Average","Good"] else 0)
        with col2:
            st.session_state.rb_quality_rating = st.selectbox(
                "Overall Quality Rating",
                ["Q1 — Exceptional","Q2 — High Quality","Q3 — Good",
                 "Q4 — Average","Q5 — Fair","Q6 — Poor",
                 "Average","Average-Above","Above Average","Below Average","Good"],
                index=["Q1 — Exceptional","Q2 — High Quality","Q3 — Good",
                 "Q4 — Average","Q5 — Fair","Q6 — Poor",
                 "Average","Average-Above","Above Average","Below Average","Good"].index(
                    st.session_state.rb_quality_rating)
                    if st.session_state.rb_quality_rating in
                    ["Q1 — Exceptional","Q2 — High Quality","Q3 — Good",
                     "Q4 — Average","Q5 — Fair","Q6 — Poor",
                     "Average","Average-Above","Above Average","Below Average","Good"] else 0)

    # ── SECTION 4: NEIGHBORHOOD & MARKET ──────────────────────────────────
    elif active.startswith("4"):
        st.markdown("### Neighborhood & Market Description")

        neighborhoods = load_data("neighborhoods_data", "rc_neighborhoods.json", [])
        lib_pull("Neighborhood Descriptions", neighborhoods, "neighborhood_desc")
        st.session_state.rb_neighborhood_desc = st.text_area(
            "Neighborhood Description",
            st.session_state.rb_neighborhood_desc,
            height=120)

        comments = load_data("comments_data", "rc_comments.json", DEFAULT_COMMENTS)
        mkt_comments = [c for c in comments if "market" in c["category"].lower()
                        or "supply" in c["category"].lower()
                        or "marketing" in c["category"].lower()]
        lib_pull("Market Condition Comments", mkt_comments, "market_desc")
        st.session_state.rb_market_desc = st.text_area(
            "Market Description / Supply & Demand Commentary",
            st.session_state.rb_market_desc,
            height=100,
            placeholder="Describe market conditions, supply/demand, and marketing time support...")

        st.divider()
        st.markdown("**Market Condition Checkboxes**")
        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1:
            st.session_state.rb_market_conditions = st.selectbox(
                "Market Conditions", ["Increasing","Stable","Declining"],
                index=["Increasing","Stable","Declining"].index(
                    st.session_state.rb_market_conditions)
                    if st.session_state.rb_market_conditions in
                    ["Increasing","Stable","Declining"] else 1)
        with mc2:
            st.session_state.rb_supply_demand = st.selectbox(
                "Supply / Demand",
                ["Shortage","In Balance","Over Supply"],
                index=["Shortage","In Balance","Over Supply"].index(
                    st.session_state.rb_supply_demand)
                    if st.session_state.rb_supply_demand in
                    ["Shortage","In Balance","Over Supply"] else 0)
        with mc3:
            st.session_state.rb_marketing_time = st.selectbox(
                "Marketing Time",
                ["Under 3 Months","3-6 Months","Over 6 Months"],
                index=["Under 3 Months","3-6 Months","Over 6 Months"].index(
                    st.session_state.rb_marketing_time)
                    if st.session_state.rb_marketing_time in
                    ["Under 3 Months","3-6 Months","Over 6 Months"] else 0)
        with mc4:
            st.session_state.rb_growth_rate = st.selectbox(
                "Growth Rate", ["Rapid","Stable","Slow"],
                index=["Rapid","Stable","Slow"].index(
                    st.session_state.rb_growth_rate)
                    if st.session_state.rb_growth_rate in
                    ["Rapid","Stable","Slow"] else 1)

        st.divider()
        st.markdown("**Housing Unit Trends — Manual Entry or CSV Upload**")
        housing_csv = st.file_uploader(
            "Upload Housing Trends CSV (from MLS/Spark)",
            type=["csv"], key="rb_housing_csv")

        if housing_csv:
            try:
                df = pd.read_csv(housing_csv)
                st.dataframe(df.head(10))
                st.caption("CSV loaded — map fields below")
                cols = ["(select)"] + list(df.columns)
                hc1, hc2, hc3 = st.columns(3)
                with hc1:
                    price_col = st.selectbox("Sale Price column", cols, key="rb_hcspc")
                with hc2:
                    age_col = st.selectbox("Year Built column", cols, key="rb_hcagc")
                with hc3:
                    if st.button("Extract Trends"):
                        if price_col != "(select)":
                            prices = pd.to_numeric(df[price_col].str.replace(
                                r'[$,]','',regex=True), errors='coerce').dropna()
                            st.session_state.rb_price_low = f"${prices.min():,.0f}"
                            st.session_state.rb_price_high = f"${prices.max():,.0f}"
                            st.session_state.rb_price_pred = f"${prices.median():,.0f}"
                        if age_col != "(select)":
                            ages = pd.to_numeric(df[age_col], errors='coerce').dropna()
                            yr = date.today().year
                            st.session_state.rb_age_low = str(int(yr - ages.max()))
                            st.session_state.rb_age_high = str(int(yr - ages.min()))
                            st.session_state.rb_age_pred = str(int(yr - ages.median()))
                        st.rerun()
            except Exception as e:
                st.error(f"CSV error: {e}")

        st.markdown("**One-Unit Housing Price & Age Range**")
        hpc1, hpc2, hpc3 = st.columns(3)
        with hpc1:
            st.session_state.rb_price_low = st.text_input(
                "Price Low", st.session_state.rb_price_low, placeholder="$115,000")
        with hpc2:
            st.session_state.rb_price_high = st.text_input(
                "Price High", st.session_state.rb_price_high, placeholder="$1,787,000")
        with hpc3:
            st.session_state.rb_price_pred = st.text_input(
                "Price Predominant", st.session_state.rb_price_pred, placeholder="$780,000")

        hac1, hac2, hac3 = st.columns(3)
        with hac1:
            st.session_state.rb_age_low = st.text_input(
                "Age Low (yrs)", st.session_state.rb_age_low, placeholder="5")
        with hac2:
            st.session_state.rb_age_high = st.text_input(
                "Age High (yrs)", st.session_state.rb_age_high, placeholder="115")
        with hac3:
            st.session_state.rb_age_pred = st.text_input(
                "Age Predominant (yrs)", st.session_state.rb_age_pred, placeholder="55")

    # ── SECTION 5: COMPARABLE SALES ───────────────────────────────────────
    elif active.startswith("5"):
        st.markdown("### Comparable Sales Data")
        st.info("Upload your MLS comp CSV exported from Spark/MLS — same file you already pull. Fields will auto-populate.")

        comp_csv = st.file_uploader(
            "Upload Comp CSV", type=["csv"], key="rb_comp_csv")

        if comp_csv:
            try:
                df = pd.read_csv(comp_csv)
                st.success(f"Loaded {len(df)} rows, {len(df.columns)} columns")
                st.dataframe(df, use_container_width=True)
                st.session_state["rb_comp_df"] = df.to_json()
            except Exception as e:
                st.error(f"CSV error: {e}")
        elif st.session_state.get("rb_comp_df"):
            df = pd.read_json(st.session_state["rb_comp_df"])
            st.dataframe(df, use_container_width=True)
            st.caption("Previously loaded comp data shown above.")

        st.divider()
        st.markdown("**Comp Photo Uploads** (up to 5 comps)")
        for i in range(5):
            with st.expander(f"Comparable #{i+1} Photo"):
                addr_key = f"rb_comp_addr_{i}"
                photo_key = f"rb_comp_photo_{i}"
                if addr_key not in st.session_state:
                    st.session_state[addr_key] = ""
                st.session_state[addr_key] = st.text_input(
                    f"Comp #{i+1} Address", st.session_state[addr_key],
                    key=f"comp_addr_input_{i}")
                uploaded = st.file_uploader(
                    f"Comp #{i+1} Exterior Photo",
                    type=["jpg","jpeg","png"], key=f"comp_photo_up_{i}")
                if uploaded:
                    st.image(uploaded, use_container_width=True)
                    st.session_state[photo_key] = uploaded

    # ── SECTION 6: MAPS ───────────────────────────────────────────────────
    elif active.startswith("6"):
        st.markdown("### Maps")

        mc1, mc2 = st.columns(2)
        with mc1:
            st.markdown("**Plat Map**")
            plat = st.file_uploader("Upload Plat Map image",
                                     type=["jpg","jpeg","png"], key="rb_plat_map")
            if plat:
                st.image(plat, use_container_width=True)
                st.session_state["rb_plat_map_file"] = plat
        with mc2:
            st.markdown("**Comparable Sales Map**")
            comp_map = st.file_uploader("Upload Comp Map image",
                                         type=["jpg","jpeg","png"], key="rb_comp_map")
            if comp_map:
                st.image(comp_map, use_container_width=True)
                st.session_state["rb_comp_map_file"] = comp_map

    # ── SECTION 7: RECONCILIATION & VALUE ─────────────────────────────────
    elif active.startswith("7"):
        st.markdown("### Final Value Conclusion & Reconciliation")

        comments = load_data("comments_data", "rc_comments.json", DEFAULT_COMMENTS)
        recon_comments = [c for c in comments if "reconcil" in c["category"].lower()
                          or "approach" in c["category"].lower()
                          or "income" in c["category"].lower()]
        lib_pull("Reconciliation Comments", recon_comments, "reconciliation")

        st.session_state.rb_reconciliation = st.text_area(
            "Reconciliation Commentary",
            st.session_state.rb_reconciliation,
            height=180,
            placeholder="The Sales Comparison Approach was given full weight as it best reflects the actions and intentions of willing buyers and sellers...")

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.rb_opinion_value = st.text_input(
                "Final Opinion of Value ($)",
                st.session_state.rb_opinion_value,
                placeholder="685,000")
        with col2:
            st.session_state.rb_effective_date = st.date_input(
                "As of (Effective Date)",
                value=date.fromisoformat(st.session_state.rb_effective_date)
            ).isoformat()

    # ── SECTION 8: SKETCH ─────────────────────────────────────────────────
    elif active.startswith("8"):
        st.markdown("### Floor Plan / Sketch")
        st.caption("Upload CubiCasa sketch export or TOTAL sketch PDF export as image.")

        sk1, sk2 = st.columns(2)
        with sk1:
            st.markdown("**Above Grade Floor Plan**")
            sketch_ag = st.file_uploader("Above Grade Sketch",
                                          type=["jpg","jpeg","png","pdf"],
                                          key="rb_sketch_ag")
            if sketch_ag and sketch_ag.type != "application/pdf":
                st.image(sketch_ag, use_container_width=True)
                st.session_state["rb_sketch_ag_file"] = sketch_ag
        with sk2:
            st.markdown("**Below Grade / Basement Floor Plan**")
            sketch_bg = st.file_uploader("Basement Sketch",
                                          type=["jpg","jpeg","png","pdf"],
                                          key="rb_sketch_bg")
            if sketch_bg and sketch_bg.type != "application/pdf":
                st.image(sketch_bg, use_container_width=True)
                st.session_state["rb_sketch_bg_file"] = sketch_bg

    # ── SECTION 9: SCOPE OF WORK ──────────────────────────────────────────
    elif active.startswith("9"):
        st.markdown("### Scope of Work")

        comments = load_data("comments_data", "rc_comments.json", DEFAULT_COMMENTS)
        sow_comments = [c for c in comments if "scope" in c["category"].lower()]
        lib_pull("Scope of Work Language", sow_comments, "scope_of_work")

        st.session_state.rb_scope_of_work = st.text_area(
            "Scope of Work",
            st.session_state.rb_scope_of_work,
            height=220)

    # ── SECTION 10: LIMITING CONDITIONS ───────────────────────────────────
    elif active.startswith("10"):
        st.markdown("### Limiting Conditions")

        comments = load_data("comments_data", "rc_comments.json", DEFAULT_COMMENTS)
        lc_comments = [c for c in comments if "condition" in c["category"].lower()
                        or "inspection" in c["category"].lower()
                        or "environmental" in c["category"].lower()]
        lib_pull("Limiting Condition Language", lc_comments, "limiting_conditions")

        st.session_state.rb_limiting_conditions = st.text_area(
            "Limiting Conditions",
            st.session_state.rb_limiting_conditions,
            height=300)

    # ── SECTION 11: CERTIFICATION ─────────────────────────────────────────
    elif active.startswith("11"):
        st.markdown("### Appraiser Certification & Signature")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Inspection Details**")
            st.session_state.rb_inspection_type = st.selectbox(
                "Inspection Type",
                ["Interior & Exterior","Exterior Only","Desktop (No Inspection)",
                 "Drive-By","Hybrid"],
                index=["Interior & Exterior","Exterior Only",
                       "Desktop (No Inspection)","Drive-By","Hybrid"].index(
                    st.session_state.rb_inspection_type)
                    if st.session_state.rb_inspection_type in
                    ["Interior & Exterior","Exterior Only",
                     "Desktop (No Inspection)","Drive-By","Hybrid"] else 0)
            st.session_state.rb_inspection_date = st.date_input(
                "Date of Inspection",
                value=date.fromisoformat(st.session_state.rb_inspection_date)
            ).isoformat()
            st.session_state.rb_report_date = st.date_input(
                "Date of Report",
                value=date.fromisoformat(st.session_state.rb_report_date)
            ).isoformat()

        with col2:
            st.markdown("**License / Certification Image**")
            lic_upload = st.file_uploader(
                "Upload License Certificate Image",
                type=["jpg","jpeg","png"], key="rb_license_img")
            if lic_upload:
                st.image(lic_upload, use_container_width=True)
                st.session_state["rb_license_file"] = lic_upload

        st.divider()
        st.info("**Appraiser:** Spencer Webb  |  **Company:** A-Tech Appraisal Co., LLC  |  **License:** CRA.0060031 — RI  |  **Expires:** 05/03/2026")

    # ── GENERATE PDF ──────────────────────────────────────────────────────
    st.divider()
    st.markdown("### Generate Report")

    col_gen, col_reset = st.columns([3,1])
    with col_reset:
        if st.button("🗑 Reset All Fields"):
            keys_to_clear = [k for k in st.session_state if k.startswith("rb_")]
            for k in keys_to_clear:
                del st.session_state[k]
            st.rerun()

    with col_gen:
        if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
            with st.spinner("Building report..."):
                try:
                    pdf_bytes = generate_gp_res_pdf(st.session_state)
                    addr_slug = st.session_state.get("rb_address1","report").replace(" ","_").replace(",","")
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"Appraisal_{addr_slug}.pdf",
                        mime="application/pdf",
                        use_container_width=True)
                    st.success("Report generated successfully.")
                except Exception as e:
                    st.error(f"PDF generation error: {e}")
                    import traceback
                    st.code(traceback.format_exc())
