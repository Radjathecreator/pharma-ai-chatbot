# 💊 Pharma-IA : Assistant Intelligent Multimodal pour la Santé

Ce projet a été réalisé dans le cadre du **Master 2 Data Analytics & Artificial Intelligence**. 

L'objectif est de concevoir une application web intelligente capable d'aider les utilisateurs à comprendre les notices pharmaceutiques et à analyser visuellement des emballages de médicaments, tout en effectuant une **analyse comparative obligatoire** entre deux modes d'intégration de l'IA : les API Cloud et les modèles Open Source locaux.

---

## 🎯 Contexte Métier & Fonctionnalités

Le domaine retenu est la **pharmacie et l'aide informationnelle médicale générale**. L'application propose un Chatbot Avancé implémentant deux approches distinctes :

1. **Approche 1 (Fournisseur API Cloud) :** Intégration du modèle multimodal de pointe `gemini-2.5-flash` permettant de traiter simultanément les questions textuelles et les images (scans d'emballages) avec un suivi des performances et du coût des tokens en temps réel.
2. **Approche 2 (Modèles Open Source Hugging Face) :** Exécution locale de modèles spécialisés via la bibliothèque `transformers` :
   - Résumé automatique de notices avec `facebook/bart-large-cnn` (Architecture Encodeur-Décodeur).
   - Description d'images de médicaments avec `Salesforce/blip-image-captioning-base`.
   - Pipeline textuel de réponse avec `google/flan-t5-base`.

---

## 📊 Critères de l'Analyse Comparative

L'application intègre un **Tableau de Bord de Performance** permettant de comparer en direct :
- La **qualité et pertinence** des réponses (Modèle généraliste Cloud vs Modèles spécialisés locaux).
- Le **temps de réponse / d'inférence** (en secondes).
- La **consommation des ressources** et la gestion des coûts (coûts financiers réels basés sur les tokens consommés).

---
