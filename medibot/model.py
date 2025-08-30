import json
import logging
from typing import List, Dict, Optional

class SymptomMatcher:
    """AI-powered symptom matching engine for disease identification"""
    
    def __init__(self, diseases_data: List[Dict]):
        """Initialize with diseases database"""
        self.diseases_data = diseases_data
        self.symptom_keywords = self._build_symptom_keywords()
        
    def _build_symptom_keywords(self) -> set:
        """Build a comprehensive set of symptom keywords from the database"""
        keywords = set()
        for disease in self.diseases_data:
            for symptom in disease.get('symptoms', []):
                keywords.add(symptom.lower())
                # Add common variations
                if 'ache' in symptom:
                    keywords.add(symptom.replace('ache', 'pain'))
                if 'pain' in symptom:
                    keywords.add(symptom.replace('pain', 'ache'))
        
        # Add common symptom synonyms
        symptom_synonyms = {
            'temperature': 'fever',
            'runny nose': 'nasal congestion',
            'stuffy nose': 'nasal congestion',
            'stomach ache': 'stomach pain',
            'tummy ache': 'stomach pain',
            'belly ache': 'stomach pain',
            'sick': 'nausea',
            'throwing up': 'vomiting',
            'sneezing': 'sneeze',
            'coughing': 'cough',
            'tired': 'fatigue',
            'exhausted': 'fatigue',
            'drowsy': 'fatigue'
        }
        
        for synonym, standard in symptom_synonyms.items():
            keywords.add(synonym)
            
        return keywords
    
    def extract_symptoms(self, message: str) -> List[str]:
        """Extract symptoms from user message using keyword matching"""
        message_lower = message.lower()
        detected_symptoms = []
        
        # Direct keyword matching
        for keyword in self.symptom_keywords:
            if keyword in message_lower:
                detected_symptoms.append(keyword)
        
        # Pattern-based extraction for common phrases
        symptom_patterns = {
            'fever': ['hot', 'temperature', 'feverish', 'burning up'],
            'headache': ['head hurts', 'head pain', 'migraine'],
            'stomach pain': ['stomach hurts', 'belly pain', 'tummy pain', 'stomach ache'],
            'sore throat': ['throat hurts', 'painful throat', 'throat pain'],
            'cough': ['coughing', 'hacking'],
            'nausea': ['feel sick', 'queasy', 'sick to stomach'],
            'fatigue': ['tired', 'exhausted', 'weak', 'no energy'],
            'runny nose': ['stuffy nose', 'blocked nose', 'congested'],
            'sneezing': ['sneezing', 'achoo'],
            'chills': ['cold', 'shivering', 'shaking']
        }
        
        for symptom, patterns in symptom_patterns.items():
            for pattern in patterns:
                if pattern in message_lower and symptom not in detected_symptoms:
                    detected_symptoms.append(symptom)
        
        return detected_symptoms
    
    def match_disease(self, user_symptoms: List[str]) -> Optional[Dict]:
        """Match user symptoms to diseases and return best match"""
        if not user_symptoms:
            return None
        
        best_match = None
        best_score = 0
        
        for disease in self.diseases_data:
            score = self._calculate_match_score(user_symptoms, disease['symptoms'])
            
            if score > best_score:
                best_score = score
                best_match = disease
        
        # Only return match if confidence is high enough
        if best_score >= 0.3:  # At least 30% match
            return best_match
        
        return None
    
    def _calculate_match_score(self, user_symptoms: List[str], disease_symptoms: List[str]) -> float:
        """Calculate matching score between user symptoms and disease symptoms"""
        if not user_symptoms or not disease_symptoms:
            return 0.0
        
        user_symptoms_lower = [s.lower() for s in user_symptoms]
        disease_symptoms_lower = [s.lower() for s in disease_symptoms]
        
        # Count exact matches
        exact_matches = 0
        for user_symptom in user_symptoms_lower:
            if user_symptom in disease_symptoms_lower:
                exact_matches += 1
        
        # Count partial matches (synonyms and related terms)
        partial_matches = 0
        synonym_map = {
            'fever': ['temperature', 'hot', 'feverish'],
            'headache': ['head pain', 'migraine'],
            'stomach pain': ['stomach ache', 'belly pain', 'abdominal pain'],
            'sore throat': ['throat pain', 'painful throat'],
            'runny nose': ['nasal congestion', 'stuffy nose'],
            'fatigue': ['tired', 'exhausted', 'weakness'],
            'nausea': ['sick', 'queasy'],
            'chills': ['cold', 'shivering']
        }
        
        for user_symptom in user_symptoms_lower:
            for disease_symptom in disease_symptoms_lower:
                if user_symptom != disease_symptom:  # Avoid double counting exact matches
                    # Check if they are synonyms
                    for canonical, synonyms in synonym_map.items():
                        if ((user_symptom == canonical and disease_symptom in synonyms) or
                            (disease_symptom == canonical and user_symptom in synonyms) or
                            (user_symptom in synonyms and disease_symptom in synonyms)):
                            partial_matches += 0.5
                            break
        
        # Calculate score as weighted average
        total_matches = exact_matches + partial_matches
        max_possible_matches = max(len(user_symptoms), len(disease_symptoms))
        
        # Boost score if user has multiple matching symptoms
        if exact_matches >= 2:
            total_matches *= 1.2
        
        score = total_matches / max_possible_matches
        
        # Ensure score doesn't exceed 1.0
        return min(score, 1.0)
    
    def get_disease_info(self, disease_name: str) -> Optional[Dict]:
        """Get detailed information about a specific disease"""
        for disease in self.diseases_data:
            if disease['disease'].lower() == disease_name.lower():
                return disease
        return None
