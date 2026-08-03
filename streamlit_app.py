
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Control Tower ST", page_icon="📦", layout="wide")

st.markdown('''
<style>
.stApp {background:#F5F6F8;}
[data-testid="stSidebar"] {background:#111827;}
[data-testid="stSidebar"] * {color:white;}
.brand{background:#FF0054;color:white;padding:14px 16px;border-radius:10px;font-weight:800;font-size:20px;margin-bottom:14px;}
.kpi{background:white;border:1px solid #E4E6EB;border-radius:12px;padding:16px;min-height:120px;}
.label{color:#70737C;font-size:12px;font-weight:600;}
.value{color:#25262B;font-size:27px;font-weight:800;margin-top:6px;}
.delta-up{color:#16A765;font-size:12px;font-weight:700;margin-top:8px;}
.delta-down{color:#D93025;font-size:12px;font-weight:700;margin-top:8px;}
.title{font-size:28px;font-weight:800;color:#25262B;}
.subtitle{color:#70737C;margin-bottom:18px;}
</style>
''', unsafe_allow_html=True)

@st.cache_data
def demo_data():
    rng=np.random.default_rng(7)
    rows=[]
    for d in pd.date_range("2026-07-01","2026-07-31"):
        for cd in ["EXO","Patagonia","Argentina Refrigerados"]:
            created=int(rng.integers(90,210))
            completed=int(created*rng.uniform(.78,.95))
            canceled=int(created*rng.uniform(.04,.11))
            rows.append({
                "date":d.date(),"cd":cd,"st_created":created,"st_completed":completed,
                "st_canceled":canceled,"st_delayed":max(created-completed-canceled,0),
                "fill_rate_prep":rng.uniform(.86,.94),"fill_rate_rec":rng.uniform(.965,.995),
                "on_time":rng.uniform(.86,.96),"wis":rng.uniform(.04,.09),
                "lost_sales":rng.uniform(1_500_000,4_500_000)
            })
    df=pd.DataFrame(rows)
    df["fill_rate_final"]=df["fill_rate_prep"]*df["fill_rate_rec"]
    return df

df=demo_data()

with st.sidebar:
    st.markdown('<div class="brand">PedidosYa<br><span style="font-size:14px">Control Tower ST</span></div>', unsafe_allow_html=True)
    page=st.radio("Navegación",["01 | Resumen Ejecutivo","02 | Operación ST","03 | Loss Tree & WIS","04 | Análisis Detallado"],label_visibility="collapsed")
    st.divider()
    st.caption("Versión demo con datos simulados")

f1,f2,f3,f4=st.columns([1.2,2,1.2,1.2])
with f1:
    cds=st.multiselect("CD",sorted(df.cd.unique()),default=sorted(df.cd.unique()))
with f2:
    dates=st.date_input("Fecha",value=(df.date.min(),df.date.max()),min_value=df.date.min(),max_value=df.date.max())
with f3:
    st.selectbox("Estado ST",["Todos","COMPLETED","CONFIRMING","TRANSFERRING","CANCELED"])
with f4:
    st.selectbox("Cumplimiento",["Todos","ON TIME","FUERA DE TIEMPO","CANCELADA"])

if isinstance(dates, tuple) and len(dates)==2:
    start,end=dates
else:
    start,end=df.date.min(),df.date.max()

filtered=df[df.cd.isin(cds)&(df.date>=start)&(df.date<=end)].copy()

def wavg(col):
    if filtered.empty or filtered.st_created.sum()==0: return 0
    return np.average(filtered[col],weights=filtered.st_created)

def pct(x): return f"{x*100:,.2f}%".replace(",", "X").replace(".", ",").replace("X",".")
def num(x): return f"{int(round(x)):,}".replace(",",".")
def money(x): return "$ "+f"{x/1_000_000:,.2f} M".replace(",", "X").replace(".", ",").replace("X",".")

def kpi(label,value,delta=None,good=True):
    d=""
    if delta:
        d=f'<div class="{"delta-up" if good else "delta-down"}">{"▲" if good else "▼"} {delta}</div>'
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div>{d}</div>',unsafe_allow_html=True)

if page=="01 | Resumen Ejecutivo":
    st.markdown('<div class="title">01 | Resumen Ejecutivo</div><div class="subtitle">Visión consolidada de los centros de distribución.</div>',unsafe_allow_html=True)
    cols=st.columns(6)
    vals=[
        ("Fill Rate Preparación",pct(wavg("fill_rate_prep")),"+2,91 pp",True),
        ("Fill Rate Recepción",pct(wavg("fill_rate_rec")),"+1,32 pp",True),
        ("Fill Rate Final",pct(wavg("fill_rate_final")),"+2,14 pp",True),
        ("On Time",pct(wavg("on_time")),"+3,25 pp",True),
        ("ST Creadas",num(filtered.st_created.sum()),"+18,6%",True),
        ("ST Canceladas",num(filtered.st_canceled.sum()),"-7,4%",True),
    ]
    for c,v in zip(cols,vals):
        with c:kpi(*v)
    left,right=st.columns([1.55,1])
    daily=filtered.groupby("date",as_index=False).agg({"fill_rate_prep":"mean","fill_rate_rec":"mean","fill_rate_final":"mean"})
    with left:
        long=daily.melt("date",var_name="Métrica",value_name="Valor")
        fig=px.line(long,x="date",y="Valor",color="Métrica")
        fig.update_yaxes(tickformat=".0%",title=None); fig.update_xaxes(title=None)
        fig.update_layout(height=340,margin=dict(l=10,r=10,t=25,b=10))
        st.plotly_chart(fig,use_container_width=True)
    with right:
        total=filtered.st_created.sum()
        values={"COMPLETED":filtered.st_completed.sum(),"CANCELED":filtered.st_canceled.sum(),"DEMORADAS":filtered.st_delayed.sum()}
        values["EN PROCESO"]=max(total-sum(values.values()),0)
        pie=pd.DataFrame({"Estado":values.keys(),"ST":values.values()})
        fig=px.pie(pie,names="Estado",values="ST",hole=.62)
        fig.update_layout(height=340,margin=dict(l=10,r=10,t=25,b=10))
        st.plotly_chart(fig,use_container_width=True)
    c1,c2=st.columns(2)
    with c1:
        st.subheader("Top 5 SKU con mayor quiebre")
        st.dataframe(pd.DataFrame({"SKU":["PV3PJH","53ES98","52CFL8","17319762","0ZMYH6"],"Descripción":["Queso Cremoso La Paulina","Palta Hass Selección","Jabón Dove 90 g","Hamburguesas Paty","Banana Premium Ecuador"],"Quiebre":[1355,1355,1147,1099,1045]}),use_container_width=True,hide_index=True)
    with c2:
        st.subheader("Top 5 tiendas con mayor pérdida")
        st.dataframe(pd.DataFrame({"Tienda":["AR_182_Munro","AR_210_Neuquen_Este","AR_507_Villa_Crespo","AR_10_La Plata","AR_517_Santa_Fe_II"],"Lost Sales":[5879.85,2772.46,2131.90,1986.11,1982.00]}),use_container_width=True,hide_index=True)

elif page=="02 | Operación ST":
    st.markdown('<div class="title">02 | Operación Store Transfers (ST)</div><div class="subtitle">Seguimiento operativo de creación, cumplimiento y demoras.</div>',unsafe_allow_html=True)
    cols=st.columns(6)
    vals=[
        ("ST Creadas",num(filtered.st_created.sum()),"+18,6%",True),
        ("ST Completadas",num(filtered.st_completed.sum()),"+20,3%",True),
        ("ST Demoradas",num(filtered.st_delayed.sum()),"+6,7%",False),
        ("On Time",pct(wavg("on_time")),"+3,25 pp",True),
        ("ST Canceladas",num(filtered.st_canceled.sum()),"-7,4%",True),
        ("Prom. Demora","12,6 h","-1,8 h",True),
    ]
    for c,v in zip(cols,vals):
        with c:kpi(*v)
    left,right=st.columns(2)
    daily=filtered.groupby("date",as_index=False).agg(st_created=("st_created","sum"))
    with left:
        fig=px.area(daily,x="date",y="st_created"); fig.update_layout(height=340)
        st.plotly_chart(fig,use_container_width=True)
    with right:
        cd=filtered.groupby("cd",as_index=False).agg(st_delayed=("st_delayed","sum")).sort_values("st_delayed")
        fig=px.bar(cd,x="st_delayed",y="cd",orientation="h"); fig.update_layout(height=340)
        st.plotly_chart(fig,use_container_width=True)

elif page=="03 | Loss Tree & WIS":
    st.markdown('<div class="title">03 | Loss Tree & WIS</div><div class="subtitle">Disponibilidad, ventas potenciales perdidas y causas raíz.</div>',unsafe_allow_html=True)
    cols=st.columns(5)
    vals=[
        ("WIS",pct(wavg("wis")),"-0,42 pp",False),
        ("Unidades con quiebre",num(412585),"+8,7%",False),
        ("Ventas potenciales perdidas",money(filtered.lost_sales.sum()),"+9,1%",False),
        ("Día con mayor pérdida","29/07/2026","$ 142 M",False),
        ("CD con mayor pérdida","Patagonia","$ 1.124 M",False),
    ]
    for c,v in zip(cols,vals):
        with c:kpi(*v)
    a,b,c=st.columns(3)
    daily=filtered.groupby("date",as_index=False).agg(WIS=("wis","mean"))
    with a:
        fig=px.line(daily,x="date",y="WIS",markers=True); fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig,use_container_width=True)
    with b:
        cd=filtered.groupby("cd",as_index=False).agg(WIS=("wis","mean"))
        fig=px.bar(cd,x="cd",y="WIS",text_auto=".1%"); fig.update_yaxes(tickformat=".0%")
        st.plotly_chart(fig,use_container_width=True)
    with c:
        lt=pd.DataFrame({"Causa":["Peya Issues","Supplier + P&N Issues","Other Issues"],"Lost Sales":[53777.91,33205.05,2957.70]})
        fig=px.bar(lt.sort_values("Lost Sales"),x="Lost Sales",y="Causa",orientation="h")
        st.plotly_chart(fig,use_container_width=True)

else:
    st.markdown('<div class="title">04 | Análisis Detallado de ST</div><div class="subtitle">Búsqueda, detalle y exportación de transferencias.</div>',unsafe_allow_html=True)
    search=st.text_input("Buscar ST / ID / SKU / Tienda")
    cols=st.columns(7)
    vals=[
        ("ST seleccionadas",num(filtered.st_created.sum()),None,True),
        ("Unidades solicitadas",num(823586),None,True),
        ("Unidades pickeadas",num(734221),None,True),
        ("Unidades recibidas",num(722854),None,True),
        ("FR Preparación",pct(wavg("fill_rate_prep")),None,True),
        ("FR Recepción",pct(wavg("fill_rate_rec")),None,True),
        ("On Time",pct(wavg("on_time")),None,True),
    ]
    for c,v in zip(cols,vals):
        with c:kpi(*v)
    rng=np.random.default_rng(3)
    detail=pd.DataFrame({
        "Transfer ID":[f"ST{620000+i}" for i in range(1,31)],
        "Fecha creación":pd.date_range("2026-07-20",periods=30,freq="8h"),
        "CD origen":np.resize(["EXO","Patagonia","Argentina Refrigerados"],30),
        "Tienda destino":np.resize(["AR_182_Munro","AR_210_Neuquen_Este","AR_507_Villa_Crespo"],30),
        "Estado ST":np.resize(["COMPLETED","CONFIRMING","TRANSFERRING","CANCELED"],30),
        "Solicitado":rng.integers(40,220,30),
        "Pickeado":rng.integers(0,210,30),
        "Recibido":rng.integers(0,200,30),
    })
    if search:
        mask=detail.astype(str).apply(lambda s:s.str.contains(search,case=False,na=False)).any(axis=1)
        detail=detail[mask]
    st.dataframe(detail,use_container_width=True,hide_index=True,height=420)
    st.download_button("Exportar CSV",detail.to_csv(index=False).encode("utf-8-sig"),"detalle_st.csv","text/csv")
