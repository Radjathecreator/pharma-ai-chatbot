import streamlit as st
import os
from google import genai
from google.genai import types
from PIL import Image
import time

# --- CONFIGURATION DE LA PAGE (FRONT-END AVANCÉ) ---
st.set_page_config(
    page_title="Pharma-IA Intelligence",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé pour moderniser l'interface (Design épuré et pro)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .chat-timestamp { color: #888888; font-size: 0.8rem; margin-top: -5px; margin-bottom: 10px; }
    div[data-testid="stExpander"] { background-color: white; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- GESTION SÉCURISÉE DE LA CLÉ API ---
# On vérifie si la clé est dans l'environnement, sinon on propose de la saisir proprement
api_key = os.environ.get("GEMINI_API_KEY", "")

with st.sidebar:
    st.image("https://img.icons8.com/fluent/96/000000/pill.png", width=60)
    st.title("Configuration")
    st.subheader("🔑 Authentification")
    
    if not api_key:
        api_key = st.text_input("Entrez votre clé API Gemini :", type="password")
        if api_key:
            st.success("Clé API configurée pour cette session !")
    else:
        st.sidebar.success("✅ Clé API détectée dans le système.")
        
    st.markdown("---")
    st.subheader("📸 Analyse Visuelle")
    uploaded_file = st.file_uploader("Scanner un emballage / une notice :", type=["jpg", "jpeg", "png"])
    
    image_pil = None
    if uploaded_file:
        image_pil = Image.open(uploaded_file)
        st.image(image_pil, caption="Aperçu du scan", use_container_width=True)

# Blocage de l'application si aucune clé n'est fournie
if not api_key:
    st.info("💡 Veuillez configurer votre clé API Gemini dans la barre latérale pour lancer l'application.")
    st.stop()

# Initialisation du client officiel avec la bonne clé
client = genai.Client(api_key=api_key)
model_id = "gemini-2.5-flash"

# Instructions système pour fixer le comportement métier (Pharmacie)
PROMPT_SYSTEME = (
    "Tu es un assistant virtuel expert en pharmacie et santé. Ton rôle est d'aider les utilisateurs "
    "à comprendre les notices de médicaments, les dosages génériques ou à décrire un emballage. "
    "IMPORTANT : Rappelle toujours poliment que tu ne remplaces pas un médecin ou un pharmacien "
    "si la question devient trop critique ou touche à un diagnostic. Réponds de manière structurée avec des puces."
)

# --- STRUCTURE DE PAGE À ONGLETS (AVANCÉE) ---
tab_chat, tab_dashboard = st.tabs(["💬 Assistant Virtuel", "📊 Tableau de Bord & Métriques"])

# --- ONGLET 1 : CHATBOT PHARMACEUTIQUE ---
with tab_chat:
    st.markdown("### 💊 Assistant Informationnel Pharmacie")
    st.caption("Posez vos questions ou téléchargez une photo de votre boîte de médicament dans la barre latérale.")

    # Initialisation de l'historique
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "assistant", "content": "Bonjour ! Je suis votre assistant pharmacie. Comment puis-je vous renseigner aujourd'hui ?"}
        ]

    # Structure pour stocker les temps et tokens pour l'onglet Dashboard
    if "stats_temps" not in st.session_state: st.session_state.stats_temps = []
    if "stats_tokens" not in st.session_state: st.session_state.stats_tokens = []

    # Affichage de la discussion
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

# --- ZONE D'INTERACTION PRINCIPALE ---
if user_input := st.chat_input("Ex: Quels sont les effets secondaires du Paracétamol ?"):
    with st.chat_message("user"):
        st.write(user_input)
    
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.chat_message("assistant"):
        with st.spinner("Analyse clinique en cours..."):
            start_time = time.perf_counter()
            try:
                # 1. Préparation du contenu actuel (Multimodal ou Texte seul)
                if image_pil:
                    contenu_requete = [image_pil, user_input]
                else:
                    contenu_requete = user_input

                # 2. Filtrage et reconstruction de l'historique (Texte pur pour la mémoire de l'API)
                historique_api = []
                for msg in st.session_state.messages[:-1]:
                    role_gemini = "model" if msg["role"] == "assistant" else msg["role"]
                    historique_api.append(
                        types.Content(
                            role=role_gemini,
                            parts=[types.Part.from_text(text=str(msg["content"]))]
                        )
                    )

                # 3. Initialisation de la session de chat native Gemini
                chat = client.chats.create(
                    model=model_id,
                    history=historique_api,
                    config=types.GenerateContentConfig(
                        system_instruction=PROMPT_SYSTEME,
                        temperature=0.2,
                        max_output_tokens=800
                    )
                )
                
                # 4. Envoi de la requête réseau
                response = chat.send_message(contenu_requete)
                
                # 5. Extraction sécurisée du texte brut pour éliminer les bugs d'affichage
                answer = str(response.text)
                
                # Affichage propre dans Streamlit
                st.markdown(answer)
                
                # Sauvegarde dans la session utilisateur
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Enregistrement des données de performance pour ton onglet Dashboard
                inference_time = time.perf_counter() - start_time
                st.session_state.stats_temps.append(inference_time)
                if response.usage_metadata:
                    st.session_state.stats_tokens.append(response.usage_metadata.total_token_count)
                
                # Bandeau d'information technique
                st.markdown("---")
                st.caption(f"⏱️ Réponse générée en {inference_time:.2f}s avec {model_id}")
                
            except Exception as e:
                st.error(f"Une erreur est survenue lors de l'analyse : {e}")
                
# --- ONGLET 2 : ANALYSE COMPARATIVE & KPI (POUR LE RAPPORT M2) ---
with tab_dashboard:
    st.markdown("### 📊 Statistiques de performance en direct (Approche 1)")
    st.write("Ces données calculées en temps réel te permettent de remplir directement tes tableaux de comparaison pour ton livrable.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        dernier_temps = st.session_state.stats_temps[-1] if st.session_state.stats_temps else 0
        st.metric(label="Dernier Temps de Réponse (Cloud)", value=f"{dernier_temps:.2f} s", delta="- Local (BART/T5)")
        
    with col2:
        dernier_token = st.session_state.stats_tokens[-1] if st.session_state.stats_tokens else 0
        st.metric(label="Tokens Consommés (Dernier message)", value=f"{dernier_token} tokens")
        
    with col3:
        total_requetes = len(st.session_state.stats_temps)
        st.metric(label="Nombre total d'appels API", value=total_requetes)

    st.markdown("---")
    with st.expander("📝 Aide pour ton rapport de projet (Zineb Lamri)"):
        st.markdown("""
        **Points forts à noter dans ta conclusion pour l'Approche 1 :**
        - **Vitesse** : L'inférence sur le cloud de Google est souvent plus stable qu'un chargement de modèle lourd en CPU local.
        - **Multimodalité unifiée** : `gemini-2.5-flash` traite l'image de la boîte de médicament et la question textuelle en un seul appel, là où ton Approche 2 doit faire tourner deux modèles séparés (BLIP + FLAN-T5).
        - **Coût** : Consommation de tokens maîtrisée visible dans le tableau ci-dessus.
        """)
