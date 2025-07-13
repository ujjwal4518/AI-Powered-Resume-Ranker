import os
import spacy
from pdfminer.high_level import extract_text
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def extract_resume_text(path):
    try:
        return extract_text(path)
    except:
        return ""

def preprocess(text):
    doc = nlp(text.lower())
    tokens = [token.lemma_ for token in doc if token.is_alpha and not token.is_stop]
    return " ".join(tokens)

def process_resumes(filenames, upload_folder, jd_path):
    resumes_text = []
    for filename in filenames:
        path = os.path.join(upload_folder, filename)
        raw_text = extract_resume_text(path)
        processed = preprocess(raw_text)
        resumes_text.append(processed)

    with open(jd_path, 'r') as f:
        jd_raw = f.read()
    jd_processed = preprocess(jd_raw)

    all_docs = [jd_processed] + resumes_text
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_docs)

    jd_vector = tfidf_matrix[0]
    resume_vectors = tfidf_matrix[1:]

    scores = cosine_similarity(jd_vector, resume_vectors).flatten()
    return scores

def save_report(filenames, scores, output_path):
    df = pd.DataFrame({'Resume': filenames, 'Score': scores})
    df = df.sort_values(by='Score', ascending=False)
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    df.to_csv(output_path, index=False)
