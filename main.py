import pandas as pd
from datetime import datetime as dt
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap
import geopandas
import streamlit as st



hide_menu = """
<style>
#MainMenu{
    visibility:hidden;
}
footer{
    visibility:visible;
}
    footer:after{
    content:'Copyright @ 2023: Kelompok Streamlit IF4';
    display:block;
    position:relative;
    color:tomato;
    padding:5px
    top:3px
}

</style>
"""

def get_gempa_data():
    #location = r'D:\My-docs\Kampus\materi kuliah\Semester 3\Pemrograman Dasar Sains Data\UAS\Tugas Besar\Data'
    location = r'\Data'
    data = '\katalog_gempa.csv'

    df=pd.read_csv(f'{location}{data}')
    df = df.rename(columns={'tgl':'tanggal','ot':'waktu','lat':'latitude','lon':'longitude','depth':'kedalaman','mag':'magnitude','remark':'lokasi'})
    df = df.drop(['dip1','strike1','dip1','rake1','strike2','dip2','rake2'], axis=1)

    df['tanggal'] = pd.to_datetime(df['tanggal'], format='%Y-%m-%d')
    df['bulan'] = df['tanggal'].dt.month
    tempList = []
    for i in df['bulan'].tolist():
        tempVar = 0
        if (i < 4):
            tempVar = 1
        elif (i < 7):
            tempVar = 2
        elif (i < 10):
            tempVar = 3
        else:
            tempVar = 4
        tempList.append(tempVar)
    df['quarter'] = tempList
    df['tahun'] = df['tanggal'].dt.year

    df['waktu'] = pd.Series(df['waktu'], dtype="string")
    df['waktu'] = df['waktu'].str.slice(0, 8)
    bantu = pd.to_datetime(df['waktu'], format='%H:%M:%S')
    df['jam'] = bantu.dt.hour
    df['menit'] = bantu.dt.minute

    listBantu = []
    for i in bantu.dt.hour:
        varBantu = ''
        if (i < 3):
            varBantu = 'Dini Hari'
        elif (i < 6):
            varBantu = 'Subuh'
        elif (i < 12):
            varBantu = 'Pagi'
        elif (i < 18):
            varBantu = 'Sore'
        else:
            varBantu = 'Malam'
        listBantu.append(varBantu)
    df['dayperiod'] = listBantu

    listBantu = []
    for i in df['magnitude']:
        varBantu = ''
        if (i < 3):
            varBantu = 'Micro'
        elif (i < 4):
            varBantu = 'Minor'
        elif (i < 5):
            varBantu = 'Ringan'
        elif (i < 6):
            varBantu = 'Sedang'
        elif (i < 7):
            varBantu = 'Kuat'
        elif (i < 8):
            varBantu = 'Mayor'
        else:
            varBantu = 'Sangat kuat'
        listBantu.append(varBantu)
    df['kategori gempa'] = listBantu

    listBantu = []
    for i in df['bulan'].tolist():
        varBantu = ''
        if ((i > 3) & (i < 11)):
            varBantu = 'Kemarau'
        else:
            varBantu = 'Hujan'
        listBantu.append(varBantu)
    df['musim'] = listBantu

    listBantu = []
    for i in df['kedalaman'].tolist():
        varBantu = ''
        if (i < 60):
            varBantu = 'Dangkal'
        elif (i < 300):
            varBantu = 'Menengah'
        else:
            varBantu = 'Dalam'
        listBantu.append(varBantu)
    df['kategori kedalaman'] = listBantu
    return df

def bantu(data):
    bantuvar = data
    return list(data.lokasi.unique())







st.set_page_config(layout="wide")
st.markdown(hide_menu,unsafe_allow_html=True)










data = get_gempa_data()
st.title('Lokasi Gempa di Indonesia')



st.sidebar.title('Filter')

try:
    dts = st.sidebar.date_input(label='Rentang waktu: ',
                value=(dt(year=2008, month=11, day=1, hour=0, minute=0),
                        dt(year=2022, month=10, day=31, hour=0, minute=0)),
                min_value=dt(year=2008,month=11, day=1, hour=0, minute=0),
                max_value=dt(year=2022,month=10, day=31, hour=0, minute=0),
                key='#date_range',
                help="The start and end date time")
    if not dts:
        data = data
        dts = ''
    else:
        data = data[data['tanggal'].isin(pd.date_range(start=dts[0], end=dts[1], inclusive="both"))]
except:
    pass

try:
    countries = st.sidebar.multiselect('Pilih provinsi', list(data.lokasi.unique()))
    if not countries:
        countries = ''
        data = data


    else:
        data = data[data['lokasi'].isin(countries)]
        countries = f"Countries: {', '.join(countries)}"

except:
    st.sidebar.warning('error')

try:
    dyp = st.sidebar.multiselect('Sesi waktu', list(data['dayperiod'].unique()))
    if not dyp:
        data = data
        dyp = ''
    else:
        data = data[data['dayperiod'].isin(dyp)]
        dyp = f"Periode: {', '.join(dyp)}"
except:
    pass


try:
    ktg = st.sidebar.multiselect('Tingkat kekuatan',list(data['kategori gempa'].unique()))
    if not ktg:
        data = data
        ktg = ''
    else:
        data = data[data['kategori gempa'].isin(ktg)]
        ktg = f"kategori gempa: {', '.join(ktg)}"
except:
    pass

try:
    kdm = st.sidebar.multiselect('Kedalaman',list(data['kategori kedalaman'].unique()))
    if not kdm:
        data = data
        kdm = ''
    else:
        data = data[data['kategori kedalaman'].isin(kdm)]
        kdm = f"kategori kedalaman: {', '.join(kdm)}"
except:
    pass
try:
    st.info(f'''
    {countries}\n
    {dyp}\n
    {ktg}\n
    {kdm}\n
    Rentang waktu: [{dts[0]}] - [{dts[1]}]
    ''')
except:
    pass
# add Geopandas

geometry = geopandas.points_from_xy(data.longitude, data.latitude)
geo_df = geopandas.GeoDataFrame(
    data[["latitude", "longitude","kedalaman","magnitude","lokasi","bulan",
        "quarter","tahun","jam","dayperiod","kategori gempa","musim","kategori kedalaman"]], geometry=geometry
)





#maps
def mapsHeat(information):
    koordinat = ['0.7893', '113.9213']
    maps = folium.Map(location=koordinat, tiles="Cartodb dark_matter", zoom_start=5)
    heat_data = [[point.xy[1][0], point.xy[0][0]] for point in geo_df.geometry]
    HeatMap(heat_data).add_to(maps)
    for i in range(0, len(inner_join_df)):
        koordinat = inner_join_df.iloc[i, [2, 3]]
        information = inner_join_df.iloc[i, [0, 1]]
        if (inner_join_df.Magnitude_tertinggi[i] < 3):
            varBantu ='lightgray'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)
        elif (inner_join_df.Magnitude_tertinggi[i] < 4):
            varBantu ='lightgreen'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)
        elif (inner_join_df.Magnitude_tertinggi[i] < 5):
            varBantu ='green'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)
        elif (inner_join_df.Magnitude_tertinggi[i] < 6):
            varBantu ='blue'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)
        elif (inner_join_df.Magnitude_tertinggi[i] < 7):
            varBantu ='darkblue'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)
        elif (inner_join_df.Magnitude_tertinggi[i] < 8):
            varBantu ='red'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)
        else:
            varBantu ='darkred'
            folium.Marker(koordinat, popup=information, icon=folium.Icon(color=varBantu)).add_to(maps)

    return st_folium(maps, width=725, height=300)





#table
st.empty()
#metric
datas = data.copy()
lokasi = list(datas['lokasi'].unique())
bantu =  list(datas['lokasi'].values)
dictBantu = {}
for s in bantu:
    if s in dictBantu:
        dictBantu[s] += 1
    else:
        dictBantu[s] = 1


df_gempa = pd.DataFrame.from_dict(dictBantu, orient='index')
df_gempa = df_gempa.reset_index()
df_gempa = df_gempa.rename(columns = {'index':'lokasi',0:'total gempa'})

df_gempas = data.pivot_table(index = 'lokasi')
df_gempas = df_gempas[['latitude','longitude']]
df_gempas = df_gempas.reset_index()
inner_join_df= pd.merge(df_gempa, df_gempas, on='lokasi', how='inner')
maxs = {}
mins = {}
for magnitude_lokasi in datas['lokasi'].unique():
    maxs[magnitude_lokasi] = datas[datas['lokasi'].isin([magnitude_lokasi])]['magnitude'].max()
    mins[magnitude_lokasi] = datas[datas['lokasi'].isin([magnitude_lokasi])]['magnitude'].min()



maxs = pd.DataFrame.from_dict(maxs, orient='index').reset_index()
maxs = maxs.rename(columns = {'index':'lokasi',0:'Magnitude_tertinggi'})
mins = pd.DataFrame.from_dict(mins, orient='index').reset_index()
mins = mins.rename(columns = {'index':'lokasi',0:'Magnitude_terendah'})

inner_join_df =pd.merge(inner_join_df,maxs, on='lokasi', how='inner')
inner_join_df =pd.merge(inner_join_df,mins, on='lokasi', how='inner')


col1, col2= st.columns(2)

with col1:

#plotting
    try:
        columns = st.selectbox('Pilih Kategori',['dayperiod','kategori gempa','musim','kategori kedalaman'],index=0)
        if not columns:
            data = data
            columns = ''
        else:
            if columns == 'dayperiod':
                st.bar_chart(data = data[columns].value_counts().rename_axis('sesi waktu').reset_index(name='jumlah'),x = 'sesi waktu',y = 'jumlah')
            elif columns == 'kategori gempa':
                st.bar_chart(data=data[columns].value_counts().rename_axis('tingkat kekuatan').reset_index(name='jumlah'),
                             x='tingkat kekuatan', y='jumlah')
            elif columns == 'musim':
                st.bar_chart(data=data[columns].value_counts().rename_axis('musim').reset_index(name='jumlah'),
                             x='musim', y='jumlah')
            else:
                st.bar_chart(data=data[columns].value_counts().rename_axis('tingkat kedalaman').reset_index(name='jumlah'),
                             x='tingkat kedalaman', y='jumlah')

    except:
        pass
with col2:
    try:
        columns = st.selectbox('Choose',['tahun','quarter','bulan','latitude','longitude','kedalaman','magnitude'],index=0)
        if not columns:
            data = data
            columns = ''
        else:
            if columns == 'tahun':
                st.bar_chart(data=data[columns].value_counts().rename_axis('tahun').reset_index(name='jumlah'),x='tahun', y='jumlah')
            elif columns == 'quarter':
                st.bar_chart(data=data[columns].value_counts().rename_axis('kuartal').reset_index(name='jumlah'),x='kuartal', y='jumlah')
            elif columns == 'bulan':
                st.bar_chart(data=data[columns].value_counts().rename_axis('bulan').reset_index(name='jumlah'),x='bulan', y='jumlah')
            elif columns == 'latitude':
                st.bar_chart(data=data[columns].value_counts().rename_axis('latitude').reset_index(name='jumlah'),x='latitude', y='jumlah')
            elif columns == 'longitude':
                st.bar_chart(data=data[columns].value_counts().rename_axis('longitude').reset_index(name='jumlah'),x='longitude', y='jumlah')
            elif columns == 'kedalaman':
                st.bar_chart(data=data[columns].value_counts().rename_axis('kedalaman').reset_index(name='jumlah'),x='kedalaman', y='jumlah')
            else:
                st.bar_chart(data = data[columns].value_counts().rename_axis('kekuatan').reset_index(name='jumlah'),x = 'kekuatan',y = 'jumlah')
    except:
        pass

st.dataframe(data)
col1, col2, col3= st.columns(3)

with col1:
    st.subheader('Kejadian')
    st.metric("Sebanyak",sum(list(inner_join_df['total gempa'])))
with col2:
    st.subheader('Paling jarang')
    st.metric(inner_join_df['lokasi'][inner_join_df['total gempa'].idxmin()],
              inner_join_df['total gempa'][inner_join_df['total gempa'].idxmin()])
with col3:
    st.subheader('Paling sering')
    st.metric(inner_join_df['lokasi'][inner_join_df['total gempa'].idxmax()],
              inner_join_df['total gempa'][inner_join_df['total gempa'].idxmax()])

col1, col2= st.columns(2)

with col1:
    st.subheader('Magnitude Tertinggi')
    st.metric(inner_join_df['lokasi'][inner_join_df['Magnitude_tertinggi'].idxmax()],
              inner_join_df['Magnitude_tertinggi'][inner_join_df['Magnitude_tertinggi'].idxmax()])
with col2:
    st.subheader('Magnitude Terendah')
    st.metric(inner_join_df['lokasi'][inner_join_df['Magnitude_terendah'].idxmin()],
              inner_join_df['Magnitude_terendah'][inner_join_df['Magnitude_terendah'].idxmin()])

st.dataframe(inner_join_df)
st.subheader('Heatmap')
mapsHeat(inner_join_df)




















