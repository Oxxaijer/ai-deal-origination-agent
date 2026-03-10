import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from news_fetcher import fetch_company_news
from analyzer import analyze_article
from database import init_db, save_deal, fetch_saved_deals
from notifier import send_email_alert

init_db()

st.set_page_config(page_title="AI Deal Origination Agent v3", layout="wide")

st.markdown("""
    <style>
        .main-title {
            font-size: 42px;
            font-weight: 800;
            margin-bottom: 6px;
        }
        .sub-text {
            color: #666;
            margin-bottom: 20px;
        }
        .score-card {
            padding: 16px;
            border-radius: 14px;
            background: #f7f7f9;
            border: 1px solid #e6e6e9;
            margin-bottom: 10px;
        }
        .small-label {
            color: #777;
            font-size: 13px;
        }
        .big-value {
            font-size: 28px;
            font-weight: 700;
        }
        .top-deal-card {
            padding: 14px;
            border-radius: 12px;
            background: #fafafa;
            border: 1px solid #e8e8e8;
            margin-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">AI Deal Origination Agent v3</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-text">AI-powered company extraction, funding detection, scoring, storage, alerts, and dashboard intelligence.</div>',
    unsafe_allow_html=True
)

with st.sidebar:
    st.header("Search Settings")
    query = st.text_input(
        "News query",
        value="startup funding OR B2B software OR SaaS OR IT services OR acquisition"
    )
    page_size = st.slider("Number of articles", min_value=3, max_value=10, value=5)
    min_score_alert = st.slider("Email alert if overall score is at least", 1, 10, 8)
    run_analysis = st.button("Run Analysis")


def make_sector_chart(df: pd.DataFrame):
    sector_counts = df["industry"].fillna("Unknown").value_counts().head(8)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    sector_counts.plot(kind="bar", ax=ax)
    ax.set_title("Top Sectors")
    ax.set_xlabel("Industry")
    ax.set_ylabel("Count")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    return fig


def make_score_chart(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(df["overall_score"], bins=5)
    ax.set_title("Deal Score Distribution")
    ax.set_xlabel("Overall Score")
    ax.set_ylabel("Number of Deals")
    plt.tight_layout()
    return fig


def classify_score(score):
    if score >= 8:
        return "High Potential"
    if score >= 5:
        return "Medium Potential"
    return "Low Potential"


if run_analysis:
    try:
        with st.spinner("Fetching news..."):
            articles = fetch_company_news(query=query, page_size=page_size)

        if not articles:
            st.warning("No articles found. Try another search query.")
        else:
            st.success(f"Fetched {len(articles)} articles.")

            results = []
            progress_bar = st.progress(0)

            for index, article in enumerate(articles, start=1):
                title = article.get("title", "") or ""
                description = article.get("description", "") or ""
                content = article.get("content", "") or ""
                source = article.get("source", {}).get("name", "Unknown")
                url = article.get("url", "")
                published_at = article.get("publishedAt", "")

                analysis = analyze_article(
                    title=title,
                    description=description,
                    content=content,
                    source=source
                )

                deal = {
                    "company_name": analysis.get("company_name", "Unknown"),
                    "other_companies_mentioned": analysis.get("other_companies_mentioned", []),
                    "industry": analysis.get("industry", "Unknown"),
                    "event_type": analysis.get("event_type", "other"),
                    "funding_detected": analysis.get("funding_detected", False),
                    "funding_amount": analysis.get("funding_amount", ""),
                    "country_or_region": analysis.get("country_or_region", ""),
                    "summary": analysis.get("summary", ""),
                    "investment_signal": analysis.get("investment_signal", "Low"),
                    "growth_score": analysis.get("growth_score", 0),
                    "market_score": analysis.get("market_score", 0),
                    "strategic_fit": analysis.get("strategic_fit", 0),
                    "risk_score": analysis.get("risk_score", 0),
                    "overall_score": float(analysis.get("overall_score", 0)),
                    "reasoning": analysis.get("reasoning", ""),
                    "title": title,
                    "source": source,
                    "published_at": published_at,
                    "url": url
                }

                save_deal(deal)

                if deal["overall_score"] >= min_score_alert:
                    sent, message = send_email_alert(deal)
                    if sent:
                        st.success(f"Email sent for {deal['company_name']}")
                    else:
                        st.warning(f"Email not sent for {deal['company_name']}: {message}")

                results.append(deal)
                progress_bar.progress(index / len(articles))

            progress_bar.empty()

            df = pd.DataFrame(results)

            if not df.empty:
                df["score_band"] = df["overall_score"].apply(classify_score)

            high_count = int((df["overall_score"] >= 8).sum()) if not df.empty else 0
            funding_count = int(df["funding_detected"].sum()) if not df.empty else 0
            avg_score = round(df["overall_score"].mean(), 2) if not df.empty else 0
            top_sector = df["industry"].mode()[0] if not df.empty else "N/A"

            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(
                    f'<div class="score-card"><div class="small-label">Articles analysed</div><div class="big-value">{len(df)}</div></div>',
                    unsafe_allow_html=True
                )
            with c2:
                st.markdown(
                    f'<div class="score-card"><div class="small-label">Funding events detected</div><div class="big-value">{funding_count}</div></div>',
                    unsafe_allow_html=True
                )
            with c3:
                st.markdown(
                    f'<div class="score-card"><div class="small-label">Average deal score</div><div class="big-value">{avg_score}</div></div>',
                    unsafe_allow_html=True
                )
            with c4:
                st.markdown(
                    f'<div class="score-card"><div class="small-label">Top sector</div><div class="big-value" style="font-size:20px;">{top_sector}</div></div>',
                    unsafe_allow_html=True
                )

            st.subheader("Top Opportunities")
            top_deals = df.sort_values(by="overall_score", ascending=False).head(3)

            top_cols = st.columns(3)
            for i, (_, item) in enumerate(top_deals.iterrows()):
                with top_cols[i]:
                    st.markdown(
                        f"""
                        <div class="top-deal-card">
                            <div class="small-label">Company</div>
                            <div class="big-value" style="font-size:22px;">{item['company_name']}</div>
                            <br>
                            <div class="small-label">Industry</div>
                            <div>{item['industry']}</div>
                            <br>
                            <div class="small-label">Overall Score</div>
                            <div class="big-value">{item['overall_score']}</div>
                            <br>
                            <div class="small-label">Signal</div>
                            <div>{item['investment_signal']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

            st.subheader("Dashboard Charts")
            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                sector_fig = make_sector_chart(df)
                st.pyplot(sector_fig)

            with chart_col2:
                score_fig = make_score_chart(df)
                st.pyplot(score_fig)

            st.subheader("Deal Signals")
            st.dataframe(
                df[
                    [
                        "company_name",
                        "industry",
                        "event_type",
                        "funding_detected",
                        "funding_amount",
                        "growth_score",
                        "market_score",
                        "strategic_fit",
                        "risk_score",
                        "overall_score",
                        "score_band",
                        "investment_signal",
                        "source"
                    ]
                ].sort_values(by="overall_score", ascending=False),
                use_container_width=True
            )

            st.subheader("Detailed Analysis")
            for item in sorted(results, key=lambda x: x["overall_score"], reverse=True):
                with st.expander(f"{item['company_name']} — score {item['overall_score']}"):
                    st.markdown(f"**Article title:** {item['title']}")
                    st.markdown(f"**Industry:** {item['industry']}")
                    st.markdown(f"**Event type:** {item['event_type']}")
                    st.markdown(f"**Funding detected:** {item['funding_detected']}")
                    st.markdown(f"**Funding amount:** {item['funding_amount'] or 'Not stated'}")
                    st.markdown(f"**Region:** {item['country_or_region'] or 'Unknown'}")
                    st.markdown(
                        f"**Other companies mentioned:** {', '.join(item['other_companies_mentioned']) if item['other_companies_mentioned'] else 'None'}"
                    )
                    st.markdown(f"**Investment signal:** {item['investment_signal']}")
                    st.markdown(f"**Growth score:** {item['growth_score']}/10")
                    st.markdown(f"**Market score:** {item['market_score']}/10")
                    st.markdown(f"**Strategic fit:** {item['strategic_fit']}/10")
                    st.markdown(f"**Risk score:** {item['risk_score']}/10")
                    st.markdown(f"**Overall score:** {item['overall_score']}/10")
                    st.markdown(f"**Summary:** {item['summary']}")
                    st.markdown(f"**Reasoning:** {item['reasoning']}")
                    st.markdown(f"**Source:** {item['source']}")
                    st.markdown(f"**Published at:** {item['published_at']}")
                    st.markdown(f"**Article link:** {item['url']}")

            st.subheader("Saved Deals Database")
            saved_rows = fetch_saved_deals(limit=20)
            if saved_rows:
                saved_df = pd.DataFrame(
                    saved_rows,
                    columns=[
                        "company_name", "industry", "event_type", "funding_detected",
                        "funding_amount", "overall_score", "investment_signal",
                        "source", "published_at", "url"
                    ]
                )
                st.dataframe(saved_df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "Download CSV",
                data=csv_data,
                file_name="deal_signals_v3.csv",
                mime="text/csv"
            )

    except Exception as error:
        st.error(f"Something went wrong: {error}")
else:
    st.info("Set your search query in the sidebar and click Run Analysis.")