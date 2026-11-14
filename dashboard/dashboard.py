from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="Bike Sharing Analytics Dashboard (2011–2012)",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid")


@st.cache_data
def load_data() -> pd.DataFrame:
    data_path = Path(__file__).resolve().parent / "main_data.csv"
    df = pd.read_csv(data_path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    df["time_cluster_clean"] = df["time_cluster"].str.replace("\n", " ", regex=False)
    df["demand_cluster_clean"] = df["demand_cluster"].str.replace("\n", " ", regex=False)
    return df


def create_daily_df(df: pd.DataFrame) -> pd.DataFrame:
    return df.groupby("dteday", as_index=False).agg(
        season=("season", "first"),
        yr=("yr", "first"),
        mnth=("mnth", "first"),
        weekday=("weekday", "first"),
        workingday=("workingday", "first"),
        daily_weathersit=("daily_weathersit", "first"),
        demand_cluster=("demand_cluster", "first"),
        demand_cluster_clean=("demand_cluster_clean", "first"),
        temp=("temp", "mean"),
        hum=("hum", "mean"),
        casual=("casual", "sum"),
        registered=("registered", "sum"),
        cnt=("cnt", "sum"),
    )


df = load_data()

# ==================== SIDEBAR FILTER ====================
with st.sidebar:
    st.title("🚲 Bike Sharing Analytics")
    st.caption("Periode Observasi: 2011 – 2012")
    st.markdown("---")
    st.subheader("Filter Data")

    min_date = df["dteday"].min().date()
    max_date = df["dteday"].max().date()

    date_range = st.date_input(
        label="Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date = end_date = date_range[0] if isinstance(date_range, tuple) else date_range

    season_options = ["Spring", "Summer", "Fall", "Winter"]
    selected_seasons = st.multiselect(
        label="Musim (Season)",
        options=season_options,
        default=season_options,
    )

    workingday_options = ["Working Day", "Weekend/Holiday"]
    selected_workingdays = st.multiselect(
        label="Kategori Hari",
        options=workingday_options,
        default=workingday_options,
    )

    weather_options = ["Clear/Partly Cloudy", "Mist/Cloudy", "Light Rain/Snow"]
    selected_weathers = st.multiselect(
        label="Kondisi Cuaca Harian",
        options=weather_options,
        default=weather_options,
    )

    st.markdown("---")
    st.caption("Proyek Akhir Analisis Data dengan Python")

# Terapkan filter
filtered_df = df[
    (df["dteday"].dt.date >= start_date)
    & (df["dteday"].dt.date <= end_date)
    & (df["season"].isin(selected_seasons))
    & (df["workingday"].isin(selected_workingdays))
    & (df["daily_weathersit"].isin(selected_weathers))
].copy()

# ==================== HEADER & KPI ====================
st.title("🚲 Dashboard Analisis Penyewaan Sepeda (Bike Sharing)")
st.markdown(
    f"Menampilkan ringkasan performa operasional, pola permintaan per jam, dampak cuaca & musim, "
    f"serta hasil *clustering* pada periode **{start_date.strftime('%d %b %Y')}** hingga **{end_date.strftime('%d %b %Y')}**."
)

if filtered_df.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter saat ini. Silakan ubah pilihan filter di sidebar.")
    st.stop()

daily_filtered = create_daily_df(filtered_df)

total_cnt = int(filtered_df["cnt"].sum())
total_registered = int(filtered_df["registered"].sum())
total_casual = int(filtered_df["casual"].sum())
avg_daily_cnt = daily_filtered["cnt"].mean()
reg_share = (total_registered / total_cnt * 100) if total_cnt > 0 else 0.0
cas_share = (total_casual / total_cnt * 100) if total_cnt > 0 else 0.0

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Total Penyewaan (cnt)", value=f"{total_cnt:,}")
with col2:
    st.metric(label="Rata-Rata Penyewaan / Hari", value=f"{avg_daily_cnt:,.0f}")
with col3:
    st.metric(
        label="Pengguna Registered",
        value=f"{total_registered:,}",
        delta=f"{reg_share:.1f}% dari total",
        delta_color="off",
    )
with col4:
    st.metric(
        label="Pengguna Casual",
        value=f"{total_casual:,}",
        delta=f"{cas_share:.1f}% dari total",
        delta_color="off",
    )

st.markdown("---")

# ==================== TABS VISUALISASI ====================
tab1, tab2, tab3 = st.tabs([
    "📈 1. Pola Penyewaan Per Jam (Pertanyaan 1)",
    "🌦️ 2. Dampak Cuaca & Musim (Pertanyaan 2)",
    "🧩 3. Analisis Lanjutan (Clustering)",
])

# -------------------- TAB 1: PERTANYAAN 1 --------------------
with tab1:
    st.subheader("Pola Rata-Rata Penyewaan Per Jam: Hari Kerja vs Akhir Pekan/Hari Libur")
    st.markdown(
        "Perbandingan kurva permintaan per jam (`00:00–23:00`) antara segmen pengguna **Registered** dan **Casual**."
    )

    hourly_agg = (
        filtered_df.groupby(["workingday", "hr"])[["casual", "registered", "cnt"]]
        .mean()
        .reset_index()
    )

    active_day_types = [d for d in ["Working Day", "Weekend/Holiday"] if d in hourly_agg["workingday"].unique()]
    n_panels = len(active_day_types)

    fig1, axes1 = plt.subplots(1, n_panels, figsize=(8 * n_panels, 5.2), sharey=True)
    if n_panels == 1:
        axes1 = [axes1]

    y_max_q1 = max(hourly_agg["cnt"].max() * 1.18, 100)

    subtitle_map = {
        "Working Day": "Hari Kerja (Working Day) — Pola Bimodal Komuter",
        "Weekend/Holiday": "Akhir Pekan & Hari Libur — Pola Unimodal Rekreasi Siang",
    }

    for ax, cat in zip(axes1, active_day_types):
        subset = hourly_agg[hourly_agg["workingday"] == cat]
        ax.plot(
            subset["hr"], subset["cnt"],
            label="Total Penyewaan (cnt)", color="#7f8c8d", linestyle="--", linewidth=1.8, alpha=0.85
        )
        ax.plot(
            subset["hr"], subset["registered"],
            label="Registered (Terdaftar)", color="#1f77b4", marker="o", markersize=5, linewidth=2.5
        )
        ax.plot(
            subset["hr"], subset["casual"],
            label="Casual (Kasual)", color="#ff7f0e", marker="s", markersize=5, linewidth=2.5
        )

        # Tandai jam puncak secara dinamis
        peak_row = subset.loc[subset["cnt"].idxmax()]
        ax.scatter([peak_row["hr"]], [peak_row["cnt"]], color="#d62728", zorder=5, s=65)
        ax.annotate(
            f"Puncak: {int(peak_row['hr']):02d}:00\n({peak_row['cnt']:.0f} sewa/jam)",
            xy=(peak_row["hr"], peak_row["cnt"]),
            xytext=(min(peak_row["hr"] + 1.2, 18.5), peak_row["cnt"] + y_max_q1 * 0.05),
            arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.4),
            fontsize=9.5,
            fontweight="bold",
            color="#c62828",
        )

        ax.set_title(subtitle_map.get(cat, cat), fontsize=11.5, fontweight="bold", pad=10)
        ax.set_xlabel("Jam (00:00 - 23:00)", fontsize=10.5)
        ax.set_xticks(range(0, 24, 2))
        ax.set_ylim(0, y_max_q1)
        ax.grid(axis="x", linestyle=":", alpha=0.5)
        ax.legend(frameon=True, facecolor="white", loc="upper left", fontsize=9)
        sns.despine(ax=ax)

    axes1[0].set_ylabel("Rata-Rata Jumlah Penyewaan / Jam", fontsize=10.5)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

    with st.expander("Lihat Ringkasan Angka Per Jam & Insight Utama"):
        st.info(
            "**Insight Utama:** Pada **Working Day**, permintaan membentuk dua puncak (*bimodal*) di jam berangkat kerja "
            "(**08:00**) dan pulang kerja (**17:00–18:00**) yang didominasi pengguna `registered`. Sebaliknya, pada "
            "**Weekend/Holiday**, permintaan memuncak di siang hari (**12:00–15:00**) dengan peningkatan signifikan dari "
            "segmen pengguna `casual`."
        )
        pivot_hr = hourly_agg.pivot(index="hr", columns="workingday", values=["cnt", "registered", "casual"]).round(1)
        st.dataframe(pivot_hr, use_container_width=True)

# -------------------- TAB 2: PERTANYAAN 2 --------------------
with tab2:
    st.subheader("Pengaruh Kondisi Cuaca dan Musim terhadap Volume Penyewaan Harian")
    st.markdown(
        "Perbandingan rata-rata volume penyewaan sepeda per hari (`cnt`) berdasarkan kondisi cuaca harian dan pergantian musim."
    )

    weather_order = [w for w in ["Clear/Partly Cloudy", "Mist/Cloudy", "Light Rain/Snow"] if w in daily_filtered["daily_weathersit"].unique()]
    weather_summary = (
        daily_filtered.groupby("daily_weathersit")["cnt"]
        .agg(["count", "mean"])
        .reindex(weather_order)
        .reset_index()
    )

    season_order = [s for s in ["Fall", "Summer", "Winter", "Spring"] if s in daily_filtered["season"].unique()]
    season_summary = (
        daily_filtered.groupby("season")["cnt"]
        .agg(["count", "mean"])
        .reindex(season_order)
        .reset_index()
    )

    y_max_q2 = max(
        weather_summary["mean"].max() if not weather_summary.empty else 0,
        season_summary["mean"].max() if not season_summary.empty else 0,
        100,
    ) * 1.22

    fig2, axes2 = plt.subplots(1, 2, figsize=(16, 5.5), sharey=True)

    # Panel Kiri: Cuaca
    w_colors = []
    for w in weather_summary["daily_weathersit"]:
        if w == "Clear/Partly Cloudy":
            w_colors.append("#1f77b4")
        elif w == "Light Rain/Snow":
            w_colors.append("#e57373")
        else:
            w_colors.append("#b0bec5")

    bars_w = axes2[0].bar(weather_summary["daily_weathersit"], weather_summary["mean"], color=w_colors, width=0.52)
    axes2[0].set_title("Rata-Rata Penyewaan Harian Berdasarkan Kondisi Cuaca", fontsize=11.5, fontweight="bold", pad=10)
    axes2[0].set_xlabel("Kondisi Cuaca Harian", fontsize=10.5)
    axes2[0].set_ylabel("Rata-Rata Penyewaan Sepeda / Hari", fontsize=10.5)
    axes2[0].set_ylim(0, y_max_q2)
    axes2[0].grid(axis="x", visible=False)
    sns.despine(ax=axes2[0])

    base_w = weather_summary["mean"].iloc[0] if not weather_summary.empty else 1
    for i, bar in enumerate(bars_w):
        val = bar.get_height()
        pct = ((val - base_w) / base_w) * 100
        lbl = f"{val:,.0f}\n(Baseline)" if i == 0 else f"{val:,.0f}\n({pct:+.1f}%)"
        axes2[0].text(
            bar.get_x() + bar.get_width() / 2,
            val + y_max_q2 * 0.02,
            lbl,
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold" if i in [0, len(bars_w) - 1] else "normal",
            color="#333333",
        )

    # Panel Kanan: Musim
    s_colors = []
    max_s = season_summary["mean"].max() if not season_summary.empty else 0
    min_s = season_summary["mean"].min() if not season_summary.empty else 0
    for val in season_summary["mean"]:
        if val == max_s:
            s_colors.append("#1f77b4")
        elif val == min_s and len(season_summary) > 1:
            s_colors.append("#e57373")
        else:
            s_colors.append("#b0bec5")

    bars_s = axes2[1].bar(season_summary["season"], season_summary["mean"], color=s_colors, width=0.52)
    axes2[1].set_title("Rata-Rata Penyewaan Harian Berdasarkan Musim", fontsize=11.5, fontweight="bold", pad=10)
    axes2[1].set_xlabel("Musim (Season)", fontsize=10.5)
    axes2[1].grid(axis="x", visible=False)
    sns.despine(ax=axes2[1])

    for i, bar in enumerate(bars_s):
        val = bar.get_height()
        pct = ((val - max_s) / max_s) * 100 if max_s > 0 else 0
        lbl = f"{val:,.0f}\n(Puncak)" if val == max_s else f"{val:,.0f}\n({pct:+.1f}%)"
        axes2[1].text(
            bar.get_x() + bar.get_width() / 2,
            val + y_max_q2 * 0.02,
            lbl,
            ha="center",
            va="bottom",
            fontsize=9.5,
            fontweight="bold" if val in [max_s, min_s] else "normal",
            color="#333333",
        )

    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.info(
        "**Insight Utama:** Pada keseluruhan periode 2011–2012, cuaca hujan ringan/salju (`Light Rain/Snow`) menurunkan "
        "rata-rata penyewaan harian hingga **63,0%** dibandingkan cuaca cerah (`Clear/Partly Cloudy`). Dari sisi musim, "
        "musim gugur (`Fall`) mencapai puncak tertinggi (**5.644** sewa/hari), sedangkan musim semi (`Spring`) turun "
        "**53,9%** menjadi **2.604** sewa/hari—menjadikannya waktu ideal untuk pemeliharaan besar armada."
    )

# -------------------- TAB 3: ANALISIS LANJUTAN (CLUSTERING) --------------------
with tab3:
    st.subheader("Analisis Lanjutan: Clustering (Manual Grouping & Binning)")
    st.markdown(
        "Segmentasi operasional tanpa algoritma *machine learning* menggunakan **Manual Grouping** (klaster periode jam) "
        "dan **Binning Kuantil** (klaster tingkat permintaan harian beserta profil suhu dan kelembapannya)."
    )

    fig3, axes3 = plt.subplots(1, 2, figsize=(16, 5.5))

    # Panel Kiri: Manual Grouping (Time Cluster)
    tc_order = [
        "Morning Commute\n(06:00-09:59)",
        "Midday / Leisure\n(10:00-15:59)",
        "Evening Commute\n(16:00-19:59)",
        "Night / Off-Peak\n(20:00-05:59)",
    ]
    tc_pivot = (
        filtered_df.groupby(["time_cluster", "workingday"])["cnt"]
        .mean()
        .unstack()
        .reindex(tc_order)
    )

    x = np.arange(len(tc_order))
    width = 0.36
    max_tc = 0

    if "Working Day" in tc_pivot.columns:
        vals_wd = tc_pivot["Working Day"].fillna(0)
        max_tc = max(max_tc, vals_wd.max())
        rects1 = axes3[0].bar(x - width / 2, vals_wd, width, label="Working Day", color="#1f77b4")
        for r in rects1:
            h = r.get_height()
            if h > 0:
                axes3[0].text(r.get_x() + r.get_width() / 2, h + 6, f"{h:.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#1f77b4")

    if "Weekend/Holiday" in tc_pivot.columns:
        vals_we = tc_pivot["Weekend/Holiday"].fillna(0)
        max_tc = max(max_tc, vals_we.max())
        rects2 = axes3[0].bar(x + width / 2, vals_we, width, label="Weekend/Holiday", color="#ff7f0e")
        for r in rects2:
            h = r.get_height()
            if h > 0:
                axes3[0].text(r.get_x() + r.get_width() / 2, h + 6, f"{h:.0f}", ha="center", va="bottom", fontsize=9, fontweight="bold", color="#d95f02")

    axes3[0].set_title("Manual Grouping: Rata-Rata Sewa/Jam per Klaster Waktu", fontsize=11.5, fontweight="bold", pad=10)
    axes3[0].set_xticks(x)
    axes3[0].set_xticklabels(tc_order, fontsize=9)
    axes3[0].set_ylabel("Rata-Rata Penyewaan / Jam", fontsize=10.5)
    axes3[0].set_ylim(0, max(max_tc * 1.2, 100))
    axes3[0].grid(axis="x", visible=False)
    axes3[0].legend(frameon=True, facecolor="white", loc="upper right")
    sns.despine(ax=axes3[0])

    # Panel Kanan: Binning (Demand Cluster)
    dc_order = [
        "Low Demand\n(22–3.740)",
        "Medium Demand\n(3.744–5.312)",
        "High Demand\n(5.315–8.714)",
    ]
    dc_summary = (
        daily_filtered.groupby("demand_cluster")
        .agg(
            jumlah_hari=("cnt", "count"),
            rata_rata_cnt=("cnt", "mean"),
            rata_rata_temp_c=("temp", lambda s: (s * 41).mean()),
            rata_rata_hum_pct=("hum", lambda s: (s * 100).mean()),
        )
        .reindex(dc_order)
        .dropna(subset=["rata_rata_cnt"])
        .reset_index()
    )

    dc_color_map = {
        "Low Demand\n(22–3.740)": "#e57373",
        "Medium Demand\n(3.744–5.312)": "#b0bec5",
        "High Demand\n(5.315–8.714)": "#1f77b4",
    }
    dc_colors = [dc_color_map.get(c, "#1f77b4") for c in dc_summary["demand_cluster"]]
    bars_dc = axes3[1].bar(dc_summary["demand_cluster"], dc_summary["rata_rata_cnt"], color=dc_colors, width=0.5)

    y_max_dc = max(dc_summary["rata_rata_cnt"].max() if not dc_summary.empty else 0, 100) * 1.25
    axes3[1].set_title("Binning (Kuantil): Volume & Suhu per Klaster Permintaan", fontsize=11.5, fontweight="bold", pad=10)
    axes3[1].set_xlabel("Klaster Tingkat Permintaan Harian", fontsize=10.5)
    axes3[1].set_ylabel("Rata-Rata Penyewaan / Hari", fontsize=10.5)
    axes3[1].set_ylim(0, y_max_dc)
    axes3[1].grid(axis="x", visible=False)
    sns.despine(ax=axes3[1])

    for i, bar in enumerate(bars_dc):
        h = bar.get_height()
        temp_c = dc_summary.loc[i, "rata_rata_temp_c"]
        hum_pct = dc_summary.loc[i, "rata_rata_hum_pct"]
        axes3[1].text(
            bar.get_x() + bar.get_width() / 2,
            h + y_max_dc * 0.02,
            f"{h:,.0f} sewa/hari\n(Suhu: {temp_c:.1f}°C | Hum: {hum_pct:.0f}%)",
            ha="center",
            va="bottom",
            fontsize=9,
            fontweight="bold",
            color="#333333",
        )

    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)

    with st.expander("Lihat Tabel Detail Klaster Permintaan Harian"):
        display_dc = dc_summary.copy()
        display_dc["demand_cluster"] = display_dc["demand_cluster"].str.replace("\n", " ", regex=False)
        display_dc.columns = ["Klaster Permintaan", "Jumlah Hari", "Rata-Rata Sewa/Hari", "Rata-Rata Suhu (°C)", "Rata-Rata Kelembapan (%)"]
        st.dataframe(display_dc.round(2), use_container_width=True)

st.markdown("---")
st.caption("Copyright © 2026 — Bike Sharing Data Analysis Project")