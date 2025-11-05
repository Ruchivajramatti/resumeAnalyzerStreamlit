from __future__ import annotations

from typing import List, Set
import re


def extract_entities(text: str) -> dict:
    """Very lightweight entity extraction using regex heuristics."""
    ents = {"EMAIL": [], "PHONE": [], "URL": []}
    ents["EMAIL"] = re.findall(r"[\w\.\-]+@[\w\.-]+", text)
    ents["PHONE"] = re.findall(r"(?:\+?\d[\s-]?)?(?:\(?\d{3}\)?[\s-]?)?\d{3}[\s-]?\d{4}", text)
    ents["URL"] = re.findall(r"https?://\S+", text)
    return ents


DEFAULT_SKILLS: Set[str] = {
    # Programming Languages
    "python","java","c","c++","javascript","typescript","go","rust","sql","r",
    # Libraries/Frameworks
    "flask","django","streamlit","react","node","pytorch","tensorflow","sklearn","spacy",
    # Data/Cloud/Tools
    "pandas","numpy","git","docker","kubernetes","azure","aws","gcp","linux",
    # NLP/ML
    "nlp","machine learning","deep learning","ner","tf-idf","cosine similarity",
}


def extract_skills(text: str, known_skills: Set[str] | None = None) -> List[str]:
    """Very simple skills extraction: case-insensitive match against a known set plus noun chunks heuristics."""
    ks = {s.lower() for s in (known_skills or DEFAULT_SKILLS)}
    lower = text.lower()
    found = {s for s in ks if s in lower}
    return sorted(found)


def keywords_tfidf(text: str, top_k: int = 15) -> List[str]:
    """Approximate keyword extraction using token frequency with stopword filtering."""
    if not text or not text.strip():
        return []
    text_l = text.lower()
    tokens = re.findall(r"[a-zA-Z]{2,}", text_l)
    stop = {
        'the','and','for','with','from','that','this','you','your','are','was','were','will','shall','would','could','should','have','has','had','but','not','can','our','their','his','her','its','they','them','him','she','he','we','i','to','in','of','on','at','by','as','or','an','a'
    }
    freq = {}
    for i, tok in enumerate(tokens):
        if tok in stop:
            continue
        freq[tok] = freq.get(tok, 0) + 1
        # bigrams simple boost
        if i+1 < len(tokens):
            bg = f"{tok} {tokens[i+1]}"
            if tokens[i+1] not in stop:
                freq[bg] = freq.get(bg, 0) + 1
    keywords = sorted(freq.items(), key=lambda x: (-x[1], x[0]))[:top_k]
    return [k for k,_ in keywords]
