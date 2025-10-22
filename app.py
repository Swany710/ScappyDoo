"""
ScappyDoo - City Permit Web Scraper GUI
A user-friendly interface for scraping city permit data.
"""
import streamlit as st
import json
import pandas as pd
from pathlib import Path
import time
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from permit_scraper import PermitScraper
from exporters import PermitExporter

# Page configuration
st.set_page_config(
    page_title="ScappyDoo - Permit Scraper",
    page_icon="🐕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 5px;
        color: #721c24;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        color: #0c5460;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 1.1rem;
        padding: 1rem 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'permits' not in st.session_state:
    st.session_state.permits = []
if 'scraping_complete' not in st.session_state:
    st.session_state.scraping_complete = False
if 'config' not in st.session_state:
    st.session_state.config = None
if 'summary' not in st.session_state:
    st.session_state.summary = None


def load_config_file(config_path):
    """Load configuration from file."""
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading config: {e}")
        return None


def get_available_configs():
    """Get list of available configuration files."""
    config_dir = Path("configs")
    if config_dir.exists():
        return list(config_dir.glob("*.json"))
    return []


def run_scraper(config, url, max_pages, scrape_details):
    """Run the scraper with given parameters."""
    scraper_settings = config.get('scraper_settings', {})

    progress_bar = st.progress(0)
    status_text = st.empty()

    try:
        with PermitScraper(config, **scraper_settings) as scraper:
            status_text.text("Starting scraper...")
            progress_bar.progress(10)

            # Scrape permits
            status_text.text(f"Scraping permits from {url}...")
            permits = scraper.scrape_permits(url, max_pages=max_pages)
            progress_bar.progress(50)

            if not permits:
                st.warning("No permits found!")
                return []

            # Scrape details if requested
            if scrape_details:
                status_text.text("Fetching detailed information...")
                detailed_permits = []
                for i, permit in enumerate(permits):
                    detailed_permit = scraper.scrape_permit_details(permit)
                    detailed_permits.append(detailed_permit)
                    progress = 50 + int((i + 1) / len(permits) * 40)
                    progress_bar.progress(progress)
                permits = detailed_permits

            progress_bar.progress(90)
            status_text.text("Generating summary...")

            # Generate summary
            summary = PermitExporter.generate_summary(permits)
            st.session_state.summary = summary

            progress_bar.progress(100)
            status_text.text("Scraping complete!")

            return permits

    except Exception as e:
        st.error(f"Error during scraping: {e}")
        return []


# Header
st.markdown('<div class="main-header">🐕 ScappyDoo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">City Permit Web Scraper</div>', unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "🔍 Scraper", "⚙️ Configuration", "📊 Results"])

# ==================== HOME TAB ====================
with tab1:
    st.header("Welcome to ScappyDoo!")

    st.markdown("""
    ### What is ScappyDoo?
    ScappyDoo is a flexible web scraper designed to extract permit information from city and municipal websites.

    ### Quick Start Guide
    1. **Go to the Scraper tab** to start scraping
    2. **Select a configuration** or create your own
    3. **Enter the URL** of the city permit website
    4. **Click "Start Scraping"** and wait for results
    5. **View and export** your data in the Results tab

    ### Features
    - 🎯 Configurable CSS selectors for any website structure
    - 🚀 Support for both static and JavaScript-heavy sites
    - 📑 Automatic pagination handling
    - 📊 Export to CSV, JSON, or Excel
    - 📈 Summary statistics and visualizations
    - ⏱️ Rate limiting to respect server resources
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Available Configs", len(get_available_configs()))
    with col2:
        st.metric("Permits Scraped", len(st.session_state.permits))
    with col3:
        if st.session_state.scraping_complete:
            st.success("✅ Ready")
        else:
            st.info("⏳ Ready to Scrape")

# ==================== SCRAPER TAB ====================
with tab2:
    st.header("🔍 Permit Scraper")

    # Configuration selection
    st.subheader("1. Select Configuration")

    col1, col2 = st.columns([2, 1])

    with col1:
        config_files = get_available_configs()
        config_names = ["Custom Configuration..."] + [f.stem for f in config_files]
        selected_config = st.selectbox(
            "Choose a configuration",
            config_names,
            help="Select a pre-built configuration or create a custom one"
        )

    with col2:
        if st.button("📁 Load Configuration", type="secondary"):
            if selected_config != "Custom Configuration...":
                config_path = Path("configs") / f"{selected_config}.json"
                config = load_config_file(config_path)
                if config:
                    st.session_state.config = config
                    st.success(f"Loaded: {selected_config}")

    # Show loaded configuration
    if st.session_state.config:
        with st.expander("📋 View Current Configuration"):
            st.json(st.session_state.config)

    st.divider()

    # Scraping parameters
    st.subheader("2. Scraping Parameters")

    col1, col2 = st.columns(2)

    with col1:
        url = st.text_input(
            "Target URL",
            placeholder="https://city.gov/permits",
            help="Enter the URL of the permit listing page"
        )

    with col2:
        max_pages = st.number_input(
            "Maximum Pages",
            min_value=1,
            max_value=100,
            value=5,
            help="Limit the number of pages to scrape"
        )

    col1, col2 = st.columns(2)

    with col1:
        scrape_details = st.checkbox(
            "Scrape Detailed Information",
            help="Fetch additional details from individual permit pages (slower)"
        )

    with col2:
        use_unlimited = st.checkbox(
            "Unlimited Pages",
            help="Scrape all available pages (may take a long time)"
        )

    if use_unlimited:
        max_pages = None

    st.divider()

    # Start scraping button
    st.subheader("3. Start Scraping")

    col1, col2, col3 = st.columns([1, 1, 2])

    with col1:
        start_button = st.button("🚀 Start Scraping", type="primary", use_container_width=True)

    with col2:
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.permits = []
            st.session_state.scraping_complete = False
            st.session_state.summary = None
            st.success("Results cleared!")
            st.rerun()

    # Run scraper
    if start_button:
        if not st.session_state.config:
            st.error("⚠️ Please select a configuration first!")
        elif not url:
            st.error("⚠️ Please enter a URL!")
        else:
            with st.spinner("Scraping in progress..."):
                permits = run_scraper(
                    st.session_state.config,
                    url,
                    max_pages,
                    scrape_details
                )

                if permits:
                    st.session_state.permits = permits
                    st.session_state.scraping_complete = True
                    st.success(f"✅ Successfully scraped {len(permits)} permits!")
                    st.balloons()
                else:
                    st.warning("No permits were found. Check your configuration and URL.")

# ==================== CONFIGURATION TAB ====================
with tab3:
    st.header("⚙️ Configuration Builder")

    st.markdown("""
    Create or modify configurations to match your target website's structure.
    Use browser developer tools to inspect the HTML and find the correct CSS selectors.
    """)

    config_tab1, config_tab2 = st.tabs(["Create New", "Edit Existing"])

    with config_tab1:
        st.subheader("Create New Configuration")

        col1, col2 = st.columns(2)

        with col1:
            new_city_name = st.text_input("City Name", placeholder="Example City")
            new_description = st.text_area("Description", placeholder="Configuration for Example City permit portal")

        with col2:
            new_use_selenium = st.checkbox("Use Selenium (for JavaScript sites)", value=False)
            new_rate_limit = st.slider("Rate Limit (seconds)", 0.5, 5.0, 1.5, 0.5)
            new_timeout = st.slider("Timeout (seconds)", 10, 60, 30, 5)

        st.subheader("CSS Selectors")

        col1, col2 = st.columns(2)

        with col1:
            permit_container = st.text_input("Permit Container", placeholder="div.permit-item")
            permit_number = st.text_input("Permit Number", placeholder="span.permit-number")
            permit_type = st.text_input("Permit Type", placeholder="span.permit-type")
            address = st.text_input("Address", placeholder="div.address")
            status = st.text_input("Status", placeholder="span.status")

        with col2:
            issue_date = st.text_input("Issue Date", placeholder="span.issue-date")
            applicant = st.text_input("Applicant", placeholder="span.applicant")
            contractor = st.text_input("Contractor", placeholder="span.contractor")
            detail_link = st.text_input("Detail Link", placeholder="a.details-link@href")
            next_page = st.text_input("Next Page", placeholder="a.next-page")

        if st.button("💾 Save Configuration", type="primary"):
            new_config = {
                "city_name": new_city_name,
                "description": new_description,
                "selectors": {
                    "permit_container": permit_container,
                    "permit_number": permit_number,
                    "permit_type": permit_type,
                    "address": address,
                    "status": status,
                    "issue_date": issue_date,
                    "applicant": applicant,
                    "contractor": contractor,
                    "detail_link": detail_link,
                    "next_page": next_page
                },
                "scraper_settings": {
                    "rate_limit": new_rate_limit,
                    "timeout": new_timeout,
                    "use_selenium": new_use_selenium,
                    "headless": True
                }
            }

            # Remove empty selectors
            new_config["selectors"] = {k: v for k, v in new_config["selectors"].items() if v}

            # Save to file
            config_name = new_city_name.lower().replace(" ", "_")
            config_path = Path("configs") / f"{config_name}.json"
            config_path.parent.mkdir(exist_ok=True)

            with open(config_path, 'w') as f:
                json.dump(new_config, f, indent=2)

            st.session_state.config = new_config
            st.success(f"✅ Configuration saved to {config_path}")

    with config_tab2:
        st.subheader("Edit Existing Configuration")

        config_files = get_available_configs()
        if config_files:
            selected = st.selectbox("Select configuration to edit", [f.stem for f in config_files])

            if st.button("📝 Load for Editing"):
                config_path = Path("configs") / f"{selected}.json"
                config = load_config_file(config_path)
                if config:
                    st.session_state.edit_config = config
                    st.success(f"Loaded {selected} for editing")

            if 'edit_config' in st.session_state:
                st.json(st.session_state.edit_config)
        else:
            st.info("No configurations available to edit. Create a new one first!")

# ==================== RESULTS TAB ====================
with tab4:
    st.header("📊 Results & Export")

    if not st.session_state.permits:
        st.info("👆 No data yet. Go to the Scraper tab to start scraping!")
    else:
        # Summary statistics
        st.subheader("📈 Summary Statistics")

        if st.session_state.summary:
            summary = st.session_state.summary

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Permits", summary.get('total_permits', 0))
            with col2:
                if 'permit_types' in summary:
                    st.metric("Permit Types", len(summary['permit_types']))
            with col3:
                if 'status_counts' in summary:
                    st.metric("Different Statuses", len(summary['status_counts']))
            with col4:
                st.metric("Fields Captured", len(summary.get('fields', [])))

            # Visualizations
            col1, col2 = st.columns(2)

            with col1:
                if 'permit_types' in summary:
                    st.subheader("Permit Types Distribution")
                    fig = px.pie(
                        values=list(summary['permit_types'].values()),
                        names=list(summary['permit_types'].keys()),
                        title="Permits by Type"
                    )
                    st.plotly_chart(fig, use_container_width=True)

            with col2:
                if 'status_counts' in summary:
                    st.subheader("Status Distribution")
                    fig = px.bar(
                        x=list(summary['status_counts'].keys()),
                        y=list(summary['status_counts'].values()),
                        title="Permits by Status",
                        labels={'x': 'Status', 'y': 'Count'}
                    )
                    st.plotly_chart(fig, use_container_width=True)

            # Missing data analysis
            if 'missing_data' in summary and summary['missing_data']:
                with st.expander("🔍 Missing Data Analysis"):
                    missing_df = pd.DataFrame([
                        {'Field': k, 'Missing Count': v['count'], 'Missing %': v['percentage']}
                        for k, v in summary['missing_data'].items()
                    ])
                    st.dataframe(missing_df, use_container_width=True)

        st.divider()

        # Data preview
        st.subheader("📋 Data Preview")

        df = pd.DataFrame(st.session_state.permits)

        # Add filters
        col1, col2 = st.columns(2)

        with col1:
            if 'permit_type' in df.columns:
                permit_types = ['All'] + list(df['permit_type'].unique())
                selected_type = st.selectbox("Filter by Permit Type", permit_types)
                if selected_type != 'All':
                    df = df[df['permit_type'] == selected_type]

        with col2:
            if 'status' in df.columns:
                statuses = ['All'] + list(df['status'].unique())
                selected_status = st.selectbox("Filter by Status", statuses)
                if selected_status != 'All':
                    df = df[df['status'] == selected_status]

        st.dataframe(df, use_container_width=True, height=400)

        st.divider()

        # Export section
        st.subheader("💾 Export Data")

        col1, col2, col3, col4 = st.columns(4)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        with col1:
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📄 Download CSV",
                data=csv_data,
                file_name=f"permits_{timestamp}.csv",
                mime="text/csv",
                use_container_width=True
            )

        with col2:
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📋 Download JSON",
                data=json_data,
                file_name=f"permits_{timestamp}.json",
                mime="application/json",
                use_container_width=True
            )

        with col3:
            # Excel export
            if st.button("📊 Export to Excel", use_container_width=True):
                excel_path = f"output/permits_{timestamp}.xlsx"
                Path("output").mkdir(exist_ok=True)
                PermitExporter.to_excel(st.session_state.permits, excel_path)
                st.success(f"✅ Exported to {excel_path}")

        with col4:
            # Summary export
            if st.session_state.summary:
                summary_json = json.dumps(st.session_state.summary, indent=2)
                st.download_button(
                    label="📊 Download Summary",
                    data=summary_json,
                    file_name=f"summary_{timestamp}.json",
                    mime="application/json",
                    use_container_width=True
                )

# Sidebar
with st.sidebar:
    st.image("https://raw.githubusercontent.com/streamlit/streamlit/develop/docs/_static/img/logo.png", width=100)
    st.title("About ScappyDoo")

    st.markdown("""
    **Version:** 2.0
    **Mode:** GUI Application

    ### Quick Stats
    """)

    st.metric("Permits in Memory", len(st.session_state.permits))
    st.metric("Configurations Available", len(get_available_configs()))

    st.markdown("---")

    st.markdown("""
    ### Tips
    - Use browser DevTools to find CSS selectors
    - Test with `max_pages=1` first
    - Enable Selenium for JavaScript-heavy sites
    - Respect rate limits (1.5s+ recommended)

    ### Need Help?
    Check the Home tab for a quick start guide!
    """)

    if st.button("🔄 Refresh App"):
        st.rerun()
