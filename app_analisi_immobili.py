import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Configurazione della pagina
st.set_page_config(
    page_title="Dashboard Dati Immobiliari",
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
        usecols="A,B,C,D,E,F,G,H,L",
        engine="openpyxl"
    )

    data.columns = [
        'codice',
        'descrizione',
        'distribuzione_costi',
        'prezzo_vendita',
        'ore_uomo',
        'costo_personal',
        'costo_materiale_consumo',
        'noleggi_ammortamenti',
        'q.ty'
    ]
    data = data.dropna(subset=['codice'])

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

def render_dashboard():
    """Visualizza la dashboard con KPI, grafici e calcolo dinamico delle notti disponibili"""
    inject_custom_css()
    st.title("📊 Dashboard Dati immobiliari")

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

    # Sezione Filtri - Filtro Gerarchico Regione -> Provincia -> Comune
    with st.sidebar.expander("🔍 Filtro Dati"):
        st.markdown("### Filtra per Regione, Provincia e Comune")

        # Selezione Regione
        regione_scelta = st.selectbox(
            "Seleziona Regione",
            options=sorted(data['Regione'].dropna().unique()),
            key="regione_filter"
        )

        # Filtra le province in base alla regione selezionata
        province_filtrate = data[data['Regione'] == regione_scelta]['Provincia'].dropna().unique()
        provincia_scelta = st.selectbox(
            "Seleziona Provincia",
            options=sorted(province_filtrate),
            key="provincia_filter"
        )

        # Filtra i comuni in base alla provincia selezionata
        comuni_filtrati = data[
            (data['Regione'] == regione_scelta) & (data['Provincia'] == provincia_scelta)
        ]['Comune'].dropna().unique()
        comune_scelto = st.selectbox(
            "Seleziona Comune",
            options=sorted(comuni_filtrati),
            key="comune_filter"
        )

    # Sezione Filtro Date
    with st.sidebar.expander("📅 Filtra per Data"):
        st.markdown("### Seleziona un intervallo di date")

        # Trova la prima colonna con data
        colonne_data = [col for col in data.columns if "data" in col.lower() or "date" in col.lower()]
        
        if colonne_data:
            colonna_data = colonne_data[0]  # Usa la prima colonna data trovata
            data_min = data[colonna_data].min()
            data_max = data[colonna_data].max()

            # Selezione dell'intervallo di date
            data_inizio, data_fine = st.date_input(
                "Seleziona intervallo di date",
                [data_min, data_max],
                min_value=data_min,
                max_value=data_max
            )
        else:
            st.warning("⚠️ Nessuna colonna data trovata nel dataset.")
            data_inizio, data_fine = None, None

    # Mostra i dati filtrati
    st.write(f"Hai selezionato: **{regione_scelta}**, **{provincia_scelta}**, **{comune_scelto}**")

    # Filtra il dataset in base alla selezione
    data_filtrata = data[
        (data['Regione'] == regione_scelta) & 
        (data['Provincia'] == provincia_scelta) & 
        (data['Comune'] == comune_scelto)
    ]

    # Applica il filtro per data se presente
    if colonne_data and data_inizio and data_fine:
        data_filtrata = data_filtrata[
            (data_filtrata[colonna_data] >= pd.Timestamp(data_inizio)) &
            (data_filtrata[colonna_data] <= pd.Timestamp(data_fine))
        ]

    # Mostra i dati filtrati
    st.dataframe(data_filtrata)

# Esegui la funzione principale
if __name__ == "__main__":
    render_dashboard()
