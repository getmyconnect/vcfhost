import streamlit as st
import hmac
import os
from PIL import Image

# --- DIRECTORY SETUP ---
VCF_DIR = "vcf"
PAGE_DIR = "p"
ASSETS_DIR = "assets"

for d in [VCF_DIR, PAGE_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

# --- LOGIN SECURITY ---
def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["passwords"]["admin_password"]) and \
           hmac.compare_digest(st.session_state["username"], st.secrets["passwords"]["admin_user"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"] 
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.title("🔐 NFC Business Manager")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.error("😕 Access Denied")
        return False
    return True

# --- APP START ---
if check_password():
    st.sidebar.title("Settings")
    if st.sidebar.button("Log Out"):
        st.session_state.clear()
        st.rerun()

    st.title("📇 NFC Contact & Profile Creator")
    st.info("Fill the form below to generate a professional VCF and a landing page.")

    with st.form("contact_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            first = st.text_input("First Name", placeholder="Arjun")
            last = st.text_input("Last Name", placeholder="Sharma")
            phone = st.text_input("Phone", placeholder="+919876543210")
        with col2:
            email = st.text_input("Email", placeholder="arjun@example.com")
            company = st.text_input("Company", value="BeyondWalls")
            role = st.text_input("Job Role", placeholder="Account Executive")
        
        uploaded_photo = st.file_uploader("Upload Profile Photo", type=['jpg', 'jpeg', 'png'])
        
        submit = st.form_submit_button("Generate Brand Assets")

    if submit:
        if first and last and phone and uploaded_photo:
            # Create a clean slug for filenames
            slug = f"{first.lower()}_{last.lower()}".replace(" ", "_")
            
            # 1. Save the Image
            img_ext = uploaded_photo.name.split('.')[-1]
            img_filename = f"{slug}.{img_ext}"
            img_path = os.path.join(ASSETS_DIR, img_filename)
            with open(img_path, "wb") as f:
                f.write(uploaded_photo.getbuffer())

            # 2. Create VCF File
            vcf_path = os.path.join(VCF_DIR, f"{slug}.vcf")
            vcard = f"BEGIN:VCARD\nVERSION:3.0\nN:{last};{first};;;\nFN:{first} {last}\nORG:{company}\nTITLE:{role}\nTEL;TYPE=CELL:{phone}\nEMAIL;TYPE=INTERNET:{email}\nEND:VCARD"
            with open(vcf_path, "w") as f:
                f.write(vcard)

            # 3. Create HTML Profile Page
            html_path = os.path.join(PAGE_DIR, f"{slug}.html")
            # Points to the saved image relative to the HTML file's location
            relative_img = f"../{ASSETS_DIR}/{img_filename}"
            
            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{first} {last}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }}
        .card {{ background: white; width: 85%; max-width: 320px; padding: 35px 20px; border-radius: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center; }}
        img {{ width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 4px solid #007AFF; margin-bottom: 15px; }}
        h2 {{ margin: 5px 0; font-size: 22px; color: #1c1e21; }}
        p {{ color: #606770; margin-bottom: 25px; font-size: 15px; line-height: 1.4; }}
        .btn {{ background: #007AFF; color: white; padding: 16px 30px; text-decoration: none; border-radius: 12px; font-weight: bold; display: block; }}
        .btn:active {{ transform: scale(0.98); }}
    </style>
</head>
<body>
    <div class="card">
        <img src="{relative_img}" alt="Profile">
        <h2>{first} {last}</h2>
        <p>{role} <br> <b>{company}</b></p>
        <a href="../{VCF_DIR}/{slug}.vcf" class="btn">Save Contact</a>
    </div>
</body>
</html>"""
            
            with open(html_path, "w") as f:
                f.write(html_content)

            st.success(f"✅ Assets created for {first} {last}!")
            
            st.divider()
            st.warning("⚠️ **Important:** To make this live, download these files and upload them to your GitHub repository.")
            
            # Download Buttons
            colA, colB = st.columns(2)
            with colA:
                with open(vcf_path, "rb") as f:
                    st.download_button(f"Download VCF", f, file_name=f"{slug}.vcf")
            with colB:
                with open(html_path, "rb") as f:
                    st.download_button(f"Download HTML", f, file_name=f"{slug}.html")
        else:
            st.error("Please fill in all fields and upload a photo.")
