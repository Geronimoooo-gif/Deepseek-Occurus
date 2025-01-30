import streamlit as st
import requests
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd

# Télécharger les ressources nécessaires de NLTK
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')  # Optionnel, mais utile pour des analyses avancées
nltk.download('wordnet')  # Optionnel, mais utile pour des analyses avancées

# Télécharger le tokenizer Punkt pour le français
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

stop_words = set(stopwords.words('french'))

# Fonction pour récupérer le contenu HTML d'une URL
def fetch_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vérifie si la requête a réussi
        return response.text
    except requests.exceptions.RequestException as e:
        st.error(f"Erreur lors de la récupération de l'URL {url}: {e}")
        return None

# Fonction pour extraire le texte du <body>
def extract_body_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    body = soup.find('body')
    if body:
        return body.get_text(separator=' ', strip=True)
    return ""

# Fonction pour analyser sémantiquement le texte
def analyze_text(text):
    words = nltk.word_tokenize(text.lower())
    words = [word for word in words if word.isalnum() and word not in stop_words]
    word_freq = Counter(words)
    return word_freq

# Fonction pour évaluer un site en fonction de la liste de mots-clés
def evaluate_site(word_freq, target_freq):
    score = 0
    for word, freq in target_freq.items():
        if word in word_freq:
            score += min(freq, word_freq[word])
    total_possible = sum(target_freq.values())
    return (score / total_possible) * 100

# Interface Streamlit
st.title("Analyse Sémantique pour le SEO")

# Saisie du mot-clé
keyword = st.text_input("Entrez le mot-clé sur lequel vous souhaitez positionner votre article :")

# Saisie des URL des sites
st.write("Entrez les URL des 3 premiers sites de la SERP :")
url1 = st.text_input("URL du site en position 1 :")
url2 = st.text_input("URL du site en position 2 :")
url3 = st.text_input("URL du site en position 3 :")

if st.button("Analyser"):
    if keyword and url1 and url2 and url3:
        # Récupérer le contenu HTML des sites
        html1 = fetch_html(url1)
        html2 = fetch_html(url2)
        html3 = fetch_html(url3)

        if html1 and html2 and html3:
            # Extraire le texte du <body>
            text1 = extract_body_text(html1)
            text2 = extract_body_text(html2)
            text3 = extract_body_text(html3)

            # Analyser sémantiquement les textes
            freq1 = analyze_text(text1)
            freq2 = analyze_text(text2)
            freq3 = analyze_text(text3)

            # Générer la liste de mots-clés cible
            target_freq = freq1 + freq2 + freq3

            # Afficher la liste de mots-clés
            st.write("Liste de mots-clés à ajouter dans l'article :")
            target_df = pd.DataFrame(target_freq.most_common(), columns=['Mot', 'Fréquence'])
            st.dataframe(target_df)

            # Évaluer chaque site
            score1 = evaluate_site(freq1, target_freq)
            score2 = evaluate_site(freq2, target_freq)
            score3 = evaluate_site(freq3, target_freq)

            st.write(f"Note du site 1 : {score1:.2f}/100")
            st.write(f"Note du site 2 : {score2:.2f}/100")
            st.write(f"Note du site 3 : {score3:.2f}/100")

            # Exporter l'analyse au format CSV
            export_df = pd.DataFrame({
                'Site': ['Site 1', 'Site 2', 'Site 3'],
                'URL': [url1, url2, url3],
                'Note': [score1, score2, score3]
            })
            csv = export_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Exporter l'analyse au format CSV",
                data=csv,
                file_name='analyse_seo.csv',
                mime='text/csv',
            )
        else:
            st.error("Impossible de récupérer le contenu des sites. Vérifiez les URL.")
    else:
        st.error("Veuillez remplir tous les champs.")
