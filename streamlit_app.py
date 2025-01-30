import streamlit as st
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords
from collections import Counter
import pandas as pd

# Télécharger les stopwords de NLTK
nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

# Fonction pour extraire le texte d'un contenu HTML
def extract_text(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    text = soup.get_text()
    return text

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

# Saisie des contenus HTML des sites
st.write("Collez le contenu HTML des 3 premiers sites de la SERP :")
html1 = st.text_area("Site en position 1 :")
html2 = st.text_area("Site en position 2 :")
html3 = st.text_area("Site en position 3 :")

if st.button("Analyser"):
    if keyword and html1 and html2 and html3:
        # Extraire le texte des contenus HTML
        text1 = extract_text(html1)
        text2 = extract_text(html2)
        text3 = extract_text(html3)

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
        st.error("Veuillez remplir tous les champs.")
