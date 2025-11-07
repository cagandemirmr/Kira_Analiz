import time

import pandas as pd
import streamlit as st
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from babel.numbers import format_decimal
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


st.title('Emlak Veri Analizi(DEMO)')

ilce = ["Urla","Güzelbahçe(Mevcut değil)","Çeşme(Mevcut değil)"]
konut_tipi =["Satılık","Kiralık","Arsa"]

ilce_option = st.selectbox("İLÇE",ilce)

konut = st.selectbox("KONUT TİPİ",konut_tipi)


if konut == 'Kiralık':
    conn = sqlite3.connect("Completed_db.db")
    df = pd.read_sql(f"SELECT * FROM tum_ilanlar WHERE semt_mahalle IS '{ilce_option}' AND Konut = '{konut}'", conn)
    df = df.copy()
    conn.close()
    time.sleep(2)
else:
    conn = sqlite3.connect("Completed_db.db")
    df = pd.read_sql(f"SELECT * FROM tum_ilanlar WHERE ilce IS '{ilce_option}' AND Konut = '{konut}'", conn)
    df = df.copy()
    conn.close()
    time.sleep(2)

st.write(f"Aramanızla ilgili olarak {df.shape[0]} {konut} ilan bulundu ")
st.write("________________________________________________________")
semt_mahalle= df['semt_mahalle'].unique()
semt = st.selectbox('SEMT/MAHALLE SEÇİNİZ', semt_mahalle)
konut_ = df.loc[df['semt_mahalle'] == semt, 'Konut_tipi'].unique()
konut2 = st.selectbox('KONUT TİPİNİ SEÇİNİZ', konut_)

st.write("________________________________________________________")
df1 = df.loc[((df['semt_mahalle'] == semt) & (df['Konut_tipi'] == konut2)), ['oda_sayisi','brut_m2','Ay', 'fiyat']]
st.markdown(
    f"<h6 style='text-align: left; color: red;'>"
    f"<b>{df1.shape[0]}</b> <span style='color: white;'>sayıda ilan bulunmuştur.</span>"
    "</h6>",
    unsafe_allow_html=True
)
st.markdown(
    "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>En uygun fiyatlı ilan:</span>" 
    f"<b> {format_decimal(df1['fiyat'].min(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
    "</h6>",
    unsafe_allow_html=True
)
st.markdown(
    "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>En pahalı ilan:</span>" 
    f"<b> {format_decimal(df1['fiyat'].max(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
    "</h6>",
    unsafe_allow_html=True
)
st.markdown(
    "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>Ortalama fiyat:</span>" 
    f"<b> {format_decimal(df1['fiyat'].mean(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
    "</h6>",
    unsafe_allow_html=True
)

df1['fiyat_TL'] = df1['fiyat'].apply(lambda x: format_decimal(x,locale='tr_TR'))
df1['m2_fiyat'] = (df1['fiyat'] / (df1['brut_m2'].astype(float))).apply(lambda x: format_decimal(x,locale='tr_TR'))
st.write(df1.loc[:,['Ay','oda_sayisi','brut_m2','fiyat_TL','m2_fiyat']])

df1['brut_m2'] = df1['brut_m2'].astype(float)


oda = df1.groupby("oda_sayisi").agg({'fiyat': 'median','brut_m2':'mean','Ay':'count'}).reset_index().rename(columns={'Ay':'Sayı','brut_m2':'ort_brut_m2'})
oda['m2/TL'] = oda['fiyat'] / oda['ort_brut_m2']
oda['m2/TL'] = oda['m2/TL'].apply(lambda x: format_decimal(x,locale='tr_TR'))
oda_sayi = df1.groupby("oda_sayisi").agg({'fiyat': ['median','count']})['fiyat'].rename(columns={'median':'Ortalama','count':'sayı'})
tarih = df1.groupby("Ay").agg({'fiyat':'median'}).reset_index()
tarih2 = df1.groupby("Ay").agg({'fiyat':['median','count']}).reset_index()['fiyat'].rename(columns={'median':'Ortalama','count':'sayı'})

st.title("Ev Tipine Göre Ortalama Fiyatlar")
fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(data=oda.sort_values(by='fiyat',ascending=False), x='oda_sayisi', y='fiyat', ax=ax,palette='coolwarm')
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='right')
ax.set_title("Oda Sayısına Göre Ortalama Fiyatlar")
ax.set_xlabel("Oda Sayısı")
ax.set_ylabel("Ortalama Fiyat (TL)")



'''for p in ax.patches:
    ax.annotate(f"{p.get_height():,.0f} TL",
                (p.get_x() + p.get_width() / 2, p.get_height()),
                ha='center', va='bottom', fontsize=10, color='black')'''
st.pyplot(fig)

oda_filtre = st.multiselect("Oda Sayısı Seçin", sorted(df1['oda_sayisi'].unique()))





oda['fiyat'] = oda['fiyat'].apply(lambda x: format_decimal(x,locale='tr_TR'))

st.write(oda)


if oda_filtre:
    df1 = df1[df1['oda_sayisi'].isin(oda_filtre)]
    st.subheader(f"Seçtiğiniz {oda_filtre[0]} 'de:")
    st.markdown(
        "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>En uygun fiyat</span>"
        f"<b> {format_decimal(df1['fiyat'].min(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
        "</h6>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>En pahalı fiyat</span>"
        f"<b> {format_decimal(df1['fiyat'].max(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
        "</h6>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>Ortalama fiyat</span>"
        f"<b> {format_decimal(df1['fiyat'].median(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
        "</h6>",
        unsafe_allow_html=True
    )
    
    df1['m2/TL'] = df1['fiyat'] / df1['brut_m2']
    df1['m2/TL'] = df1['m2/TL'].apply(lambda x: format_decimal(x,locale='tr_TR'))
    df1['fiyat_TL'] = df1['fiyat'].apply(lambda x: format_decimal(x, locale='tr_TR'))
    df1 = df1.reset_index()
    st.write(df1.loc[:,['brut_m2','fiyat_TL','m2/TL']])



st.title("Ay'a Göre Ortalama Fiyatlar")

tarih = df1.groupby("Ay").agg({'fiyat':'median'}).reset_index()
tarih2 = df1.groupby("Ay").agg({'fiyat':['median','count']})['fiyat'].rename(columns={'median':'Ortalama_fiyat','count':'sayı'})
tarih2['Ortalama_fiyat'] =  tarih2['Ortalama_fiyat'].apply(lambda x:format_decimal(x,locale='tr_TR'))
fig2, ax2 = plt.subplots(figsize=(12, 5))
sns.barplot(data=tarih, x='Ay', y='fiyat', ax=ax2,palette='coolwarm')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90, ha='right')
ax2.set_title("Tarihe Göre Ortalama Fiyatlar")
ax2.set_xlabel("Ay")
ax2.set_ylabel("Ortalama Fiyat (TL)")

st.pyplot(fig2)
st.write(tarih2)

