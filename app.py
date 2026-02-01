import streamlit as st
import hmac
import os

# --- INITIAL SETUP ---
VCF_DIR = "vcf"
PAGE_DIR = "p"
os.makedirs(VCF_DIR, exist_ok=True)
os.makedirs(PAGE_DIR, exist_ok=True)

# --- LOGIN LOGIC ---
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
        st.title("🔐 NFC Manager Login")
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Access Denied")
        return False
    return True

# --- MAIN APP ---
if check_password():
    st.sidebar.button("Log Out", on_click=lambda: st.session_state.clear())
    st.title("📇 NFC Contact & Page Creator")
    
    with st.form("generator_form"):
        c1, c2 = st.columns(2)
        with c1:
            first = st.text_input("First Name")
            last = st.text_input("Last Name")
            phone = st.text_input("Phone (e.g. +919876543210)")
        with c2:
            email = st.text_input("Email")
            company = st.text_input("Company", value="BeyondWalls")
            role = st.text_input("Role")
            
        img_url = st.text_input("Profile Image URL", "https://via.placeholder.com/150")
        submit = st.form_submit_button("Generate Assets")

    if submit:
        if first and last and phone:
            slug = f"{first.lower()}_{last.lower()}"
            vcf_path = f"{VCF_DIR}/{slug}.vcf"
            html_path = f"{PAGE_DIR}/{slug}.html"

            # 1. Create VCF
            vcard = f"BEGIN:VCARD\nVERSION:3.0\nN:{last};{first};;;\nFN:{first} {last}\nORG:{company}\nTITLE:{role}\nTEL;TYPE=CELL:{phone}\nEMAIL;TYPE=INTERNET:{email}\nEND:VCARD"
            with open(vcf_path, "w") as f: f.write(vcard)

            # 2. Create HTML Landing Page
            html = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><style>
                body {{ font-family: sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                .card {{ background: white; width: 85%; max-width: 320px; padding: 30px; border-radius: 20px; box-shadow: 0 8px 20px rgba(0,0,0,0.15); text-align: center; }}
                img {{ width: 100px; height: 100px; border-radius: 50%; object-fit: cover; border: 3px solid #007AFF; }}
                .btn {{ background: #007AFF; color: white; padding: 15px; text-decoration: none; border-radius: 10px; display: block; margin-top: 20px; font-weight: bold; }}
            </style></head><body><div class="card">
                <img src="{img_url}"><h2>{first} {last}</h2><p>{role}<br>{company}</p>
                <a href="../vcf/{slug}.vcf" class="btn">Add to Contacts</a>
            </div></body></html>"""
            with open(html_path, "w") as f: f.write(html)

            st.success(f"Success! {slug} generated.")
            st.info(f"Link for NFC: https://yourusername.github.io/nfc-manager/p/{slug}.html")
        else:
            st.warning("Please fill required fields (Name/Phone).")
