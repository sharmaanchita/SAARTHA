import streamlit as st
import pandas as pd
import streamlit.components.v1 as components

st.set_page_config( 
     page_title="SAARTHA", 
     page_icon="images/saartha-high-resolution-logo.png", 
     layout="wide", 
     initial_sidebar_state="expanded", 
 ) 
hide_default_format = """ 
        <style> 
        #MainMenu {visibility: show; } 
        footer {visibility: hidden;} 
        </style> 
        """ 
st.markdown(hide_default_format, unsafe_allow_html=True) 

def gradient_text(text, color1, color2):
    gradient_css = f"""
        background: -webkit-linear-gradient(left, {color1}, {color2});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: bold;
        font-size: 42px;
    """
    return f'<span style="{gradient_css}">{text}</span>'

col1, col2, col3 = st.columns([5, 2, 5])  # Adjust column ratios to center the image
with col2:
    st.image("images/saartha-high-resolution-logo.png", width=200)

def set_page_query_param(page_name):
    st.experimental_set_query_params(page=page_name)
set_page_query_param("home")


# Header Section
st.markdown(
    """
    <style>
    .main-header {
        font-size: 50px;
        font-weight: bold;
        text-align: center;
        color: #DA70D6;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 20px;
        text-align: center;
        color: #f8f9fa;
        margin-top: -10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">Revolutionizing OEM Supply Chains</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Optimize. Sustain. Allocate Smartly.</div>', unsafe_allow_html=True)

st.divider()

# Main Content
# Style for Feature Cards
feature_card_style = """
    <style>
    .feature-card {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        margin: 10px;
        text-align: center;
        color: #f8f9fa;
        transition: transform 0.3s;
    }
    .feature-card:hover {
        transform: scale(1.05);
        background-color: #333333;
    }
    .feature-icon {
        font-size: 50px;
        margin-bottom: 15px;
        color: #DA70D6;
    }
    .feature-title {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
        color: #DA70D6;
    }
    .feature-description {
        font-size: 16px;
        line-height: 1.5;
        color: #f8f9fa;
    }
    </style>
"""

st.markdown(feature_card_style, unsafe_allow_html=True)

# Feature Tiles
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🔄</div>
            <div class="feature-title">Optimize Supply Chain</div>
            <div class="feature-description">
                Enhance efficiency with demand balance, material reports, and resource utilization insights.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🌍</div>
            <div class="feature-title">Reduce Carbon Emissions</div>
            <div class="feature-description">
                Track and minimize your environmental impact with our tools and visualizations.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🛠️</div>
            <div class="feature-title">Intelligent Resource Allocation</div>
            <div class="feature-description">
                Optimize production, layout, and workforce allocation for better results.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    
footer="""<style>

a:hover,  a:active {
color: red;
background-color: transparent;
text-decoration: underline;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: white;
color: black;
text-align: center;
}
</style>
<div class="footer">
<p>Developed by <a style='display: inline; text-align: center;' href="https://www.linkedin.com/in/harshavardhan-bajoria/" target="_blank">Team SAARTHA</a></p>
</div>
"""
st.markdown(footer,unsafe_allow_html=True)
