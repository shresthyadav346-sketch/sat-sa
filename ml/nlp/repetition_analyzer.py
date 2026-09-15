"""
NLP Repetition Analyzer.
Uses TF-IDF and Cosine Similarity to detect template-driven, repetitive triage notes.
100% offline and deterministic.
"""

from typing import Dict, Any, List, Tuple
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session

from backend.app.models.alert_case import Case, Investigation
from backend.app.config import settings

class InvestigationRepetitionAnalyzer:
    def __init__(self, similarity_threshold: float = None):
        self.similarity_threshold = similarity_threshold or settings.TFIDF_SIMILARITY_THRESHOLD
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=500,
            ngram_range=(1, 2)
        )
        
    def analyze_cse_investigations(self, db: Session, cse_id: str) -> Dict[str, Any]:
        """
        Analyze all investigation texts for a CSE.
        Returns:
        - repetition_score (0.0 to 1.0)
        - top_repetitive_texts (samples)
        - sample_case_ids (affected cases)
        """
        records = (
            db.query(Investigation.case_id, Investigation.description)
            .join(Case, Investigation.case_id == Case.case_id)
            .filter(Case.cse_id == cse_id)
            .all()
        )
        
        if len(records) < 10:
            return {
                "repetition_score": 0.0,
                "top_repetitive_texts": [],
                "sample_case_ids": []
            }
            
        case_ids = [r[0] for r in records]
        texts = [r[1] or "" for r in records]
        
        # Count exact duplicates first
        text_counts = Counter(texts)
        most_common_texts = text_counts.most_common(3)
        
        # Sample for pairwise matrix (up to 250 texts for rapid local calculation)
        sample_size = min(250, len(texts))
        sample_texts = texts[:sample_size]
        sample_case_ids = case_ids[:sample_size]
        
        try:
            tfidf_matrix = self.vectorizer.fit_transform(sample_texts)
            sim_matrix = cosine_similarity(tfidf_matrix)
            
            # Mask diagonal (self-similarity)
            np.fill_diagonal(sim_matrix, 0.0)
            
            # Fraction of entries exceeding similarity threshold
            n_pairs = sample_size * (sample_size - 1)
            high_sim_pairs = np.sum(sim_matrix >= self.similarity_threshold)
            
            repetition_ratio = float(high_sim_pairs / n_pairs) if n_pairs > 0 else 0.0
            
            # Find case IDs involved in high-similarity pairs
            high_sim_indices = set(np.where(sim_matrix >= self.similarity_threshold)[0])
            affected_case_ids = [sample_case_ids[idx] for idx in list(high_sim_indices)[:15]]
            
            top_texts = [text for text, count in most_common_texts if count > 2]
            
            return {
                "repetition_score": round(repetition_ratio, 3),
                "top_repetitive_texts": top_texts,
                "sample_case_ids": affected_case_ids
            }
        except Exception as e:
            # Fallback to exact match frequency
            exact_rep_ratio = (
                sum(cnt for txt, cnt in text_counts.items() if cnt > 3) / len(texts)
            ) if texts else 0.0
            return {
                "repetition_score": round(exact_rep_ratio, 3),
                "top_repetitive_texts": [t for t, c in most_common_texts if c > 2],
                "sample_case_ids": case_ids[:10]
            }
