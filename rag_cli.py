#!/usr/bin/env python3
import os
import argparse
import networkx as nx
import google.generativeai as genai
from typing import List, Dict
import json
import configparser
from docling.document_converter import DocumentConverter

def load_config(config_path: str = "config.ini") -> str:
    """Charge la configuration depuis le fichier config.ini."""
    config = configparser.ConfigParser()
    
    # Si le fichier n'existe pas, le créer avec une section par défaut
    if not os.path.exists(config_path):
        config['DEFAULT'] = {
            'api_key': 'VOTRE_CLE_API_ICI',
            'model': 'gemini-1.5-pro'
        }
        with open(config_path, 'w') as f:
            config.write(f)
        print(f"Fichier de configuration créé à {config_path}")
        print("Veuillez éditer ce fichier pour y mettre votre clé API")
        exit(1)
    
    # Lire la configuration
    config.read(config_path)
    api_key = config['DEFAULT'].get('api_key')
    
    if not api_key or api_key == 'VOTRE_CLE_API_ICI':
        print("Erreur: Clé API non configurée")
        print(f"Veuillez éditer le fichier {config_path} pour y mettre votre clé API")
        exit(1)
    
    return api_key

def convert_pdf_to_markdown(pdf_path: str) -> str:
    """Convertit un fichier PDF en markdown en utilisant Gemini."""
    try:
        # Lire le contenu du PDF
        with open(pdf_path, 'rb') as f:
            pdf_content = f.read()
        
        # Configurer Gemini
        api_key = load_config()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        
        # Créer le prompt pour la conversion
        prompt = """Convertis le contenu de ce PDF en markdown. 
        - Conserve la structure du document (titres, sous-titres, paragraphes)
        - Formate correctement les listes et les tableaux
        - Conserve les images et les légendes
        - Utilise le formatage markdown approprié (# pour les titres, * pour l'italique, etc.)
        - Assure-toi que le texte est bien structuré et lisible
        - Si le document contient des images, décris-les de manière appropriée
        """
        
        # Envoyer le PDF à Gemini
        response = model.generate_content([prompt, pdf_content])
        
        # Retourner le contenu markdown
        return response.text
    except Exception as e:
        print(f"Erreur lors de la conversion de {pdf_path}: {str(e)}")
        raise

def convert_new_pdfs(directory_path: str):
    """Convertit uniquement les nouveaux fichiers PDF en markdown."""
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire {directory_path} n'existe pas")
    
    print(f"Recherche des nouveaux fichiers PDF dans {directory_path}...")
    pdf_files = [f for f in os.listdir(directory_path) if f.endswith('.pdf')]
    
    for filename in pdf_files:
        pdf_path = os.path.join(directory_path, filename)
        markdown_path = os.path.join(directory_path, filename.replace('.pdf', '.md'))
        
        # Vérifier si le fichier markdown existe déjà
        if not os.path.exists(markdown_path):
            print(f"Traitement de {filename}...")
            try:
                markdown_content = convert_pdf_to_markdown(pdf_path)
                with open(markdown_path, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"✓ {filename} converti avec succès")
            except Exception as e:
                print(f"✗ Erreur lors du traitement de {filename}: {str(e)}")
        else:
            print(f"✓ Fichier markdown existant trouvé pour {filename}")

def load_knowledge_graph(graph_path: str) -> nx.DiGraph:
    """Charge le graphe de connaissances depuis le fichier GraphML."""
    if not os.path.exists(graph_path):
        raise FileNotFoundError(f"Le fichier {graph_path} n'existe pas")
    return nx.read_graphml(graph_path)

def extract_relevant_nodes(graph: nx.DiGraph, query: str) -> List[str]:
    """Extrait les nœuds pertinents du graphe en fonction de la requête."""
    relevant_nodes = []
    query_terms = query.lower().split()
    
    for node in graph.nodes():
        node_lower = str(node).lower()
        if any(term in node_lower for term in query_terms):
            relevant_nodes.append(node)
    
    return relevant_nodes

def get_context_from_graph(graph: nx.DiGraph, relevant_nodes: List[str]) -> str:
    """Extrait le contexte pertinent du graphe."""
    context = []
    
    for node in relevant_nodes:
        # Ajouter le nœud et ses attributs
        node_data = graph.nodes[node]
        context.append(f"Concept: {node}")
        if 'type' in node_data:
            context.append(f"Type: {node_data['type']}")
        
        # Ajouter les relations sortantes
        for neighbor in graph.successors(node):
            edge_data = graph.get_edge_data(node, neighbor)
            if edge_data and 'relation' in edge_data:
                context.append(f"Relation: {node} {edge_data['relation']} {neighbor}")
    
    return "\n".join(context)

def get_context_from_markdown(directory_path: str) -> str:
    """Extrait le contexte en concaténant tous les fichiers markdown."""
    context = []
    
    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Le répertoire {directory_path} n'existe pas")
    
    print(f"Recherche des fichiers markdown dans {directory_path}...")
    md_files = [f for f in os.listdir(directory_path) if f.endswith('.md')]
    print(f"Fichiers markdown trouvés: {md_files}")
    
    for filename in md_files:
        file_path = os.path.join(directory_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                context.append(f"\n=== Contenu de {filename} ===\n{content}\n")
                print(f"✓ Fichier {filename} lu avec succès")
        except Exception as e:
            print(f"✗ Erreur lors de la lecture de {filename}: {str(e)}")
    
    if not context:
        raise ValueError("Aucun fichier markdown trouvé dans le répertoire")
    
    return "\n".join(context)

def list_available_models(api_key: str):
    """Liste les modèles disponibles."""
    genai.configure(api_key=api_key)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Modèle disponible: {m.name}")

def setup_gemini(api_key: str):
    """Configure l'API Gemini."""
    genai.configure(api_key=api_key)
    # Utiliser le modèle Gemini 1.5 Pro
    return genai.GenerativeModel('gemini-1.5-pro')

def generate_response(model, query: str, context: str) -> str:
    """Génère une réponse en utilisant Gemini avec le contexte du graphe."""
    prompt = f"""Contexte:
{context}

Question: {query}

En utilisant le contexte fourni, réponds à la question de manière précise et concise.
Si le contexte ne contient pas suffisamment d'informations, indique-le clairement.
Formatte ta réponse comme un texte continu et naturel, sans utiliser de puces ou de numérotation.
Évite les phrases trop courtes et les répétitions."""

    response = model.generate_content(prompt)
    return response.text

def main():
    parser = argparse.ArgumentParser(description='Système RAG utilisant Gemini et un graphe de connaissances')
    parser.add_argument('--graph', help='Chemin vers le fichier GraphML du graphe de connaissances')
    parser.add_argument('--api-key', help='Clé API Gemini (optionnel si configurée dans config.ini)')
    parser.add_argument('--query', help='Question à poser')
    parser.add_argument('--list-models', action='store_true', help='Liste les modèles disponibles')
    parser.add_argument('--md', action='store_true', help='Utiliser la concaténation des fichiers markdown au lieu du graphe')
    parser.add_argument('--config', default='config.ini', help='Chemin vers le fichier de configuration')
    parser.add_argument('--convert-only', action='store_true', help='Convertir uniquement les nouveaux fichiers PDF en markdown')
    
    args = parser.parse_args()
    
    try:
        if args.convert_only:
            if not args.graph:
                parser.error("L'argument --graph est requis pour spécifier le répertoire contenant les fichiers PDF")
            convert_new_pdfs(args.graph)
            return
            
        # Charger la clé API depuis le fichier de configuration
        api_key = args.api_key if args.api_key else load_config(args.config)
        
        if args.list_models:
            list_available_models(api_key)
            return
            
        if not args.query:
            parser.error("L'argument --query est requis")
            
        if args.md:
            if not args.graph:
                parser.error("L'argument --graph est requis pour spécifier le répertoire contenant les fichiers markdown")
            context = get_context_from_markdown(args.graph)
        else:
            if not args.graph:
                parser.error("L'argument --graph est requis pour spécifier le fichier GraphML")
            # Charger le graphe de connaissances
            graph = load_knowledge_graph(args.graph)
            
            # Extraire les nœuds pertinents
            relevant_nodes = extract_relevant_nodes(graph, args.query)
            
            if not relevant_nodes:
                print("Aucune information pertinente trouvée dans le graphe de connaissances.")
                return
            
            # Extraire le contexte
            context = get_context_from_graph(graph, relevant_nodes)
        
        # Configurer Gemini
        model = setup_gemini(api_key)
        
        # Générer la réponse
        response = generate_response(model, args.query, context)
        
        print("\n" + "="*80)
        print("RÉPONSE:")
        print("="*80)
        print(response)
        print("="*80)
        
        print("\nContexte utilisé:")
        print("-"*80)
        print(context)
        print("-"*80)
        
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    main() 