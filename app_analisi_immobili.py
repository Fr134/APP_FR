import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

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
    colonne_richieste = {'descrizione', 'incassi_totali', 'costi_totali', 'margine_totale'}
    if not colonne_richieste.issubset(df.columns):
        st.error("Il DataFrame non contiene tutte le colonne richieste: 'descrizione', 'incassi_totali', 'costi_totali', 'margine_totale'")
        return

    # Converti in numerico per sicurezza e riempi eventuali NaN con 0
    df[['incassi_totali', 'costi_totali', 'margine_totale']] = df[['incassi_totali', 'costi_totali', 'margine_totale']].apply(pd.to_numeric, errors='coerce').fillna(0)

    # Imposta lo stile del grafico
    sns.set_style("whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Larghezza delle barre
    larghezza_barra = 0.2

    # Genera le posizioni per ogni categoria
    x = range(len(df))

    # Plotta le tre serie di dati
    ax.bar([pos - larghezza_barra for pos in x], df['incassi_totali'], width=larghezza_barra, label="Incassi Totali", color='blue')
    ax.bar(x, df['costi_totali'], width=larghezza_barra, label="Costi Totali", color='red')
    ax.bar([pos + larghezza_barra for pos in x], df['margine_totale'], width=larghezza_barra, label="Margine Totale", color='green')

    # Etichette sugli assi
    ax.set_xlabel("Descrizione", fontsize=12)
    ax.set_ylabel("Quantità (€)", fontsize=12)
    ax.set_title("Confronto Incassi, Costi e Margine Totale", fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(df['descrizione'], rotation=45, ha="right")

    # Mostra la legenda
    ax.legend()

    # Mostra il grafico in Streamlit
    st.pyplot(fig)


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

    col1, col2, col3 = st.columns([1,1,1])
    with col1:
        st.metric("📈 Ricavi Totali (€)", f"{incassi_totali:,.0f}")
    with col2:
        st.metric("📈 Costi Totali (€)", f"{costi_totali:,.0f}")
    with col3:
        st.metric("📈 Margine Totale (€)", f"{margine_totale:,.0f}")

    col4, col5, col6 = st.columns([1,1,1])

    with col4,col5:
        st.write("### Grafico a Barre: Incassi, Costi e Margine")
        grafico_barre(filtered_df)
    with col6:
        st.metric("📈 Servizio con incassi maggiori", top3_incassi['descrizione'].iloc[0])
        st.metric("📈 (€)", top3_incassi['incassi_totali'].iloc[0])
        st.metric("📈 (€)", top3_incassi['costo_totale'].iloc[0])
        st.metric("📈 (€)", top3_incassi['margine_totale'].iloc[0])


menu = st.sidebar.selectbox("Navigazione", ["Carica File", "Dashboard"])

if menu == "Carica File":
    upload_file()
elif menu == "Dashboard":
    render_dashboard()
