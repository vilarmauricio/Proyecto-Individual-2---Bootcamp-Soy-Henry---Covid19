import streamlit as st
import pandas as pd
import datetime as dt
import numpy as np
import plotly.express as px


#Descarga de archivo

#from sodapy import Socrata
#client = Socrata("healthdata.gov", None)
#results = client.get("g62h-syeh", limit=50000)

# Convert to pandas DataFrame
#resultados_df = pd.DataFrame.from_records(results)
#Guardamos archivo
#resultados_df.to_csv('./dataset/data_covid.csv')

df = pd.read_csv('./dataset/data_covid.csv')
#df.head()
# Convertimos fechas en datetime
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')

# Seleccionamos columnas que vemos mas relevantes para el informe
selecc_col_dic = {   'state' : 'Estado', # Estado 
                 'date' : 'Fecha',  # Fecha
                 'critical_staffing_shortage_today_yes': 'Reporta_escasez_de_personal', # Hospitales que informan escasez de personal
                 'critical_staffing_shortage_today_no': 'Reportan_sin_escasez_de_personal', # Hospitales
                 'critical_staffing_shortage_today_not_reported': 'No_reportan_sobre_escasez_de_personal', #Hospitales
                 'inpatient_beds': 'Camas_hospital', #hospital_camas  
                 'inpatient_beds_used_covid': 'Camas_usadas_sosp_conf', # hospital_camas_usadas_sospech_confir_covid
                 'previous_day_admission_adult_covid_confirmed': 'Admision_adulto_conf_dia_previo', # día_anterior_admisión_adulto_covid_confirmado
                 'previous_day_admission_pediatric_covid_confirmed': 'Admision_pediatrico_conf_dia_previo', # día_anterior_ingreso_pediátrico_covid_confirmado
                  'staffed_adult_icu_bed_occupancy': 'Camas_UCI_ocupadas_general', # numero_total_camas_UCI_ocupadas_general
                  'staffed_icu_adult_patients_confirmed_covid': 'Camas_UCI_adultos_ocupadas_conf', # numero_camas_UCI_ocupadas_Covid_confirmado_adultos
                  'total_adult_patients_hospitalized_confirmed_covid': 'Camas_comunes_adulto_ocupadas_conf', # numero_camas_comunes_ocupadas_Covid_confirmado
                  'total_pediatric_patients_hospitalized_confirmed_covid': 'Camas_comunes_pediatrico_ocupadas_conf', # numero_camas_comunes_ocupadas_Covid_confirmado_pediatrico
                  'total_staffed_adult_icu_beds': 'Camas_UCI_adultos', # numero_camas_UCI_adultos
                  'inpatient_beds_utilization': 'Porcentaje_utilizacion_camas', # porcentaje de camas utilizadas en el estado
                  #'geocoded_state', # estado_geocodificado 
                  'previous_day_admission_adult_covid_confirmed_18_19': 'Rango_18_19_confirmados_hospitalizados', # rango etario
                  'previous_day_admission_adult_covid_confirmed_20_29': 'Rango_20_29_confirmados_hospitalizados', # rango etario
                  'previous_day_admission_adult_covid_confirmed_30_39': 'Rango_30_39_confirmados_hospitalizados', # rango etario
                  'previous_day_admission_adult_covid_confirmed_40_49': 'Rango_40_49_confirmados_hospitalizados', # rango etario
                  'previous_day_admission_adult_covid_confirmed_50_59': 'Rango_50_59_confirmados_hospitalizados', # rango etario
                  'previous_day_admission_adult_covid_confirmed_60_69': 'Rango_60_69_confirmados_hospitalizados',  # rango etario
                  'previous_day_admission_adult_covid_confirmed_70_79': 'Rango_70_79_confirmados_hospitalizados', # rango etario
                  'previous_day_admission_adult_covid_confirmed_80': 'Rango_80_mas_confirmados_hospitalizados',     # rango etario
                  'previous_day_admission_adult_covid_confirmed_unknown': 'Rango_desconocido_confirmados_hospitalizados', # rango etario
                  'deaths_covid': 'Muertes_covid', # muertes covid conf y sospechosos
                   'all_pediatric_inpatient_beds': 'Camas_pediatricas', # Total camas pediatricas
                   'previous_day_admission_pediatric_covid_confirmed_0_4': 'Rango_0_4_confirmados_hospitalizados',
                   'previous_day_admission_pediatric_covid_confirmed_5_11': 'Rango_5_11_confirmados_hospitalizados',
                   'previous_day_admission_pediatric_covid_confirmed_12_17': 'Rango_12_17_confirmados_hospitalizados'
                }
df = df[list(selecc_col_dic.keys())]
df.rename(selecc_col_dic, axis= 1, inplace= True)
fecha_max = str(df.Fecha.values.max())[:10]
fecha_min = str(df.Fecha.values.min())[:10]

# Funcion principal
def main():
    #titulo
    st.title('Dashboard Proyecto Individual 2')
    st.header('Impacto Hospitalario del Covid-19 en USA')
    #titulo de sidebar
    st.sidebar.header('Parametros')

    #Ponemos los parametros customizables en el sidebar
    st.sidebar.subheader('Intervalo Fechas Muestras - Mapa Geografico')
    fecha_inicio = st.sidebar.date_input('Fecha Inicio: ', value= dt.date.fromisoformat(fecha_min), min_value= dt.date.fromisoformat(fecha_min), max_value= dt.date.fromisoformat(fecha_max))
    fecha_final = st.sidebar.date_input('Fecha Final: ', value= dt.date.fromisoformat('2022-08-10'), min_value= dt.date.fromisoformat(fecha_min), max_value= dt.date.fromisoformat(fecha_max))
    
    # Parte 1
    # Filtramos dataset
    df_fechas = df[(df['Fecha'] >= str(fecha_inicio)) & (df['Fecha'] <= str(fecha_final))]
    df_agrup_state = df_fechas[['Estado', 'Camas_comunes_adulto_ocupadas_conf', 'Camas_comunes_pediatrico_ocupadas_conf', 'Muertes_covid', 'Reporta_escasez_de_personal']]
    df_agrup_state['Hospitalizados'] = df_agrup_state['Camas_comunes_adulto_ocupadas_conf'] + df_agrup_state['Camas_comunes_pediatrico_ocupadas_conf']
    df_agrup_state = df_agrup_state.groupby('Estado', as_index= False).sum()
    df_agrup_state = df_agrup_state.sort_values(by = 'Camas_comunes_adulto_ocupadas_conf' ,ascending= False)
    
    st.subheader('Mapa USA')

    opcion_mapa = st.selectbox('Selecccionar Filtro', ['Hospitalizados', 'Muertes_covid'])

    # Mapa Hospitalizados
    def grafico_mapa(df, filtro = 'Hospitalizados'):
        figura_mapa= px.choropleth(df,
                           locations= df['Estado'],
                           locationmode= 'USA-states',
                           scope= 'usa',
                           color= df[filtro],
                           color_continuous_scale= 'blues',
                           labels= {'locations': 'Estado', 'color_continuous_scale': 'Hospitales'},
                           title= 'Hospitalizados por COVID-19 por Estado (USA)',
                           width=800, height=400)

        figura_mapa.update_layout(
                           geo_scope= 'usa',
                           margin=dict(l=20, r=20, t=40, b=20),
                           paper_bgcolor="LightSteelBlue",
                           )
        return figura_mapa

    
    figura_mapa = grafico_mapa(df_agrup_state, opcion_mapa)
    st.plotly_chart(figura_mapa)

    # Parte 2
    # Mostramos informacion en cuerpo de pagina
    st.subheader('Top 5 Estados con Mayor Ocupacion Hosp. COVID')
    st.write('Fecha inicio:', fecha_inicio, 'Fecha Final:', fecha_final)
    
    #Grafico
    def grafico_figura1(df):
        figura1 = px.bar(df, 
                        x= df.Estado,
                        y= df.Hospitalizados,
                        title= 'Top 5 Estados con mayor camas (comunes utilizadas)',
                         width=800, height=400)

        figura1.update_layout(
                           margin=dict(l=20, r=20, t=40, b=20),
                           paper_bgcolor="LightSteelBlue",
                           )
                    
        return figura1
    
    figura1 = grafico_figura1(df_agrup_state[['Estado', 'Hospitalizados']].head(5))
    st.plotly_chart(figura1)

    ## Punto 3
    # Estados que más camas UCI -Unidades de Cuidados Intensivos- utilizaron durante el año 2020
    st.sidebar.subheader('')
    
    
    st.subheader('Estados que más camas UCI -Unidades de Cuidados Intensivos- utilizaron durante el año 2020')
    
    # Filtramos dataset
    df_2020 = df[(df['Fecha'] <= '2020-12-31')]
    df_agrup_state_UCI = df_2020[['Estado', 'Camas_UCI_adultos_ocupadas_conf']].groupby('Estado').sum()

   
    opciones = st.slider('Seleccionar cantidad de Estados a Mostrar', 1, len(df_agrup_state_UCI), 5)
    df_agrup_state_UCI = df_agrup_state_UCI.sort_values(by = 'Camas_UCI_adultos_ocupadas_conf' ,ascending= False).head(opciones)

    #Graficamos
    def grafico_figura3(df):
        figura3 = px.bar(df_agrup_state_UCI,
                        width=800, height=400)

        figura3.update_layout(
                           margin=dict(l=20, r=20, t=40, b=20),
                           paper_bgcolor="LightSteelBlue",
                           )
        figura3.update_yaxes(title_text='Cant Camas UCI')
        
        return figura3
    
    figura3 = grafico_figura3(df_agrup_state_UCI)
    st.plotly_chart(figura3)
    

    ## Parte 4
    #Ponemos los parametros customizables en el sidebar
    st.sidebar.subheader('Intervalo Fechas - Ocupacion Camas')
    fecha_inicio_2 = st.sidebar.date_input('Fecha Inicio Intervalo: ', value= dt.date.fromisoformat(fecha_min), min_value= dt.date.fromisoformat(fecha_min), max_value= dt.date.fromisoformat(fecha_max))
    fecha_final_2 = st.sidebar.date_input('Fecha Final Intervalo: ', value= dt.date.fromisoformat('2021-08-01'), min_value= dt.date.fromisoformat(fecha_min), max_value= dt.date.fromisoformat(fecha_max))

    df_fechas2 = df[(df['Fecha'] >= str(fecha_inicio_2)) & (df['Fecha'] <= str(fecha_final_2))] 
    df_hospitalizados = df_fechas2[['Fecha', 'Camas_comunes_adulto_ocupadas_conf', 'Camas_comunes_pediatrico_ocupadas_conf', 'Camas_UCI_adultos_ocupadas_conf']]
    df_hospitalizados['Hospitalizados'] = df_hospitalizados['Camas_comunes_adulto_ocupadas_conf'] + df_hospitalizados['Camas_comunes_pediatrico_ocupadas_conf']

    # Agrupo
    df_hospitalizados = df_hospitalizados.groupby('Fecha', as_index= False).sum()
    df_hospitalizados.drop(['Camas_comunes_pediatrico_ocupadas_conf','Camas_comunes_adulto_ocupadas_conf'], axis=1, inplace= True)
    df_hospitalizados.rename({'Camas_UCI_adultos_ocupadas_conf':'Hospitalizados_UCI'}, axis= 1, inplace= True)
    
    st.subheader('Ocupación de camas en Hospitales por COVID')
    st.write('Fecha inicio:', fecha_inicio_2, 'Fecha Final:', fecha_final_2)

    # Graficamos
    max_2020 = df_hospitalizados.Hospitalizados.max()
    fecha_punto_max = str(df_hospitalizados[(df_hospitalizados['Hospitalizados'] == max_2020)].Fecha.values)[2:12]
    
    def grafico_figura2(df, x_anot, y_anot):
        figura8 = px.line(df,
                    x= df.Fecha,
                    y= [df.Hospitalizados, df.Hospitalizados_UCI],
                    title= 'Nivels de Ocupacion Camas en Hospitales por Covid',
                    width=800, height=400)

        figura8.update_layout(
                           margin=dict(l=20, r=20, t=40, b=20),
                           paper_bgcolor="LightSteelBlue",
                           )
        figura8.update_yaxes(title_text='Cant Hopitalizados')
        figura8.add_annotation(x= x_anot, y= y_anot,
                    text="Pico de Hospitalizados",
                    xref="x",
                    yref="y",
                    showarrow=True,
                    font=dict(
                        family="Courier New, monospace",
                        size=12,
                        color="#ffffff"
                            ),
                    align="center",
                    arrowhead=2,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor="#636363",
                    ax=20,
                    ay=-30,
                    bordercolor="#c7c7c7",
                    borderwidth=2,
                    borderpad=4,
                    bgcolor="#ff7f0e",
                    opacity=0.8
                    )
                    
        return figura8
    
    figura2 = grafico_figura2(df_hospitalizados, fecha_punto_max, max_2020)
    st.plotly_chart(figura2)

    st.write('Punto Max:', max_2020, 'Fecha:', fecha_punto_max)

    #Grafico de Barras Etario
    df_etario = df_fechas2[['Rango_0_4_confirmados_hospitalizados',
              'Rango_5_11_confirmados_hospitalizados',
              'Rango_12_17_confirmados_hospitalizados',
              'Rango_18_19_confirmados_hospitalizados',
              'Rango_20_29_confirmados_hospitalizados',
              'Rango_30_39_confirmados_hospitalizados',
              'Rango_40_49_confirmados_hospitalizados',
              'Rango_50_59_confirmados_hospitalizados',
              'Rango_60_69_confirmados_hospitalizados',
              'Rango_70_79_confirmados_hospitalizados',
              'Rango_80_mas_confirmados_hospitalizados']]
    
    dicc_rename_rango = {'Rango_0_4_confirmados_hospitalizados': '0_4',
                'Rango_5_11_confirmados_hospitalizados': '5_11',
                'Rango_12_17_confirmados_hospitalizados': '12_17',
                'Rango_18_19_confirmados_hospitalizados': '18_19',
                'Rango_20_29_confirmados_hospitalizados': '20-29',
                'Rango_30_39_confirmados_hospitalizados': '30_39',
                'Rango_40_49_confirmados_hospitalizados': '40-49',
                'Rango_50_59_confirmados_hospitalizados': '50_59',
                'Rango_60_69_confirmados_hospitalizados':  '60_69',
                'Rango_70_79_confirmados_hospitalizados':  '70_79',
                'Rango_80_mas_confirmados_hospitalizados':  '80+'}
    
    df_etario.rename(dicc_rename_rango, axis= 1, inplace= True)
    
    #Se crea un diccionario con la suma
    dicc_etario= {}
    for c in df_etario.columns:
        dicc_etario[c] = df_etario[c].sum()

    df_etario = pd.DataFrame([[key, dicc_etario[key]] for key in dicc_etario.keys()], columns=['Rango', 'Hopitalizados_Confirm'])
    
    def grafico_barras_etario(df):
        figura9 = px.bar(df, 
                 x= df.Rango,
                 y= df.Hopitalizados_Confirm,
                 title= 'Hospitalizados por Rango Etario',
                width=800, height=400)

        figura9.update_layout(
                           margin=dict(l=20, r=20, t=40, b=20),
                           paper_bgcolor="LightSteelBlue",
                           )
        return figura9

    figura9 = grafico_barras_etario(df_etario)
    st.plotly_chart(figura9)

    st.write('Fuente de datos: https://healthdata.gov/Hospital/COVID-19-Reported-Patient-Impact-and-Hospital-Capa/g62h-syeh')
# Indicamos este archivo.py como principal
if __name__ == '__main__':
    main()