import pandas as pd
import plotly.express as raw_px
import dash_bootstrap_components as dbc
from dash import html
import vizro.models as vm
from vizro import Vizro
from vizro.models.types import capture
import os

# ==========================================
# BUSINESS BLUE PALETTE 
# ==========================================
BUSINESS_COLORS = [
    "#1e40af",  # Deep Navy Blue
    "#2563eb",  # Royal Blue
    "#3b82f6",  # Sky Blue
    "#0ea5e9",  # Ocean Blue
    "#06b6d4",  # Teal / Cyan
    "#475569",  # Slate Grey
    "#6366f1",  # Indigo
    "#8b5cf6"   # Violet
]

def customize_fig(fig, is_area=False):
    """Applies a premium styling to Plotly Express charts, supporting both light and dark themes."""
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_family="Inter, sans-serif",
        title=dict(
            font=dict(size=15),
            x=0.02,
            xanchor="left",
            y=0.97,
            yanchor="top",
            pad=dict(b=10)
        ),
        margin=dict(l=55, r=20, t=70, b=45),
        xaxis=dict(
            zerolinecolor="#cbd5e1"
        ),
        yaxis=dict(
            zerolinecolor="#cbd5e1"
        ),
        legend=dict(font=dict(size=10))
    )
    if is_area:
        fig.update_traces(line_shape='spline', line_width=3)
    return fig

# ==========================================
# KPI Cards
# ==========================================
@capture("figure")
def custom_kpi_card(data_frame, value_column=None, agg_func="sum", title=None, value_type="currency"):
    """Creates a custom reactive KPI Card component that formats values in Trillions, Billions, or percentages."""
    if data_frame.empty:
        val = "No Data"
    else:
        if agg_func == "sum":
            val = data_frame[value_column].sum()
        elif agg_func == "mean":
            val = data_frame[value_column].mean()
        elif agg_func == "max":
            val = data_frame[value_column].max()
        elif agg_func == "min":
            val = data_frame[value_column].min()
        elif agg_func == "nunique":
            val = data_frame[value_column].nunique()
        elif agg_func == "avg_monthly_volume":
            val = data_frame.groupby("tahun_bulan")["volume"].sum().mean()
        elif agg_func == "most_active_crypto":
            val = data_frame.groupby("asset_name")["volume"].sum().idxmax()
        elif agg_func == "most_active_month":
            val = data_frame.groupby("tahun_bulan")["volume"].sum().idxmax()
        elif agg_func == "most_active_year":
            val = str(data_frame.groupby("Tahun")["volume"].sum().idxmax())
        elif agg_func == "max_price_gain":
            val = data_frame["price_change_pct"].max()
        elif agg_func == "min_price_drop":
            val = data_frame["price_change_pct"].min()
        else:
            val = 0

    if isinstance(val, str):
        formatted_val = val
    elif value_type == "currency":
        if val >= 1e12:
            formatted_val = f"${val / 1e12:.2f} Triliun"
        elif val >= 1e9:
            formatted_val = f"${val / 1e9:.2f} Miliar"
        elif val >= 1e6:
            formatted_val = f"${val / 1e6:.2f} Juta"
        else:
            formatted_val = f"${val:,.2f}"
    elif value_type == "percent":
        formatted_val = f"{val:+.2f}%" if val > 0 else f"{val:.2f}%"
    elif value_type == "days":
        formatted_val = f"{val:,.1f} Hari" if val % 1 != 0 else f"{val:,.0f} Hari"
    elif value_type == "count":
        formatted_val = f"{val:,.0f} Aset"
    else:
        formatted_val = f"{val:,.0f}"

    return dbc.Card([
   html.H3(
    title or "KPI",
    style={
        "fontSize": "18px",
        "fontWeight": "500"
    }
),
    html.P(
    formatted_val,
    style={
        "fontSize": "30px",
        "fontWeight": "700",
        "margin": "0"
    }
)
], className="kpi-card")
# ==========================================
#  GRAPH FIGURES
# ==========================================
@capture("graph")
def make_volume_monthly_bar(data_frame):
    # Mengelompokkan berdasarkan tahun dan menghitung total volume
    df_agg = data_frame.groupby('Tahun', as_index=False)['volume'].sum()

    fig = raw_px.bar(
        df_agg, x="Tahun", y="volume",
        color_discrete_sequence=[BUSINESS_COLORS[0]], # Gunakan satu warna atau bisa diubah
        text_auto=".2s",
        labels={"Tahun": "Tahun", "volume": "Volume($)"},
        title="Total Volume Perdagangan Cryptocurrency (2021-2026)"
    )

    # Atur x-axis agar hanya menampilkan tahun bulat (2021, 2022, ...)
    fig.update_xaxes(dtick=1)
    fig.update_layout(xaxis_title=None)

    return customize_fig(fig)

@capture("graph")
def make_volume_asset_bar(data_frame):
    # Mengelompokkan berdasarkan asset dan menghitung total volume
    df_agg = data_frame.groupby('asset_name', as_index=False)['volume'].sum()
    # Mengurutkan dari yang terbesar
    df_agg = df_agg.sort_values(by='volume', ascending=False)

    fig = raw_px.bar(
        df_agg, x="asset_name", y="volume", color="asset_name",
        color_discrete_sequence=BUSINESS_COLORS,
        text_auto=".2s",
        labels={"asset_name": "Aset Kripto", "volume": "Volume($)"},
        title="Total Volume Perdagangan Berdasarkan Aset Cryptocurrency"
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title=None,
        margin=dict(l=55, r=20, t=70, b=85),
    )
    fig.update_xaxes(tickfont=dict(size=12))

    return customize_fig(fig)

@capture("graph")
def make_volume_trend_line(data_frame):
    df_agg = data_frame.groupby('date', as_index=False)['volume'].sum()

    fig = raw_px.line(
        df_agg,
        x="date",
        y="volume",
        labels={"date": "Tanggal", "volume": "Volume($)"},
        title="Dinamika Tren Volume Perdagangan Bulanan Keseluruhan",
        markers=True
    )

    fig.update_xaxes(
        dtick="M6",
        tickformat="%b %Y",
        tickangle=0
    )

    fig.update_layout(
        margin=dict(l=55, r=20, t=70, b=100)
    )

    fig = customize_fig(fig)

    fig.update_traces(
        line=dict(color=BUSINESS_COLORS[1], width=2.5, shape="spline"),
        marker=dict(size=5, color=BUSINESS_COLORS[1]),
        fill="tozeroy",
        fillgradient=dict(
            type="vertical",
            colorscale=[(0, "rgba(37,99,235,0.35)"), (1, "rgba(37,99,235,0)")]
        ),
    )

    return fig

    return customize_fig(fig, is_area=True)

@capture("graph")
def make_volume_market_share(data_frame):
    # Kalkulasi  total volume per asset filter periode
    df_agg = data_frame.groupby('asset_name', as_index=False)['volume'].sum()

    fig = raw_px.pie(
        df_agg, values="volume", names="asset_name",
        color="asset_name",
        color_discrete_sequence=BUSINESS_COLORS,
        title="Pangsa Pasar Berdasarkan Volume Perdagangan",
        hole=0.4
    )

    fig.update_traces(textposition='auto', textinfo='percent', rotation=120, automargin=True,)
    fig.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5,
            font=dict(size=10)
        ),
        margin=dict(l=60, r=60, t=80, b=90)
    )
    return customize_fig(fig)

# ==========================================
# DATA LOADING & PREPROCESSING
# ==========================================
df = pd.read_csv("Global_Financial_Markets_Final.csv", sep=";")

# Convert date column
df["date"] = pd.to_datetime(df["tahun_bulan"], format="%Y-%m")

# Filter years 2021 - 2026
df["Tahun"] = df["date"].dt.year
df = df[(df["Tahun"] >= 2021) & (df["Tahun"] <= 2026)]

# Ensure proper chronological ordering for MoM calculations
df = df.sort_values(["asset_name", "date"]).reset_index(drop=True)



# ==========================================
# DASHBOARD PAGES BUILD
# ==========================================

# Default dashboard tampilan terbuka
default_assets = ["Bitcoin", "Ethereum"]
default_years = [2021, 2022, 2023, 2024, 2025, 2026]

page_volume = vm.Page(
    title="Volume Perdagangan",
    components=[
        vm.Figure(figure=custom_kpi_card(df, 'volume', agg_func='sum', title='Total Volume Perdagangan', value_type='currency')),
        vm.Figure(figure=custom_kpi_card(df, 'volume', agg_func='avg_monthly_volume', title='Volume Rata-rata Bulanan', value_type='currency')),
        vm.Figure(figure=custom_kpi_card(df, 'volume', agg_func='most_active_crypto', title='Crypto Volume Tertinggi', value_type='currency')),
        vm.Figure(figure=custom_kpi_card(df, 'volume', agg_func='most_active_month', title='Bulan Volume Tertinggi', value_type='text')),
        vm.Graph(figure=make_volume_monthly_bar(df)),
        vm.Graph(figure=make_volume_asset_bar(df)),
        vm.Graph(figure=make_volume_trend_line(df)),
        vm.Graph(figure=make_volume_market_share(df))
    ],
    controls=[
        vm.Filter(
            column="asset_name",
            selector=vm.Dropdown(multi=True, title="Pilih Cryptocurrency", value=default_assets)
        ),
        vm.Filter(
            column="Tahun",
            selector=vm.Dropdown(multi=True, title="Pilih Tahun", value=default_years)
        )
    ],
    layout=vm.Grid(
        grid=[
            [0, 1, 2, 3],
            [4, 4, 7, 7],
            [5, 5, 7, 7],
            [6, 6, 6, 6]
        ],
        row_min_height="140px",
        row_gap="0px",
        col_gap="0px"
    )
)

# ==========================================
# RUN DASHBOARD
# ==========================================
dashboard = vm.Dashboard(
    title="Dashboard Aktivitas dan Dinamika Volume Aset Keuangan Global",
    pages=[page_volume]
)

dashboard = Vizro().build()

server = dashboard.server

if __name__ == "__main__":
    dashboard.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050))
    )

