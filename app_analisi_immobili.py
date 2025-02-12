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

    incassi_totali = data['incassi_totali'].sum
    costi_totali = data['costo_totale'].sum
    margine_totale = data['margine_totale'].sum

    top3_incassi = data.nlargest(3,'incassi_totali')
    top3_margine = data.nlargest(3, 'margine_totale')
    

    return data, incassi_totali, costi_totali, margine_totale




def render_dashboard():
    """Visualizza la dashboard con KPI, grafici e calcolo dinamico delle notti disponibili"""
    inject_custom_css()
    st.title("📊 Dashboard Cabina estetica")
    upload_file()

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
    
    filtered_df, incassi_totali, costi_totali, margine_totale = calcolo_kpi(filtered_df)

    # Mostra i dati filtrati
    st.dataframe(filtered_df)

    


# Esegui la funzione principale
if __name__ == "__main__":
    render_dashboard()
