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

if ilce_option != 'Urla':
    st.write(f"Şu anda {ilce_option}")


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


semt_mahalle= df['semt_mahalle'].unique()
semt = st.selectbox('SEMT/MAHALLE SEÇİNİZ', semt_mahalle)
konut_ = df.loc[df['semt_mahalle'] == semt, 'Konut_tipi'].unique()
konut2 = st.selectbox('KONUT TİPİNİ SEÇİNİZ', konut_)


df1 = df.loc[((df['semt_mahalle'] == semt) & (df['Konut_tipi'] == konut2)), ['oda_sayisi','brut_m2','Ay', 'fiyat']]


oda_filtre = st.selectbox("Oda Sayısı Seçin", sorted(df1['oda_sayisi'].unique()))

df1['fiyat'] = df1['fiyat'].astype(int)
df1['brut_m2'] = df1['brut_m2'].astype(float)




if oda_filtre:
    df1 = df1[df1['oda_sayisi']==oda_filtre]
    st.subheader(f"Seçtiğiniz {oda_filtre} 'de:")

    st.write(f"Toplam {df1.shape[0]} tane ilan bulunuyor")
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

    df1['fiyat'] = df1['fiyat'].astype(int)
    df1['brut_m2'] = df1['brut_m2'].astype(float)

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

df = df.loc[((df['semt_mahalle'] == semt) & (df['Konut_tipi'] == konut2)), ['oda_sayisi','brut_m2','Ay', 'fiyat']]

df['fiyat'] = df['fiyat'].astype(float)
df['brut_m2'] = df['brut_m2'].astype(float)

oda = df.groupby("oda_sayisi").agg({'fiyat': 'median','brut_m2':'mean','Ay':'count'}).reset_index().rename(columns={'Ay':'Sayı','brut_m2':'ort_brut_m2'})
oda['m2/TL'] = oda['fiyat'] / oda['ort_brut_m2']
oda['m2/TL'] = oda['m2/TL'].apply(lambda x: format_decimal(x,locale='tr_TR'))
oda_sayi = df.groupby("oda_sayisi").agg({'fiyat': ['median','count']})['fiyat'].rename(columns={'median':'Ortalama','count':'sayı'})
tarih = df.groupby("Ay").agg({'fiyat':'median'}).reset_index()
tarih2 = df.groupby("Ay").agg({'fiyat':['median','count']}).reset_index()['fiyat'].rename(columns={'median':'Ortalama','count':'sayı'})


st.write("________________________________________________________")
st.title("Ev Tipine Göre Ortalama Fiyatlar")
fig, ax = plt.subplots(figsize=(12, 5))
sns.barplot(data=oda.sort_values(by='fiyat',ascending=False), x='oda_sayisi', y='fiyat', ax=ax,palette='coolwarm')
ax.set_xticklabels(ax.get_xticklabels(), rotation=90, ha='right')
ax.set_title("Oda Sayısına Göre Ortalama Fiyatlar")
ax.set_xlabel("Oda Sayısı")
ax.set_ylabel("Ortalama Fiyat (TL)")

st.pyplot(fig)

st.write(f"Bölgede Toplam {df.shape[0]} tane ilan bulunuyor")
st.markdown(
    "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>En uygun fiyat</span>"
    f"<b> {format_decimal(df['fiyat'].min(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
    "</h6>",
    unsafe_allow_html=True
)
st.markdown(
    "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>En pahalı fiyat</span>"
    f"<b> {format_decimal(df['fiyat'].max(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
    "</h6>",
    unsafe_allow_html=True
)
st.markdown(
    "<h6 style='text-align: left; color: #3366cc;' ><span style='color: white;'>Ortalama fiyat</span>"
    f"<b> {format_decimal(df['fiyat'].median(), locale='tr_TR')} TL </b> <span style='color: white;'></span>"
    "</h6>",
    unsafe_allow_html=True
)
dfx = df.groupby('oda_sayisi').agg({'fiyat':['mean','count','min','max']})['fiyat'].rename(columns={'mean':'Ortalama_fiyat','count':'Adet'})
dfx['Ortalama_fiyat'] =  dfx['Ortalama_fiyat'].apply(lambda x:format_decimal(x,locale='tr_TR'))
dfx['min'] = dfx['min'].apply(lambda x:format_decimal(x,locale='tr_TR'))
dfx['max'] = dfx['max'].apply(lambda x:format_decimal(x,locale='tr_TR'))

st.write(dfx)

st.title("Ay'a Göre Ortalama Ev  Fiyatları")

tarih = df.groupby("Ay").agg({'fiyat':'median'}).reset_index()
tarih2 = df.groupby("Ay").agg({'fiyat':['median','count']})['fiyat'].rename(columns={'median':'Ortalama_fiyat','count':'sayı'})
tarih2['Ortalama_fiyat'] =  tarih2['Ortalama_fiyat'].apply(lambda x:format_decimal(x,locale='tr_TR'))
fig3, ax3 = plt.subplots(figsize=(12, 5))
sns.barplot(data=tarih, x='Ay', y='fiyat', ax=ax3,palette='coolwarm')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=90, ha='right')
ax2.set_title("Tarihe Göre Ortalama Fiyatlar")
ax2.set_xlabel("Ay")
ax2.set_ylabel("Ortalama Fiyat (TL)")

st.pyplot(fig3)
st.write(tarih2)