import streamlit as st
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# ---------- NLTK setup ----------
try:
    nltk.download('punkt')
    nltk.download('punkt_tab')   # newer versions need this
    nltk.download('stopwords')
except:
    pass

# ---------- Function to extract text from PDF ----------
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    text = ""
    for page in pdf_reader.pages:
        if page.extract_text():
            text += page.extract_text() + " "
    return text

# ---------- Function to clean text ----------
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)  # keep only alphabets

    try:
        tokens = word_tokenize(text)  # preferred tokenizer
    except LookupError:
        # fallback if punkt/punkt_tab missing
        tokens = text.split()

    stop_words = set(stopwords.words('english'))
    filtered = [word for word in tokens if word not in stop_words and len(word) > 2]
    return filtered

# ---------- Streamlit App ----------
st.title("📄 Resume Analyzer with ATS Score")
st.write("Upload your Resume and Job Description to see ATS match score")

# Upload Resume
resume_file = st.file_uploader("Upload Resume PDF", type=["pdf"])

# Upload Job Description
jd_file = st.file_uploader("Upload Job Description (PDF) OR paste text below", type=["pdf"])
jd_text_input = st.text_area("Or paste Job Description here:")

if resume_file is not None:
    # Extract and clean Resume
    resume_text = extract_text_from_pdf(resume_file)
    resume_words = clean_text(resume_text)
    resume_counts = Counter(resume_words)

    st.subheader("📌 Resume Analysis")
    st.write(f"**Total Keywords Extracted:** {len(resume_words)}")

    # Top 10 keywords
    top_resume = resume_counts.most_common(10)
    st.write("**Top 10 Resume Keywords:**")
    st.write(top_resume)

    # Bar Chart
    st.subheader("📊 Resume Keywords Frequency")
    fig, ax = plt.subplots()
    ax.bar([x[0] for x in top_resume], [x[1] for x in top_resume])
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # Word Cloud
    st.subheader("☁️ Resume Word Cloud")
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(" ".join(resume_words))
    fig, ax = plt.subplots()
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)

    # ---------- Job Description Analysis ----------
    jd_text = ""
    if jd_file is not None:
        jd_text = extract_text_from_pdf(jd_file)
    elif jd_text_input.strip() != "":
        jd_text = jd_text_input

    st.subheader("📌 Job Description Analysis")
    if jd_text:
        jd_words = clean_text(jd_text)
        jd_counts = Counter(jd_words)

        st.write(f"**Total JD Keywords Extracted:** {len(jd_words)}")

        # Match keywords
        resume_set = set(resume_words)
        jd_set = set(jd_words)
        matched = resume_set.intersection(jd_set)
        missing = jd_set - resume_set

        # ATS Score
        ats_score = round((len(matched) / len(jd_set)) * 100, 2)
        st.subheader("📊 ATS Score")
        st.write(f"✅ Match Score: **{ats_score}%**")

        st.write("**Matched Keywords:**")
        st.write(list(matched)[:30])  # show first 30

        st.write("**Missing Keywords (Consider Adding):**")
        st.write(list(missing)[:30])  # show first 30
    else:
        st.warning("⚠️ Please upload or paste a Job Description to calculate ATS Score.")
