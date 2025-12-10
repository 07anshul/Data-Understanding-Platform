import streamlit
import requests

API_BASE_URL = "http://fastapi:8000/api/v1"

def search_papers(query: str, limit: int=10):
    try:
        resp = requests.get(
            f"{API_BASE_URL}/papers/search",
            params={"query": query, "limit": limit},
            timeout=15,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        streamlit.error(f"Failed to search papers. Please try again later.\n{e}")
        return []

def build_download_pdf_url(doi: str) -> str:
    return f"{API_BASE_URL}/papers/download?doi={doi}"

def main():
    streamlit.set_page_config(page_title="Paper Download", page_icon="📄", layout="wide")
    streamlit.title("Grab all the papers you need for your research!")

    query = streamlit.text_input("Search keyword, title, or DOI:", value="")
    limit = streamlit.slider("Select Top Results You Need", min_value=5, max_value=100, value=10, step=5)
    search_clicked = streamlit.button("Search", type="primary")

    if search_clicked:
        if not query.strip():
            streamlit.warning("Please enter a valid search keyword.")
            return

        with streamlit.spinner("Searching papers..."):
            results = search_papers(query=query, limit=limit)

        if not results:
            streamlit.info("No papers found for your query.")
            return

        streamlit.subheader("Results:")

        for item in results:
            title = item.get("title") or "Untitled"
            doi = item.get("doi")
            year = item.get("year")
            authors = item.get("authors") or []
            pdf_available = item.get("pdf_available", False)

            with streamlit.container(border=True):
                streamlit.markdown(f"**{title}**")
                meta_parts = []
                if year:
                    meta_parts.append(str(year))
                if authors:
                    meta_parts.append(", ".join(authors[:3]) + (" et al." if len(authors) > 3 else ""))
                if doi:
                    meta_parts.append(f"DOI: `{doi}`")

                if meta_parts:
                    streamlit.write(" • ".join(meta_parts))

                cols = streamlit.columns([1, 3])
                with cols[0]:
                    if pdf_available and doi:
                        download_url = build_download_pdf_url(doi)
                        streamlit.markdown(
                            f"[⬇️ Download PDF]({download_url})",
                            unsafe_allow_html=True,
                        )
                    else:
                        streamlit.caption("No open-access PDF detected for this paper.")


if __name__ == "__main__":
    main()