import streamlit as st
import pandas as pd
import os
import re
import zipfile
import shutil
from io import BytesIO

st.title("📍 Plus Code Country Sorter")

uploaded_file = st.file_uploader("Upload CSV file with 'PlusCode' column", type=['csv'])

def extract_country(code):
    match = re.search(r'\s(.+)', str(code))
    if match:
        location_part = match.group(1).strip()
        parts = [p.strip() for p in location_part.split(',')]
        if parts:
            return parts[-1]
    return None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)

        if 'Plus Code' not in df.columns:
            st.error("CSV must contain a column named 'PlusCode'")
        else:
            st.success("CSV file loaded successfully!")

            # Create output folders in memory
            base_folder = "output"
            output_folder = os.path.join(base_folder, "sorted_by_country")
            unrecognized_folder = os.path.join(base_folder, "unrecognized")

            os.makedirs(output_folder, exist_ok=True)
            os.makedirs(unrecognized_folder, exist_ok=True)

            grouped = {}
            unrecognized = []

            for _, row in df.iterrows():
                code = row['Plus Code']
                country = extract_country(code)

                if country:
                    grouped.setdefault(country, []).append(row)
                else:
                    unrecognized.append(row)

            # Save grouped files
            for country, rows in grouped.items():
                filename = f"{country.replace(' ', '_')}.csv"
                pd.DataFrame(rows).to_csv(os.path.join(output_folder, filename), index=False)

            # Save unrecognized
            if unrecognized:
                pd.DataFrame(unrecognized).to_csv(os.path.join(unrecognized_folder, "unrecognized.csv"), index=False)

            # Create ZIP
            zip_buffer = BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for folder_name, _, filenames in os.walk(base_folder):
                    for file in filenames:
                        file_path = os.path.join(folder_name, file)
                        arcname = os.path.relpath(file_path, base_folder)
                        zipf.write(file_path, arcname)

            st.success("✅ Processing complete!")
            st.download_button("📦 Download Result ZIP", zip_buffer.getvalue(), file_name="pluscode_sorted.zip")

            # Clean up temp folders after zipping
            shutil.rmtree(base_folder)

    except Exception as e:
        st.error(f"Error: {e}")
