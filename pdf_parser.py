# pdf_parser.py
import ssl
import os
import networkx as nx
import spacy
import subprocess
from collections import defaultdict
ssl._create_default_https_context = ssl._create_unverified_context

from docling.document_converter import DocumentConverter

# Charger le modèle spaCy pour le français
try:
    nlp = spacy.load("fr_core_news_sm")
except OSError:
    print("Installation du modèle spaCy pour le français...")
    subprocess.run(["python", "-m", "spacy", "download", "fr_core_news_sm"])
    nlp = spacy.load("fr_core_news_sm")

def extract_entities_and_relations(text):
    """
    Extrait les entités et relations d'un texte en utilisant spaCy.
    """
    doc = nlp(text)
    entities = []
    relations = []
    
    # Extraire les entités nommées
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))
    
    # Extraire les relations basiques (sujet-verbe-objet)
    for sent in doc.sents:
        for token in sent:
            if token.dep_ in ["nsubj", "dobj"]:
                head = token.head
                if head.pos_ == "VERB":
                    relations.append((token.text, head.text, token.dep_))
    
    return entities, relations

def build_knowledge_graph(markdown_files):
    """
    Construit un graphe de connaissances à partir des fichiers markdown.
    """
    G = nx.DiGraph()
    
    for file_path in markdown_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            entities, relations = extract_entities_and_relations(content)
            
            # Ajouter les entités au graphe
            for entity, label in entities:
                G.add_node(entity, type=label)
            
            # Ajouter les relations au graphe
            for subj, verb, rel_type in relations:
                G.add_edge(subj, verb, relation=rel_type)
    
    return G

def convert_pdf_to_markdown(pdf_path):
    """
    Convertit un fichier PDF en markdown en utilisant docling.
    """
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()

def process_directory(directory_path):
    """
    Traite tous les fichiers PDF dans le répertoire spécifié et construit un graphe de connaissances.
    Utilise les fichiers markdown existants si disponibles.
    """
    markdown_files = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(directory_path, filename)
            markdown_path = os.path.join(directory_path, filename.replace('.pdf', '.md'))
            
            # Vérifier si le fichier markdown existe déjà
            if os.path.exists(markdown_path):
                print(f"✓ Fichier markdown existant trouvé pour {filename}")
                markdown_files.append(markdown_path)
            else:
                print(f"Traitement de {filename}...")
                try:
                    markdown_content = convert_pdf_to_markdown(pdf_path)
                    with open(markdown_path, 'w', encoding='utf-8') as f:
                        f.write(markdown_content)
                    markdown_files.append(markdown_path)
                    print(f"✓ {filename} converti avec succès")
                except Exception as e:
                    print(f"✗ Erreur lors du traitement de {filename}: {str(e)}")
    
    # Construire le graphe de connaissances
    if markdown_files:
        print("\nConstruction du graphe de connaissances...")
        knowledge_graph = build_knowledge_graph(markdown_files)
        
        # Sauvegarder le graphe
        graph_path = os.path.join(directory_path, "knowledge_graph.graphml")
        nx.write_graphml(knowledge_graph, graph_path)
        print(f"✓ Graphe de connaissances sauvegardé dans {graph_path}")
        
        # Afficher quelques statistiques
        print(f"\nStatistiques du graphe:")
        print(f"- Nombre de nœuds: {knowledge_graph.number_of_nodes()}")
        print(f"- Nombre de relations: {knowledge_graph.number_of_edges()}")
        
        return knowledge_graph
    return None

if __name__ == "__main__":
    # Exemple d'utilisation
    directory_path = "./cours_psychologie"
    knowledge_graph = process_directory(directory_path)
