import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns




# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Cabina estetica",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

#############   caricamento manuale file     ##################

def upload_file():
    # Sezione espandibile per il caricamento del file
    with st.expander("📂 Carica File Excel"):
        uploaded_file = st.file_uploader("Seleziona un file Excel", type="xlsx")
        if uploaded_file:
            st.success("File caricato con successo!")
           # Salva i dati nel session state
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['data'] = load_and_preprocess_data(uploaded_file)
    return uploaded_file

def load_and_preprocess_data(uploaded_file):
    data = pd.read_excel(
        uploaded_file,
        usecols="A,B,C,D,E,F,G,H,I,J",
        engine="openpyxl"
    )


    data.columns = [
        'codice',
        'categoria',
        'descrizione',
        'distribuzione_costi',
        'prezzo_vendita',
        'ore_uomo',
        'costo_personale',
        'costo_materiale_consumo',
        'noleggi_ammortamenti',
        'q.ty'
    ]
    data = data.dropna(subset=['codice'])
    # Lista delle colonne da convertire in numerico
    cols_to_convert = ["distribuzione_costi", "prezzo_vendita", "ore_uomo", 
                       "costo_personale", "costo_materiale_consumo",
                       "noleggi_ammortamenti", "q.ty" ]  # Sostituisci con i nomi reali delle colonne
    # Converte solo le colonne specificate in numerico (i valori non numerici diventano NaN)
    data[cols_to_convert] = data[cols_to_convert].apply(pd.to_numeric, errors='coerce').fillna(0)




    return data

def inject_custom_css():
    """
    Inietta CSS personalizzato nella pagina Streamlit.
    """
    custom_css = """
    <style>
        /* Cambia il colore del titolo */
        h1 {
            color: #2E8B57; /* Verde scuro */
        }

        /* Personalizza i metriche */
        .metric-container {
            background-color: #f7f7f7; /* Grigio chiaro */
            border: 1px solid #ddd; /* Bordo sottile */
            border-radius: 8px; /* Angoli arrotondati */
            padding: 10px; /* Spaziatura interna */
            margin: 5px; /* Spaziatura esterna */
        }

        /* Modifica i pulsanti */
        button {
            background-color: #007BFF; /* Blu scuro */
            color: white; /* Testo bianco */
            border: none;
            border-radius: 5px;
            padding: 10px 15px;
        }
        button:hover {
            background-color: #0056b3; /* Blu ancora più scuro */
        }

        /* Personalizza il layout delle colonne */
        .stColumn {
            margin-bottom: 20px; /* Spazio tra colonne */
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def calcolo_kpi(data):

    
    data['costo_totale_servizio'] = data['costo_personale'] + data['costo_materiale_consumo'] + data['noleggi_ammortamenti']
    data['margine_servizio'] = data['prezzo_vendita'] - data['costo_totale_servizio']
    data['incassi_totali'] = data['prezzo_vendita'] * data['q.ty']
    data['costo_totale'] = data['costo_totale_servizio'] * data['q.ty']
    data['margine_totale'] = data['margine_servizio'] * data['q.ty']

    incassi_totali = data['incassi_totali'].sum()
    costi_totali = data['costo_totale'].sum()
    margine_totale = data['margine_totale'].sum()

    # Gestione di NaN e conversione sicura in float
    incassi_totali = float(incassi_totali) if pd.notna(incassi_totali) else 0
    costi_totali = float(costi_totali) if pd.notna(costi_totali) else 0
    margine_totale = float(margine_totale) if pd.notna(margine_totale) else 0

    top3_incassi = data.nlargest(3,'incassi_totali')
    top3_margine = data.nlargest(3, 'margine_totale')
    

    return data, incassi_totali, costi_totali, margine_totale, top3_incassi, top3_margine



def grafico_barre(df):
    """
    Crea un grafico a barre verticali con 3 barre per ogni riga del DataFrame.
    - Asse X: descrizione (nomi delle righe)
    - Asse Y: valori in euro (incassi_totali, costi_totali, margine_totale)
    """

    # Controlla se il DataFrame ha i dati necessari
    colonne_richieste = {'descrizione', 'incassi_totali', 'costo_totale', 'margine_totale'}
    if not colonne_richieste.issubset(df.columns):
        st.error("Il DataFrame non contiene tutte le colonne richieste: 'descrizione', 'incassi_totali', 'costo_totale', 'margine_totale'")
        return

    # Converti in numerico per sicurezza e riempi eventuali NaN con 0
    df[['incassi_totali', 'costo_totale', 'margine_totale']] = df[['incassi_totali', 'costo_totale', 'margine_totale']].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Filtra solo le righe con incassi_totali > 0
    df = df[df['incassi_totali'] > 0]

    # Se non ci sono dati dopo il filtro, mostra un messaggio e termina
    if df.empty:
        st.warning("Nessun dato disponibile con incassi_totali > 0.")
        return

    # Crea il grafico a barre con Plotly
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['descrizione'],
        y=df['incassi_totali'],
        name='Incassi Totali',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=df['descrizione'],
        y=df['costo_totale'],
        name='Costi Totali',
        marker_color='red'
    ))

    fig.add_trace(go.Bar(
        x=df['descrizione'],
        y=df['margine_totale'],
        name='Margine Totale',
        marker_color='green'
    ))

    # Personalizzazione del layout
    fig.update_layout(
        barmode='group',  # Barre affiancate
        title="Confronto Incassi, Costi e Margine per trattamento",
        xaxis_title="Descrizione",
        yaxis_title="Quantità (€)",
        xaxis_tickangle=-45,
        legend_title="Tipologia",
        height=400,  # Altezza del grafico
        width=1200,  # Larghezza del grafico
        template="plotly_white"  # Rimuove lo sfondo grigliato
    )

    # Mostra il grafico in Streamlit
    st.plotly_chart(fig)



def render_dashboard():
    """Visualizza la dashboard con KPI, grafici e calcolo dinamico delle notti disponibili"""
    inject_custom_css()
    st.title("📊 Dashboard Cabina estetica")
    

    # Verifica se i dati principali sono disponibili
    if 'data' not in st.session_state or st.session_state['data'] is None:
        st.error("Nessun dato disponibile. Torna alla pagina di caricamento.")
        return

    # Verifica se il file è disponibile per il calcolo delle notti disponibili
    if 'uploaded_file' not in st.session_state:
        st.error("Nessun file caricato per il calcolo delle notti disponibili.")
        return

    file_path = st.session_state['uploaded_file']
    data = st.session_state['data']

    with st.sidebar.expander("🔍 Filtro Dati"):
        st.markdown("### Filtra i dati")

        # Filtro per Categoria
        categoria = st.selectbox(
            "Seleziona Categoria",
            ["Tutte"] + list(data['categoria'].unique()),
            key="categoria_filter"
        )

        # Filtro per Descrizione
        descrizione = st.selectbox(
            "Seleziona Descrizione",
            ["Tutte"] + list(data['descrizione'].unique()),
            key="descrizione_filter"
        )

    # Applicazione filtri
    filtered_df = data.copy()

    if categoria != "Tutte":
        filtered_df = filtered_df[filtered_df['categoria'] == categoria]

    if descrizione != "Tutte":
        filtered_df = filtered_df[filtered_df['descrizione'] == descrizione]
    
    filtered_df, incassi_totali, costi_totali, margine_totale, top3_incassi, top3_margine = calcolo_kpi(filtered_df)

    # Mostra i dati filtrati
    st.dataframe(top3_incassi)
    st.write(list(filtered_df.columns))  # Mostra i nomi come lista


    col01, col02 =st.columns([2,1])
    with col01:
        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            st.metric("📈 Ricavi Totali (€)", f"{incassi_totali:,.0f}")
        with col2:
            st.metric("📈 Costi Totali (€)", f"{costi_totali:,.0f}")
        with col3:
            st.metric("📈 Margine Totale (€)", f"{margine_totale:,.0f}")
        st.write("### Grafico a Barre: Incassi, Costi e Margine")
        grafico_barre(filtered_df)    
    with col02:
        # Menù a tendina per selezionare tra "Incassi" e "Margine"
        selected_metric = st.selectbox(
            
            "Seleziona il tipo di dati da visualizzare:",
            options=["Incassi", "Margine"]
        )

        # Seleziona il DataFrame corretto in base alla scelta dell'utente
        if selected_metric == "Incassi":
            selected_df = top3_incassi
            title = "📊 Top 3 Incassi"
        else:
            selected_df = top3_margine
            title = "📊 Top 3 Margine"

        # Mostra il titolo dinamico in base alla selezione
        st.subheader(title)

        # Selettore per scegliere la riga del DataFrame (Mostra "Primo", "Secondo", "Terzo")
        selected_option = st.radio(

            "Seleziona il servizio da visualizzare:",
            options=["Primo", "Secondo", "Terzo"],  # Etichette visibili all'utente
            
            horizontal=True
        )

        # Mappa la scelta dell'utente agli indici del DataFrame
        selected_index = {"Primo": 0, "Secondo": 1, "Terzo": 2}[selected_option]
        # Mostra i dati della riga selezionata
        st.metric("📈 Servizio", selected_df['descrizione'].iloc[selected_index])
        st.metric("📈 Incassi Totali servizio(€)", selected_df['incassi_totali'].iloc[selected_index])
        st.metric("📈 Costi Totali per il servizio(€)", selected_df['costo_totale'].iloc[selected_index])
        st.metric("📈 Margine sul servizio(€)", selected_df['margine_totale'].iloc[selected_index])
        st.metric("📈 Numero Trattamenti", selected_df['q.ty'].iloc[selected_index])
    

    

    col5, col6 = st.columns([2,1])

    with col5:
        
    
menu = st.sidebar.selectbox("Navigazione", ["Carica File", "Dashboard"])

if menu == "Carica File":
    upload_file()
elif menu == "Dashboard":
    render_dashboard()







    # Mostra i dati della riga selezionata dal DataFrame corretto
    
