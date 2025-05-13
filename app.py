
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Streamlit App Title
st.title("Zen Leaf Menu Scrubber")
st.markdown("Paste a Zen Leaf menu URL to check for missing COA / Lab Results.")

# URL input
url = st.text_input("Zen Leaf Menu URL")

# Scrub trigger
if st.button("Scrub Menu") and url:
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Error fetching the menu: {e}")
    else:
        soup = BeautifulSoup(response.text, 'html.parser')
        products = soup.find_all('div', class_='ProductCard')

        if not products:
            st.warning("No products found on the page.")
        else:
            coa_keywords = ['coa', 'lab result', 'lab-tested', 'certificate']
            results = []

            for product in products:
                name_tag = product.find('p', class_='ProductCard__name')
                brand_tag = product.find('p', class_='ProductCard__brand')
                details = product.get_text().lower()

                product_name = name_tag.text.strip() if name_tag else "Unnamed Product"
                brand_name = brand_tag.text.replace("Brand:", "").strip() if brand_tag else "Unknown Brand"
                missing_coa = not any(keyword in details for keyword in coa_keywords)

                if missing_coa:
                    results.append({
                        "Product": product_name,
                        "Brand": brand_name,
                        "Missing COA": True
                    })

            if results:
                df = pd.DataFrame(results)
                st.dataframe(df)

                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name='zenleaf_missing_coa.csv',
                    mime='text/csv'
                )
            else:
                st.success("All products contain COA / lab result information.")
