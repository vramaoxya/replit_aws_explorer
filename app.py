import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Ressources AWS",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSV_PATH = "attached_assets/ec2_prices_20260410-140511_1782061605327.csv"

REGION_FLAGS = {
    "eu-central-1": "🇩🇪",
    "eu-central-2": "🇨🇭",
    "eu-north-1": "🇸🇪",
    "eu-south-1": "🇮🇹",
    "eu-south-2": "🇪🇸",
    "eu-west-1": "🇮🇪",
    "eu-west-2": "🇬🇧",
    "eu-west-3": "🇫🇷",
    "us-east-1": "🇺🇸",
    "us-east-2": "🇺🇸",
}

REGION_CITIES = {
    "eu-central-1": "Frankfurt, Allemagne",
    "eu-central-2": "Zurich, Suisse",
    "eu-north-1": "Stockholm, Suède",
    "eu-south-1": "Milan, Italie",
    "eu-south-2": "Madrid, Espagne",
    "eu-west-1": "Dublin, Irlande",
    "eu-west-2": "Londres, Royaume-Uni",
    "eu-west-3": "Paris, France",
    "us-east-1": "Virginie du Nord, USA",
    "us-east-2": "Ohio, USA",
}

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_PATH, sep=";", decimal=",", low_memory=False)
    numeric_cols = [
        "CostH1yr","CostMRR1yr","CostYRR1yr",
        "CostH3yr","CostMRR3yr","CostYRR3yr",
        "ODH","ODMRR","ODYRR",
        "SnapG/M","gp2G/M","gp3G/M","io1G/M","st1G/M",
        "s3<50T","s3<450T","s3>500T","glacierG/M",
        "CPU","RAM","SAPS"
    ]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Region Code"] = df["Region Code"].str.strip()
    df["Region Name"] = df["Region Name"].str.strip()
    df["Ec2Type"] = df["Ec2Type"].str.strip()
    df["OS"] = df["OS"].str.strip()
    df["SavingsPlanH"] = df["CostH1yr"] * 1.05
    df["SavingsPlanMRR"] = df["CostMRR1yr"] * 1.05
    return df

df = load_data()

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/9/93/Amazon_Web_Services_Logo.svg", width=120)
    st.markdown("## Navigation")
    page = st.radio(
        "Choisir une section",
        [
            "🏠 Accueil",
            "💻 Ressources EC2",
            "📊 Analyse coûts EC2",
            "🗄️ Coûts S3 & EBS",
        ],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.caption("Données : AWS Pricing · Mise à jour : Avril 2026")
    regions_available = sorted(df["Region Name"].unique())
    st.markdown(f"**{len(regions_available)} régions** · **{len(df):,} instances**")


if page == "🏠 Accueil":
    st.title("☁️ Ressources AWS")
    st.markdown("### Plateforme de visualisation des coûts et ressources Amazon Web Services par région")
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Régions couvertes", len(df["Region Code"].unique()))
    with col2:
        st.metric("Types d'instances EC2", df["Ec2Type"].nunique())
    with col3:
        st.metric("Systèmes d'exploitation", df["OS"].nunique())
    with col4:
        st.metric("Enregistrements totaux", f"{len(df):,}")

    st.markdown("---")
    st.subheader("🌍 Régions disponibles")
    region_summary = df.groupby(["Region Code","Region Name"]).agg(
        instances=("Ec2Type","nunique"),
        od_min=("ODH","min"),
        od_max=("ODH","max"),
    ).reset_index()

    cols = st.columns(3)
    for i, row in region_summary.iterrows():
        flag = REGION_FLAGS.get(row["Region Code"], "🌐")
        city = REGION_CITIES.get(row["Region Code"], row["Region Name"])
        with cols[i % 3]:
            st.markdown(f"""
**{flag} {row['Region Name']}**  
📍 {city}  
🖥️ {row['instances']} types d'instances  
💰 On-Demand: \${row['od_min']:.4f} – \${row['od_max']:.3f} /h
""")
            st.markdown("---")

    st.markdown("---")
    st.subheader("📚 À propos des ressources AWS présentées")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("#### 💻 Amazon EC2")
        st.markdown("""
**Elastic Compute Cloud** est le service de calcul à la demande d'AWS.

- Instances virtuelles dans le cloud
- Différents types : General Purpose, Compute Optimized, Memory Optimized
- **Modèles de tarification** : On-Demand, Reserved (1 an, 3 ans), Savings Plans
- Facturation à la seconde (minimum 60s)
- Disponible dans toutes les régions mondiales
        """)

    with c2:
        st.markdown("#### 🗃️ Amazon S3")
        st.markdown("""
**Simple Storage Service** est le service de stockage objet d'AWS.

- Stockage illimité et hautement disponible
- Durabilité de 99,999999999% (11 neuf)
- **Tarification par palier** : < 50 TB, < 450 TB, > 500 TB
- Archivage via Amazon Glacier
- Réplication multi-régions disponible
        """)

    with c3:
        st.markdown("#### 💾 Amazon EBS")
        st.markdown("""
**Elastic Block Store** est le service de stockage en bloc pour EC2.

- Volumes persistants attachés aux instances EC2
- **Types de volumes** : gp2, gp3, io1, st1
- Facturation au Go/mois provisionné
- Snapshots facturés séparément
- Performance ajustable selon le type
        """)

    st.markdown("---")
    st.subheader("📈 Comparaison rapide des coûts On-Demand par région")
    pivot = df.groupby("Region Name")["ODH"].mean().reset_index()
    pivot.columns = ["Région", "Coût horaire moyen ($)"]
    pivot = pivot.sort_values("Coût horaire moyen ($)", ascending=True)

    fig = px.bar(
        pivot,
        x="Coût horaire moyen ($)",
        y="Région",
        orientation="h",
        color="Coût horaire moyen ($)",
        color_continuous_scale="Blues",
        title="Coût horaire moyen On-Demand EC2 par région"
    )
    fig.update_layout(height=400, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")


elif page == "💻 Ressources EC2":
    st.title("💻 Instances EC2 par Région")
    st.markdown("Explorez et comparez les instances EC2 disponibles dans chaque région AWS.")
    st.markdown("---")

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        selected_regions = st.multiselect(
            "Régions",
            options=sorted(df["Region Name"].unique()),
            default=sorted(df["Region Name"].unique())[:3]
        )
    with col_f2:
        selected_os = st.multiselect(
            "Système d'exploitation",
            options=sorted(df["OS"].dropna().unique()),
            default=sorted(df["OS"].dropna().unique())
        )
    with col_f3:
        family_options = sorted(df["Ec2Type"].dropna().str.extract(r'^([a-z0-9]+)\.')[0].dropna().unique())
        selected_family = st.multiselect("Famille d'instances", options=family_options, default=family_options[:5])

    if not selected_regions:
        st.warning("Veuillez sélectionner au moins une région.")
        st.stop()

    fdf = df[df["Region Name"].isin(selected_regions)]
    if selected_os:
        fdf = fdf[fdf["OS"].isin(selected_os)]
    if selected_family:
        fdf = fdf[fdf["Ec2Type"].str.extract(r'^([a-z0-9]+)\.')[0].isin(selected_family)]

    st.markdown(f"**{len(fdf):,} instances** correspondent aux filtres sélectionnés.")
    st.markdown("---")

    st.subheader("🔥 Comparaison des coûts On-Demand par région")
    fig_box = px.box(
        fdf,
        x="Region Name",
        y="ODH",
        color="Region Name",
        title="Distribution des coûts horaires On-Demand par région",
        labels={"ODH": "Coût horaire ($)", "Region Name": "Région"}
    )
    fig_box.update_layout(height=450, showlegend=False, xaxis_tickangle=-30)
    st.plotly_chart(fig_box, width="stretch")

    st.subheader("📊 Coût moyen par famille d'instance et région")
    fdf2 = fdf.copy()
    fdf2["Famille"] = fdf2["Ec2Type"].str.extract(r'^([a-z0-9]+)\.')
    pivot2 = fdf2.groupby(["Famille","Region Name"])["ODH"].mean().reset_index()
    fig_heat = px.density_heatmap(
        pivot2,
        x="Region Name",
        y="Famille",
        z="ODH",
        color_continuous_scale="YlOrRd",
        title="Coût horaire moyen On-Demand ($) par famille & région",
        labels={"ODH": "$/h", "Region Name": "Région", "Famille": "Famille"}
    )
    fig_heat.update_layout(height=500, xaxis_tickangle=-30)
    st.plotly_chart(fig_heat, width="stretch")

    st.subheader("🔍 CPU vs RAM vs Coût")
    fig_scatter = px.scatter(
        fdf,
        x="CPU",
        y="RAM",
        size="ODH",
        color="Region Name",
        hover_data=["Ec2Type","ODH","OS"],
        title="CPU / RAM / Coût On-Demand par région",
        labels={"CPU": "vCPU", "RAM": "RAM (Go)", "ODH": "Coût $/h"}
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, width="stretch")

    st.subheader("📋 Tableau détaillé")
    display_cols = ["Region Name","Ec2Type","OS","CPU","RAM","ODH","ODMRR","CostH1yr","CostH3yr"]
    available_cols = [c for c in display_cols if c in fdf.columns]
    show_df = fdf[available_cols].copy()
    show_df.columns = ["Région","Type","OS","vCPU","RAM (Go)","$/h OD","$/mois OD","$/h 1an","$/h 3ans"][:len(available_cols)]
    st.dataframe(
        show_df.sort_values("$/h OD").head(200),
        width="stretch",
        hide_index=True
    )


elif page == "📊 Analyse coûts EC2":
    st.title("📊 Analyse des Coûts EC2 par Région et Engagement")
    st.markdown("Comparez les coûts EC2 selon le type d'engagement : On-Demand, 1 an, 3 ans et Savings Plans.")
    st.markdown("---")

    c1, c2 = st.columns(2)
    with c1:
        sel_region = st.selectbox(
            "Région principale",
            options=sorted(df["Region Name"].unique()),
            index=0
        )
    with c2:
        compare_regions = st.multiselect(
            "Comparer avec d'autres régions",
            options=[r for r in sorted(df["Region Name"].unique()) if r != sel_region],
            default=[]
        )

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        sel_os = st.selectbox("OS", options=["Tous"] + sorted(df["OS"].dropna().unique().tolist()))
    with col_f2:
        commitment = st.multiselect(
            "Types d'engagement",
            options=["On-Demand (PayAsYouGo)","Reserved 1 an","Reserved 3 ans","Savings Plan (~1 an)"],
            default=["On-Demand (PayAsYouGo)","Reserved 1 an","Reserved 3 ans","Savings Plan (~1 an)"]
        )

    all_regions = [sel_region] + compare_regions
    rdf = df[df["Region Name"].isin(all_regions)].copy()
    if sel_os != "Tous":
        rdf = rdf[rdf["OS"] == sel_os]

    cost_map = {
        "On-Demand (PayAsYouGo)": "ODH",
        "Reserved 1 an": "CostH1yr",
        "Reserved 3 ans": "CostH3yr",
        "Savings Plan (~1 an)": "SavingsPlanH"
    }

    st.markdown("---")
    st.subheader(f"💰 Coûts mensuels comparés par type d'engagement")

    melted_rows = []
    for reg in all_regions:
        reg_df = rdf[rdf["Region Name"] == reg]
        for eng in commitment:
            col_key = cost_map.get(eng)
            if col_key and col_key in reg_df.columns:
                avg_mrr = reg_df[col_key].mean() * 730
                melted_rows.append({"Région": reg, "Engagement": eng, "Coût mensuel moyen ($)": avg_mrr})

    if melted_rows:
        melted_df = pd.DataFrame(melted_rows)
        fig_bar = px.bar(
            melted_df,
            x="Engagement",
            y="Coût mensuel moyen ($)",
            color="Région",
            barmode="group",
            title="Coût mensuel moyen (730h) par type d'engagement et région",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_bar.update_layout(height=450, xaxis_tickangle=-15)
        st.plotly_chart(fig_bar, width="stretch")

    st.subheader("📉 Économies réalisées vs On-Demand")
    savings_rows = []
    for reg in all_regions:
        reg_df = rdf[rdf["Region Name"] == reg]
        od_avg = reg_df["ODH"].mean()
        if od_avg > 0:
            for eng in ["Reserved 1 an","Reserved 3 ans","Savings Plan (~1 an)"]:
                col_key = cost_map.get(eng)
                if col_key and col_key in reg_df.columns:
                    eng_avg = reg_df[col_key].mean()
                    saving_pct = (1 - eng_avg / od_avg) * 100
                    savings_rows.append({"Région": reg, "Engagement": eng, "Économie (%)": saving_pct})

    if savings_rows:
        sdf = pd.DataFrame(savings_rows)
        fig_sav = px.bar(
            sdf,
            x="Engagement",
            y="Économie (%)",
            color="Région",
            barmode="group",
            title="Économie moyenne vs On-Demand par type d'engagement",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_sav.update_layout(height=400)
        fig_sav.add_hline(y=0, line_dash="dot", line_color="gray")
        st.plotly_chart(fig_sav, width="stretch")

    st.markdown("---")
    st.subheader(f"🏆 Instances les plus chères par région")
    top_n = st.slider("Nombre d'instances à afficher", 5, 20, 10)

    tabs = st.tabs(all_regions)
    for i, reg in enumerate(all_regions):
        with tabs[i]:
            reg_top = rdf[rdf["Region Name"] == reg].nlargest(top_n, "ODH")[
                ["Ec2Type","OS","CPU","RAM","ODH","ODMRR","ODYRR","CostH1yr","CostH3yr"]
            ].copy()
            reg_top.columns = ["Type","OS","vCPU","RAM(Go)","$/h OD","$/mois OD","$/an OD","$/h 1an","$/h 3ans"]
            st.dataframe(reg_top, width="stretch", hide_index=True)

            fig_top = px.bar(
                reg_top.sort_values("$/h OD", ascending=True),
                x="$/h OD",
                y="Type",
                orientation="h",
                color="$/h OD",
                color_continuous_scale="Reds",
                title=f"Top {top_n} instances les plus chères — {reg}"
            )
            fig_top.update_layout(height=400, coloraxis_showscale=False)
            st.plotly_chart(fig_top, width="stretch")

    st.markdown("---")
    st.subheader("🗓️ Projection de coûts annuels")
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        num_instances = st.number_input("Nombre d'instances", min_value=1, max_value=10000, value=10)
    with col_p2:
        instance_filter = st.text_input("Filtrer par type (ex: m5, c6i)", value="")

    proj_df = rdf[rdf["Region Name"] == sel_region].copy()
    if instance_filter:
        proj_df = proj_df[proj_df["Ec2Type"].str.contains(instance_filter, case=False, na=False)]

    if not proj_df.empty:
        proj_rows = []
        for eng in commitment:
            col_key = cost_map.get(eng)
            if col_key and col_key in proj_df.columns:
                annual = proj_df[col_key].mean() * 8760 * num_instances
                proj_rows.append({"Engagement": eng, "Coût annuel total ($)": annual})

        proj_df2 = pd.DataFrame(proj_rows)
        fig_proj = px.bar(
            proj_df2,
            x="Engagement",
            y="Coût annuel total ($)",
            color="Engagement",
            title=f"Projection annuelle pour {num_instances} instances — {sel_region}",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_proj.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_proj, width="stretch")


elif page == "🗄️ Coûts S3 & EBS":
    st.title("🗄️ Coûts S3 & EBS par Région")
    st.markdown("Visualisez et comparez les coûts de stockage objet (S3) et bloc (EBS) dans chaque région AWS.")
    st.markdown("---")

    region_storage = df.groupby(["Region Code","Region Name"]).agg(
        gp2=("gp2G/M","first"),
        gp3=("gp3G/M","first"),
        io1=("io1G/M","first"),
        st1=("st1G/M","first"),
        snap=("SnapG/M","first"),
        s3_50=("s3<50T","first"),
        s3_450=("s3<450T","first"),
        s3_500=("s3>500T","first"),
        glacier=("glacierG/M","first"),
    ).reset_index()

    st.subheader("💾 EBS — Coûts par type de volume et région")

    ebs_melt = region_storage.melt(
        id_vars=["Region Code","Region Name"],
        value_vars=["gp2","gp3","io1","st1"],
        var_name="Type EBS",
        value_name="$/Go/mois"
    )
    ebs_labels = {"gp2": "GP2 (SSD généraliste)", "gp3": "GP3 (SSD performant)", "io1": "IO1 (SSD haute perf.)", "st1": "ST1 (HDD séquentiel)"}
    ebs_melt["Type EBS"] = ebs_melt["Type EBS"].map(ebs_labels)

    fig_ebs = px.bar(
        ebs_melt.dropna(),
        x="Region Name",
        y="$/Go/mois",
        color="Type EBS",
        barmode="group",
        title="Tarifs EBS par type de volume et région ($/Go/mois)",
        color_discrete_sequence=px.colors.qualitative.Set1,
        labels={"Region Name": "Région"}
    )
    fig_ebs.update_layout(height=450, xaxis_tickangle=-30)
    st.plotly_chart(fig_ebs, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📊 Comparaison GP2 vs GP3")
        fig_gp = px.scatter(
            region_storage.dropna(subset=["gp2","gp3"]),
            x="gp2",
            y="gp3",
            text="Region Name",
            title="GP2 vs GP3 — économies potentielles",
            labels={"gp2": "GP2 $/Go/mois", "gp3": "GP3 $/Go/mois"},
            color_discrete_sequence=["#636EFA"]
        )
        max_val = max(region_storage["gp2"].max(), region_storage["gp3"].max()) * 1.1
        fig_gp.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val,
                         line=dict(dash="dash", color="red"), name="Équivalence")
        fig_gp.update_traces(textposition="top center")
        fig_gp.update_layout(height=400)
        st.plotly_chart(fig_gp, width="stretch")
        st.caption("Les points sous la ligne rouge indiquent que GP3 est moins cher que GP2.")

    with c2:
        st.subheader("🧊 Snapshot & Glacier")
        snap_melt = region_storage.melt(
            id_vars=["Region Name"],
            value_vars=["snap","glacier"],
            var_name="Type",
            value_name="$/Go/mois"
        )
        snap_melt["Type"] = snap_melt["Type"].map({"snap": "Snapshot EBS", "glacier": "Glacier (Archivage)"})
        fig_snap = px.bar(
            snap_melt.dropna(),
            x="Region Name",
            y="$/Go/mois",
            color="Type",
            barmode="group",
            title="Coûts Snapshot & Glacier par région",
            labels={"Region Name": "Région"},
            color_discrete_sequence=["#00CC96","#AB63FA"]
        )
        fig_snap.update_layout(height=400, xaxis_tickangle=-30)
        st.plotly_chart(fig_snap, width="stretch")

    st.markdown("---")
    st.subheader("🪣 Amazon S3 — Tarifs par palier de stockage et région")

    s3_melt = region_storage.melt(
        id_vars=["Region Code","Region Name"],
        value_vars=["s3_50","s3_450","s3_500"],
        var_name="Palier S3",
        value_name="$/Go/mois"
    )
    s3_labels = {
        "s3_50": "Tranche 1 : 0–50 TB",
        "s3_450": "Tranche 2 : 50–500 TB",
        "s3_500": "Tranche 3 : > 500 TB"
    }
    s3_melt["Palier S3"] = s3_melt["Palier S3"].map(s3_labels)

    fig_s3 = px.bar(
        s3_melt.dropna(),
        x="Region Name",
        y="$/Go/mois",
        color="Palier S3",
        barmode="group",
        title="Tarifs S3 Standard par palier de stockage et région",
        labels={"Region Name": "Région"},
        color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    fig_s3.update_layout(height=450, xaxis_tickangle=-30)
    st.plotly_chart(fig_s3, width="stretch")

    st.subheader("💡 Simulateur de coût de stockage mensuel")
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        sim_region = st.selectbox("Région", options=sorted(df["Region Name"].unique()), key="sim_reg")
        s3_vol = st.number_input("Volume S3 (To)", min_value=0.0, value=10.0, step=1.0)
    with col_s2:
        ebs_gp3_vol = st.number_input("Volume EBS gp3 (Go)", min_value=0, value=500, step=100)
        ebs_io1_vol = st.number_input("Volume EBS io1 (Go)", min_value=0, value=0, step=100)
    with col_s3:
        snap_vol = st.number_input("Snapshots EBS (Go)", min_value=0, value=200, step=50)
        glacier_vol = st.number_input("Glacier (Go)", min_value=0, value=0, step=100)

    sim_row = region_storage[region_storage["Region Name"] == sim_region].iloc[0] if not region_storage[region_storage["Region Name"] == sim_region].empty else None

    if sim_row is not None:
        s3_gb = s3_vol * 1024
        s3_cost = 0.0
        if s3_gb <= 50 * 1024:
            s3_cost = s3_gb * sim_row["s3_50"]
        elif s3_gb <= 500 * 1024:
            s3_cost = (50 * 1024 * sim_row["s3_50"]) + ((s3_gb - 50 * 1024) * sim_row["s3_450"])
        else:
            s3_cost = (50 * 1024 * sim_row["s3_50"]) + (450 * 1024 * sim_row["s3_450"]) + ((s3_gb - 500 * 1024) * sim_row["s3_500"])

        ebs_gp3_cost = ebs_gp3_vol * sim_row["gp3"]
        ebs_io1_cost = ebs_io1_vol * sim_row["io1"]
        snap_cost = snap_vol * sim_row["snap"]
        glacier_cost = glacier_vol * sim_row["glacier"]
        total_cost = s3_cost + ebs_gp3_cost + ebs_io1_cost + snap_cost + glacier_cost

        sim_data = {
            "Composant": ["S3 Standard", "EBS GP3", "EBS IO1", "Snapshots EBS", "Glacier"],
            "Coût mensuel ($)": [s3_cost, ebs_gp3_cost, ebs_io1_cost, snap_cost, glacier_cost]
        }
        sim_df = pd.DataFrame(sim_data)
        sim_df_filtered = sim_df[sim_df["Coût mensuel ($)"] > 0]

        col_r1, col_r2 = st.columns([1, 2])
        with col_r1:
            st.metric("💰 Coût mensuel total estimé", f"${total_cost:,.2f}")
            st.metric("💰 Coût annuel total estimé", f"${total_cost * 12:,.2f}")
            st.markdown("**Détail par composant :**")
            for _, row_s in sim_df.iterrows():
                if row_s["Coût mensuel ($)"] > 0:
                    st.markdown(f"- **{row_s['Composant']}** : ${row_s['Coût mensuel ($)']:,.2f}/mois")

        with col_r2:
            if not sim_df_filtered.empty:
                fig_pie = px.pie(
                    sim_df_filtered,
                    values="Coût mensuel ($)",
                    names="Composant",
                    title=f"Répartition des coûts — {sim_region}",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set2
                )
                fig_pie.update_layout(height=350)
                st.plotly_chart(fig_pie, width="stretch")

    st.markdown("---")
    st.subheader("📋 Tableau récapitulatif des tarifs de stockage")
    display_storage = region_storage[[
        "Region Name","gp2","gp3","io1","st1","snap","s3_50","s3_450","s3_500","glacier"
    ]].copy()
    display_storage.columns = [
        "Région","EBS gp2 ($/Go/m)","EBS gp3 ($/Go/m)","EBS io1 ($/Go/m)","EBS st1 ($/Go/m)",
        "Snapshot ($/Go/m)","S3 <50TB ($/Go/m)","S3 <500TB ($/Go/m)","S3 >500TB ($/Go/m)","Glacier ($/Go/m)"
    ]
    st.dataframe(display_storage, width="stretch", hide_index=True)
