import streamlit as st
import pandas as pd
import os
from datetime import datetime
import time
import plotly.express as px
import plotly.graph_objs as go
from sklearn.linear_model import LinearRegression
from datetime import date
from datetime import datetime

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Encabezado #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
st.set_page_config(page_title = 'Proyecciones Ixachi 3D', page_icon = ':bar_chart:', layout = 'wide')
st.title('Proyecciones por Departamento: SOLUCIÓN INTEGRAL DE LA IMAGEN SÍSMICA ENFOCADA AL PLAY MESOZOICO IXACHI 3D')

# Función para obtener la hora y fecha actual
def get_current_time():
    now = datetime.now()
    current_date = now.strftime("%d/%m/%Y")
    current_time = now.strftime("%H:%M:%S")
    return current_date, current_time

# Crear columnas para la fecha y la hora
col1, col2 = st.columns([1, 1])

# Obtener la fecha y hora actual
current_date, current_time = get_current_time()

# Mostrar la fecha y hora
col2.markdown(f"""
<div style="font-size: 1.5rem; font-weight: bold; color: #dcdee0; text-align: right;">
    Fecha: {current_date}
</div>
""", unsafe_allow_html=True)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Cargar Archivos #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Subida de archivos
fl = st.file_uploader(':file_folder: Subir archivo', type=['csv', 'txt', 'xlsx', 'xls'])

def leer_archivo(archivo, codificaciones=['ISO-8859-1', 'utf-8', 'latin1']):
    for cod in codificaciones:
        try:
            return pd.read_csv(archivo, encoding=cod), cod
        except UnicodeDecodeError:
            continue
    raise ValueError("No se pudo decodificar el archivo con las codificaciones probadas.")

if fl is not None:
    # Intentar leer el archivo subido con varias codificaciones
    try:
        df, cod_usada = leer_archivo(fl)
        st.success(f"Archivo leído correctamente usando la codificación {cod_usada}.")
    except ValueError as e:
        st.error(f"No se pudo leer el archivo subido. Error: {e}")
else:
    # Intentar leer el archivo predeterminado
    archivo_predeterminado = 'ReporteDiario_Gestoria.csv'
    try:
        df, cod_usada = leer_archivo(archivo_predeterminado)
        st.success(f"Archivo predeterminado leído correctamente usando la codificación {cod_usada}.")
    except ValueError as e:
        st.error(f"No se pudo leer el archivo predeterminado. Error: {e}")

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Fehas restantes #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

# Fechas importantes
fecha_topografia = datetime(2024, 4, 1)
fecha_perforacion = datetime(2024, 5, 7)

fecha_actual = datetime.now()

# Convertimos las fechas a strings para poder comparar con el DataFrame
fecha_topografia_str = fecha_topografia.strftime('%d/%m/%Y')
fecha_perforacion_str = fecha_perforacion.strftime('%d/%m/%Y')
fecha_hoy_vline = fecha_actual.strftime('%d/%m/%Y')

topografia_df = df[df['Fecha'] == fecha_topografia_str]
perforacion_df = df[df['Fecha'] == fecha_perforacion_str]
hoy_df = df[df['Fecha'] == fecha_hoy_vline]

id_topografia = topografia_df['ID'].iloc[0]
id_perforacion = perforacion_df['ID'].iloc[0]
id_hoy = hoy_df['ID'].iloc[0]

# Buscar los IDs correspondientes para las fechas de topografía y perforación
id_topografia = df[df['Fecha'] == fecha_topografia_str]['ID'].iloc[0]
id_perforacion = df[df['Fecha'] == fecha_perforacion_str]['ID'].iloc[0]
id_hoy = df[df['Fecha'] == fecha_hoy_vline]['ID'].iloc[0]

# Fecha actual
fecha_actual = datetime.now()

# Calcular los días restantes
dias_para_topografia = (fecha_topografia - fecha_actual).days
dias_para_perforacion = (fecha_perforacion - fecha_actual).days

# Definir el color para el texto de los días restantes
color_texto = "#ec5252"  # Un verde claro, por ejemplo

# Crear el texto con HTML para colorear los días restantes
texto_topografia = f"Inicia Topografía: {fecha_topografia.strftime('%d/%m/%Y')} - <span style='color:{color_texto};'>Días restantes: {dias_para_topografia} días</span>"
texto_perforacion = f"Inicia Perforación: {fecha_perforacion.strftime('%d/%m/%Y')} - <span style='color:{color_texto};'>Días restantes: {dias_para_perforacion} días</span>"

# Mostrar las fechas importantes con los días restantes en colores
st.markdown(texto_topografia, unsafe_allow_html=True)
st.markdown(texto_perforacion, unsafe_allow_html=True)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regresión Lineal #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
#PERMISOS

available_data_permisos = df.dropna(subset=['PermisosDia_Real_Sumatoria']).copy()
X_train_per = available_data_permisos[['ID']]
y_train_per = available_data_permisos['PermisosDia_Real_Sumatoria']

model = LinearRegression()
model.fit(X_train_per, y_train_per)

# Predecir los valores faltantes y extender la línea de regresión
# Para toda la columna 'ID'
X_full_per = df[['ID']]
df['Predicted_PermisosDia_Real_Sumatoria'] = model.predict(X_full_per)

#Km2

available_data_Km2 = df.dropna(subset=['Desempeno_Real_Km2_Sumatoria']).copy()
X_train_Km2 = available_data_Km2[['ID']]
y_train_Km2 = available_data_Km2['Desempeno_Real_Km2_Sumatoria']

model = LinearRegression()
model.fit(X_train_Km2, y_train_Km2)

# Predecir los valores faltantes y extender la línea de regresión
# Para toda la columna 'ID'
X_full_Km2 = df[['ID']]
df['Predicted_Desempeno_Real_Km2_Sumatoria'] = model.predict(X_full_Km2)


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Gráficos #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
######## Permisos ########

# Crear gráficos de dispersión
# Crear un gráfico de dispersión con una línea de tendencia (regresión lineal)

fig_permisos = go.Figure()
fig_permisos.add_trace(go.Scatter(x=df['Fecha'], y=df['PermisosDia_Real_Sumatoria'], mode='markers', name='Desempeño Real',
                         marker=dict(color='green')))

# Modificar todas las trazas actuales para cambiarlas a líneas
fig_permisos.update_traces(mode='markers')

# Añadir la curva de Desempeño Proyectado
fig_permisos.add_trace(
    go.Scatter(x=df['Fecha'], y=df['Desempeno_Proyectado_Permisos_Sumatoria'],
                mode='lines', name='Desempeño Proyectado', line=dict(color='LightSkyBlue') ))

#Curva de Desempeño real REGRESION
fig_permisos.add_trace(
    go.Scatter(
        x=df['Fecha'], 
        y=df['Predicted_PermisosDia_Real_Sumatoria'],
        mode='lines',
        name='Desmpeño Real Proyectado',
        line=dict(color='#A52A2A', dash='dash')  # Puedes cambiar el color como prefieras
    )
)

######################################################################## Km2 ########################################################################
# Crear un gráfico de dispersión con una línea de tendencia (regresión lineal)

fig_km2 = go.Figure()
fig_km2.add_trace(go.Scatter(x=df['Fecha'], y=df['Desempeno_Real_Km2_Sumatoria'], mode='markers', name='Desempeño Real',
                         marker=dict(color='green')))

# Modificar todas las trazas actuales para cambiarlas a líneas
fig_km2.update_traces(mode='markers')

# Añadir la curva de Desempeño Proyectado
fig_km2.add_trace(
    go.Scatter(x=df['Fecha'], y=df['Desempeno_Proyectado_Km2_Sumatoria'],
                mode='lines', name='Desempeño Proyectado', line=dict(color='LightSkyBlue')))

#Curva de Desempeño real REGRESION
fig_km2.add_trace(
    go.Scatter(
        x=df['Fecha'], 
        y=df['Predicted_Desempeno_Real_Km2_Sumatoria'],
        mode='lines',
        name='Desmpeño Real Proyectado',
        line=dict(color='#A52A2A', dash='dash')  # Puedes cambiar el color como prefieras
    )
)

######################################################################## Fechas Importantes ########################################################################
# Añadir líneas verticales con anotaciones de dos líneas para las fechas de topografía
fig_permisos.add_vline(x=id_topografia, line_width=2, line_dash="dash", line_color="green",
                       annotation_text="Inicia Topografía<br>(fecha límite)",
                       annotation_position="top left")
fig_km2.add_vline(x=id_topografia, line_width=2, line_dash="dash", line_color="green",
                  annotation_text="Inicia Topografía<br>(fecha límite)",
                  annotation_position="top left")

# Añadir líneas verticales con anotaciones de dos líneas para las fechas de perforación
fig_permisos.add_vline(x=id_perforacion, line_width=2, line_dash="dash", line_color="red",
                       annotation_text="Inicia Perforación<br>(fecha límite)",
                       annotation_position="top left")
fig_km2.add_vline(x=id_perforacion, line_width=2, line_dash="dash", line_color="red",
                  annotation_text="Inicia Perforación<br>(fecha límite)",
                  annotation_position="top left")

fig_permisos.add_vline(x=id_hoy, line_width=2, line_dash="dash", line_color="blue",
                        annotation_text="Avance actual<br>",
                        annotation_position="top left")

fig_km2.add_vline(x=id_hoy, line_width=2, line_dash="dash", line_color="blue",
                        annotation_text="Avance actual<br>",
                        annotation_position="top left")


######################################################################## Layout Gráficos ########################################################################
fig_permisos.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),  # Ajusta los valores según necesites para los márgenes
    yaxis_title='Desempeño en Permisos',  # Actualiza el título del eje Y
    xaxis_tickangle=45, xaxis_title='Fecha',
    legend=dict(
        yanchor="top",
        y=-0.3,  # Ajusta esto para separar la leyenda del gráfico
        xanchor="center",
        x=0.5,
        orientation="h"
    )
)

fig_km2.update_layout(
    margin=dict(l=20, r=20, t=20, b=20),  # Ajusta los valores según necesites para los márgenes
    yaxis_title='Desempeño en Km2',  # Actualiza el título del eje Y
    xaxis_tickangle=45, xaxis_title='Fecha',
    legend=dict(
        yanchor="top",
        y=-0.3,  # Ajusta esto para separar la leyenda del gráfico
        xanchor="center",
        x=0.5,
        orientation="h"
    )
)

################################################# Gráficos de pastel total - real ######################################################
#Permisos

# Calculando el total proyectado y el total real
total_proyectado = df['Prom_ProyectadoXDia_Permisos'].sum()
total_real = df['PermisosDia_Real'].sum()
deficit = df['PermisosDia_Real_Sumatoria'].last_valid_index()

# Usar el índice para obtener el último valor no NaN de esas columnas
msj_deficit = df.at[deficit, 'Deficit_Permisos']

# Calculando el valor restante para alcanzar el proyectado
valor_restante_del_proyectado = total_proyectado - total_real

# Datos para el gráfico de pastel con valores numéricos
values = [total_real, valor_restante_del_proyectado]
labels = ['Realizado', 'Restante']

# Crear la figura de Plotly para el gráfico de pastel
fig_pie_perm = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3)])

# Añadir porcentajes y valores absolutos en el texto del gráfico de pastel
fig_pie_perm.update_traces(
    textinfo='percent+value', 
    textfont_size=15,
    marker=dict(line=dict(color='#000000', width=1))
)

# Actualizar el layout para mejorar la visualización
fig_pie_perm.update_layout(
    title_text='Proyectados vs. Realizados en Permisos',
    # Coloca la leyenda a un lado para que no bloquee la visualización del gráfico
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="right",
        x=1
    )
)

#Km2
total_proyectado_km2 = df['Prom_ProyectadoXDia_Km2'].sum()
total_real_km2 = df['Km2_Diarios'].sum()
deficit_km2 = df['PermisosDia_Real_Sumatoria'].last_valid_index()

# Usar el índice para obtener el último valor no NaN de esas columnas
msj_deficit_km2 = df.at[deficit_km2, 'Deficit_Km2_DelTotal']

# Calculando el valor restante para alcanzar el proyectado
valor_restante_del_proyectado_km2 = total_proyectado_km2 - total_real_km2

# Datos para el gráfico de pastel con valores numéricos
values_km2 = [total_real_km2, valor_restante_del_proyectado_km2]
labels_km2 = ['Realizado', 'Restante']

# Crear la figura de Plotly para el gráfico de pastel
fig_pie_km2 = go.Figure(data=[go.Pie(labels=labels_km2, values=values_km2, hole=.3)])

# Añadir porcentajes y valores absolutos en el texto del gráfico de pastel
fig_pie_km2.update_traces(
    textinfo='percent+value', 
    textfont_size=15,
    marker=dict(line=dict(color='#000000', width=1))
)

# Actualizar el layout para mejorar la visualización
fig_pie_km2.update_layout(
    title_text='Proyectados vs. Realizados en Km2',
    # Coloca la leyenda a un lado para que no bloquee la visualización del gráfico
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="right",
        x=1
    )
)

##########################################################Gráfica de barras Gestores##################################################################

x_values = df['Fecha']
y_values = df['No_GestoresXDia']

# Crear la gráfica de barras con Plotly
fig_bar = go.Figure(
    go.Bar(
        x=x_values,
        y=y_values
    )
)

# Configurar el layout de la figura si lo deseas (título, etiquetas de eje, etc.)
fig_bar.update_layout(
    title='Gestores por Día',
    xaxis_title='Días',
    yaxis_title='Gestores'
)

# Añadir líneas verticales con anotaciones de dos líneas para las fechas de topografía
fig_bar.add_vline(x=id_topografia, line_width=2, line_dash="dash", line_color="green",
                       annotation_text="Inicia Topografía<br>(fecha límite)",
                       annotation_position="top left")

# Añadir líneas verticales con anotaciones de dos líneas para las fechas de perforación
fig_bar.add_vline(x=id_perforacion, line_width=2, line_dash="dash", line_color="red",
                       annotation_text="Inicia Perforación<br>(fecha límite)",
                       annotation_position="top left")

fig_bar.add_vline(x=id_hoy, line_width=2, line_dash="dash", line_color="blue",
                        annotation_text="Avance actual<br>",
                        annotation_position="top left")



#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Personal Necesario %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Rendimiento_permisos = df['PermisosDia_Real'].median()
Rendimiento_Km2 = df['Km2_Diarios'].median()

meta_permisos = df['Desempeno_Proyectado_Permisos_Sumatoria'].tail(1).iloc[0]
meta_km2 = df['Desempeno_Proyectado_Km2_Sumatoria'].tail(1).iloc[0]
x2 = df['ID'].tail(1).iloc[0]

# Crear una entrada de número float
incerti = (st.number_input('Incertidumbre:', format="%.2f")) / 100

# Botón para guardar el valor
if st.button('Guardar Valor [%]'):
    # Aquí puedes hacer algo con el valor_float, como guardarlo o procesarlo
    st.success(f'La incertidumbre agregada es: {incerti}')

extra_meta_permisos = 1 + incerti
extra_meta_km2 = 1 + incerti

y2_permisos, y2_km2 = meta_permisos * extra_meta_permisos, meta_km2 * extra_meta_km2


# Obtener el índice del último valor no NaN para las columnas específicas
indice_ultimo_valor_permisos = df['PermisosDia_Real_Sumatoria'].last_valid_index()
indice_ultimo_valor_km2 = df['Desempeno_Real_Km2_Sumatoria'].last_valid_index()

# Usar el índice para obtener el último valor no NaN de esas columnas
y1_permisos = df.at[indice_ultimo_valor_permisos, 'PermisosDia_Real_Sumatoria']
y1_km2 = df.at[indice_ultimo_valor_km2, 'Desempeno_Real_Km2_Sumatoria']

# Correcto: Usar los índices para obtener los valores de ID correspondientes
x1_permisos = df.at[indice_ultimo_valor_permisos, 'ID']
x1_km2 = df.at[indice_ultimo_valor_km2, 'ID']

# Calcular la pendiente (m) para permisos
m_permisos = (y2_permisos - y1_permisos) / (x2 - x1_permisos)

m_km2 = (y2_km2 - y1_km2) / (x2 - x1_km2)

# Calcular el intercepto (b)
b_permisos = y1_permisos - m_permisos * x1_permisos

b_km2 = y1_km2 - m_km2 * x1_km2

indices_nan_permisos = df[pd.isna(df['PermisosDia_Real_Sumatoria'])].index

indices_nan_km2 = df[pd.isna(df['Desempeno_Real_Km2_Sumatoria'])].index

for indice in indices_nan_permisos:
    # Tomar el valor de ID como x.
    x = df.at[indice, 'ID']
    # Calcular y basado en y = mx + b.
    y_cal_permisos = m_permisos * x + b_permisos
    # Reemplazar el valor NaN en la columna objetivo con el valor calculado.
    df.at[indice, 'PermisosDia_Real_Sumatoria'] = y_cal_permisos

for indice in indices_nan_km2:
    # Tomar el valor de ID como x.
    x = df.at[indice, 'ID']
    # Calcular y basado en y = mx + b.
    y_cal_km2 = m_km2 * x + b_km2
    # Reemplazar el valor NaN en la columna objetivo con el valor calculado.
    df.at[indice, 'Desempeno_Real_Km2_Sumatoria'] = y_cal_km2

# Calcular la diferencia para la columna 'PermisosDia_Real_Sumatoria'
penultimo_valor_permisos = df['PermisosDia_Real_Sumatoria'].iloc[-2]
ultimo_valor_permisos = df['PermisosDia_Real_Sumatoria'].iloc[-1]
diferencia_permisos = ultimo_valor_permisos - penultimo_valor_permisos

# Calcular la diferencia para la columna 'Desempeno_Real_Km2_Sumatoria'
penultimo_valor_km2 = df['Desempeno_Real_Km2_Sumatoria'].iloc[-2]
ultimo_valor_km2 = df['Desempeno_Real_Km2_Sumatoria'].iloc[-1]
diferencia_km2 = ultimo_valor_km2 - penultimo_valor_km2

# Guardar las diferencias en variables
diferencia_permisos_variable = diferencia_permisos
diferencia_km2_variable = diferencia_km2

med_rendi_permisos = df['RendimientoXGestor_Permisos'].median() * 0.75
med_rendi_km2 = df['RendimientoXGestor_Km2'].median() * 0.75

Gest_req_perm = round(diferencia_permisos_variable / med_rendi_permisos)
Gest_req_km2 = round(diferencia_km2_variable / med_rendi_km2)

#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Gráficos #%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
######## Permisos ########

fig_permisos2 = go.Figure()

# Añadir los datos de desempeño real como puntos
fig_permisos2.add_trace(go.Scatter(
    x=df['Fecha'],
    y=df['PermisosDia_Real_Sumatoria'],
    mode='markers',  # Cambio aquí: originalmente tenías 'lines', pero para comenzar con 'markers' es más intuitivo
    name='Desempeño Real Proyectado',
    marker=dict(color='green')
))

# Añadir la curva de Desempeño Proyectado
fig_permisos2.add_trace(go.Scatter(
    x=df['Fecha'],
    y=df['Desempeno_Proyectado_Permisos_Sumatoria'],
    mode='lines',
    name='Desempeño Proyectado',
    line=dict(color='LightSkyBlue')
))

# Añadir curva de Desempeño real proyectado (regresión)
fig_permisos2.add_trace(go.Scatter(
    x=df['Fecha'], 
    y=df['Predicted_PermisosDia_Real_Sumatoria'],
    mode='lines',
    name='Desempeño Real Proyectado',
    line=dict(color='#A52A2A', dash='dash')
))

# Añadir anotaciones para fechas importantes
fig_permisos2.add_vline(x=id_topografia, line_width=2, line_dash="dash", line_color="green",
                        annotation_text="Inicia Topografía<br>(fecha límite)",
                        annotation_position="top left")
fig_permisos2.add_vline(x=id_perforacion, line_width=2, line_dash="dash", line_color="red",
                        annotation_text="Inicia Perforación<br>(fecha límite)",
                        annotation_position="top left")
fig_permisos2.add_vline(x=id_hoy, line_width=2, line_dash="dash", line_color="blue",
                        annotation_text="Avance actual<br>",
                        annotation_position="top left")

# Configurar el layout del gráfico
fig_permisos2.update_layout(title='Permisos Real vs Proyectado [No. Permisos]',
    margin=dict(l=20, r=20, t=20, b=20),
    yaxis_title='Desempeño en Permisos',
    xaxis_tickangle=45, xaxis_title='Fecha',
    legend=dict(
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5,
        orientation="h"
    ),
    # Ajustar la configuración para asegurar que el gráfico use todo el ancho disponible
    autosize=True,  # Asegura que el tamaño se ajusta al contenedor
    width=None,  # Deja que Streamlit controle el ancho
)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig_permisos2, use_container_width=True)  # Asegura que el gráfico se ajuste al ancho del contenedor

#################################################################### Km2 #########################################################

fig_km2_2 = go.Figure()

# Añadir los datos de desempeño real como puntos
fig_km2_2.add_trace(go.Scatter(
    x=df['Fecha'],
    y=df['Desempeno_Real_Km2_Sumatoria'],
    mode='markers',  # Cambio aquí: originalmente tenías 'lines', pero para comenzar con 'markers' es más intuitivo
    name='Desempeño Real Proyectado',
    marker=dict(color='green')
))

# Añadir la curva de Desempeño Proyectado
fig_km2_2.add_trace(go.Scatter(
    x=df['Fecha'],
    y=df['Desempeno_Proyectado_Km2_Sumatoria'],
    mode='lines',
    name='Desempeño Proyectado',
    line=dict(color='LightSkyBlue')
))

# Añadir curva de Desempeño real proyectado (regresión)
fig_km2_2.add_trace(go.Scatter(
    x=df['Fecha'], 
    y=df['Predicted_Desempeno_Real_Km2_Sumatoria'],
    mode='lines',
    name='Desempeño Real Proyectado',
    line=dict(color='#A52A2A', dash='dash')
))

# Añadir anotaciones para fechas importantes
fig_km2_2.add_vline(x=id_topografia, line_width=2, line_dash="dash", line_color="green",
                        annotation_text="Inicia Topografía<br>(fecha límite)",
                        annotation_position="top left")
fig_km2_2.add_vline(x=id_perforacion, line_width=2, line_dash="dash", line_color="red",
                        annotation_text="Inicia Perforación<br>(fecha límite)",
                        annotation_position="top left")
fig_km2_2.add_vline(x=id_hoy, line_width=2, line_dash="dash", line_color="blue",
                        annotation_text="Avance actual<br>",
                        annotation_position="top left")

# Configurar el layout del gráfico
fig_km2_2.update_layout(title='Permisos Real vs Proyectado [Km2]',
    margin=dict(l=20, r=20, t=20, b=20),
    yaxis_title='Desempeño en Km2',
    xaxis_tickangle=45, xaxis_title='Fecha',
    legend=dict(
        yanchor="top",
        y=-0.3,
        xanchor="center",
        x=0.5,
        orientation="h"
    ),
    # Ajustar la configuración para asegurar que el gráfico use todo el ancho disponible
    autosize=True,  # Asegura que el tamaño se ajusta al contenedor
    width=None,  # Deja que Streamlit controle el ancho
)

gestores_actl = round(df['No_GestoresXDia'].dropna().iloc[-1])

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig_km2_2, use_container_width=True)  # Asegura que el gráfico se ajuste al ancho del contenedor

st.markdown(f"""
    <div style='background-color: black; padding: 10px;'>
        <h3 style='text-align: center; color: white;'>Gestores Actuales: <span style='color: white;'>{gestores_actl}</span></h3>    
        <h3 style='text-align: center; color: white;'>Gestores Requeridos por Permisos: <span style='color: red;'>{Gest_req_perm}</span></h3>
        <h3 style='text-align: center; color: white;'>Gestores Requeridos por Km2: <span style='color: red;'>{Gest_req_km2}</span></h3>
    </div>
    """, unsafe_allow_html=True)

############################################# Mostrar los gráficos con espacio adicional entre ellos #############################################
# Crea un layout de dos columnas con las proporciones deseadas
col1_Permisos, col2_Permisos = st.columns((2, 1))

# En la columna 1, coloca tu primer gráfico (ocupará dos tercios del ancho)
with col1_Permisos:
    st.plotly_chart(fig_permisos, use_container_width=True)

# En la columna 2, coloca tu segundo gráfico (ocupará un tercio del ancho)
with col2_Permisos:
    st.plotly_chart(fig_pie_perm, use_container_width=True)

# Mensaje que deseas mostrar, incluyendo la variable
mensaje = f"Déficit de Permisos: {msj_deficit}"

# Usando HTML para centrar el mensaje
st.markdown(f"<h3 style='text-align: right; font-size: 16px;'>{mensaje}</h3>", unsafe_allow_html=True)

# Crea un layout de dos columnas con las proporciones deseadas
col1_km2, col2_km2 = st.columns((2, 1))

# En la columna 1, coloca tu primer gráfico (ocupará dos tercios del ancho)
with col1_km2:
    st.plotly_chart(fig_km2, use_container_width=True)

# En la columna 2, coloca tu segundo gráfico (ocupará un tercio del ancho)
with col2_km2:
    st.plotly_chart(fig_pie_km2, use_container_width=True)

# Mensaje que deseas mostrar, incluyendo la variable
mensaje_km2 = f"Déficit de Km2: {msj_deficit_km2}"

# Usando HTML para centrar el mensaje
st.markdown(f"<h3 style='text-align: right; font-size: 16px;'>{mensaje_km2}</h3>", unsafe_allow_html=True)

st.plotly_chart(fig_bar, use_container_width=True)

if 'df' in locals():
    st.write(df)
else:
    st.write("Por favor, suba un archivo o asegúrese de que el archivo predeterminado esté disponible.")
