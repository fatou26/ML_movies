#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import font
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import difflib

# ==========================================
# PARTIE 1 : BACKEND (LOGIQUE)
# ==========================================

# --- DONNÉES DE TEST (À SUPPRIMER/COMMENTER EN PRODUCTION) ---
# Ceci est un jeu de données simple pour que le code soit immédiatement exécutable.
data = {
    'title': [
        'Aladdin', 'Le Roi Lion', 'La Reine des Neiges', 'Toy Story', 
        'Titanic', 'Avatar', 'Star Wars', 'Avengers', 
        'Pulp Fiction', 'Le Parrain', 'Inception', 'Interstellar',
        'Le Fabuleux Destin d\'Amélie Poulain', 'Le Seigneur des Anneaux',
        'Harry Potter', 'Spider-Man', 'Jurassic Park'
    ],
    # 'features' est la colonne centrale pour le calcul de similarité. 
    # Elle doit contenir les mots-clés, genres, acteurs, etc., combinés.
    'features': [
        'animation disney magie', 'animation disney animaux afrique', 'animation disney glace chanson', 'animation pixar jouets',
        'romance drame bateau dicaprio', 'scifi action espace cameron', 'scifi espace guerre lucas', 'action superheros marvel',
        'crime drame tarantino', 'crime mafia drame', 'scifi reve nolan', 'scifi espace temps nolan',
        'romance france paris', 'fantasy guerre anneau',
        'fantasy magie sorcier ecole', 'action superheros araignee', 'aventure dinosaure parc'
    ]
}
df = pd.DataFrame(data) 
# ------------------------------------------------------------- 
# --- CHARGEMENT DE TA BASE DE DONNÉES RÉELLE ---
# VEUILLEZ DÉCOMMENTER LA LIGNE APPROPRIÉE CI-DESSOUS ET AJUSTER LE NOM DE FICHIER.

# 1. Chargement à partir d'un fichier CSV :
# df = pd.read_csv('nom_de_ton_fichier.csv') 

# 2. Chargement si ta fonction précédente génère directement le DataFrame :
# df = ta_fonction_qui_génère_le_dataframe()

# ------------------------------------------------------------- 

# VÉRIFICATION IMPORTANTE : Assurez-vous que le DataFrame 'df' contient bien les colonnes 'title' et 'features' (ou adaptez 'features' ci-dessous).
count = CountVectorizer()
count_matrix = count.fit_transform(df['features']) # Utilise la colonne de fonctionnalités
cosine_sim = cosine_similarity(count_matrix, count_matrix) # Matrice de similarité créée une fois

# Création d'une Serie d'indices pour retrouver rapidement le film par son titre (clé de recherche)
indices = pd.Series(df.index, index=df['title'].str.lower()).drop_duplicates()
all_titles = df['title'].tolist() # Liste simple de tous les titres pour la recherche approximative

def get_recommendations_logic(title, cosine_sim=cosine_sim):
    """
    Fonction principale de recommandation.
    Elle prend le titre en entrée et utilise les objets 'df', 'indices' et 'cosine_sim' 
    calculés au-dessus (Partie 1) pour retourner les résultats.
    
    Retourne toujours : (booléen: Succès/Échec, liste: Recommandations ou Suggestions)
    """
    title_lower = title.strip().lower()

    # CAS 1 : Correspondance exacte du titre trouvé dans la BDD (df)
    if title_lower in indices:
        idx = indices[title_lower]
        
        # Récupération des scores de similarité pour le film à l'index 'idx'
        sim_scores = list(enumerate(cosine_sim[idx])) 
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:] # On retire le film lui-même (indice 0)
        
        movie_indices = [i[0] for i in sim_scores]
        # Retourne True (succès) et la liste des titres recommandés
        return True, df['title'].iloc[movie_indices].tolist()

    # CAS 2 : Titre introuvable -> Recherche de suggestions
    else:
        # Recherche 1: Match partiel (ex: "le roi" trouve "Le Roi Lion")
        match_partiel = [t for t in all_titles if title_lower in t.lower()]
        
        # Recherche 2: Match flou (ex: "Aladin" trouve "Aladdin")
        match_flou = difflib.get_close_matches(title, all_titles, n=5, cutoff=0.4)
        
        # Combinaison et nettoyage (suppression des doublons)
        toutes_suggestions = list(set(match_partiel + match_flou))
        toutes_suggestions.sort(key=len)
        
        # Retourne False (échec/suggestion) et la liste des titres suggérés
        return False, toutes_suggestions[:10]

# ==========================================
# PARTIE 2 : FRONTEND (DESIGN DYNAMIQUE)
# ==========================================

# --- PALETTE ---
COULEUR_FOND = "#121212"       # Noir profond (plus élégant que le gris)
COULEUR_BLOC_SAISIE = "#B71C1C" # Rouge sombre/Vif (Style Netflix/Cinéma)
COULEUR_ZONE_LISTE = "#1E1E1E" # Gris foncé pour la liste
COULEUR_TEXTE_BLANC = "#FFFFFF"
COULEUR_JAUNE_IMDB = "#F5C518" 
COULEUR_BOUTON = "#E0E0E0"
COULEUR_BOUTON_HOVER = "#FFFFFF"

def lancer_recherche_gui(entree_film, entree_nombre, liste_widget, statut_label):
    film_input = entree_film.get()
    if not film_input.strip(): return 
    try:
        nb_films = int(entree_nombre.get())
    except ValueError:
        nb_films = 10 
        
    succes, resultats = get_recommendations_logic(film_input)
    liste_widget.delete(0, tk.END)
    
    if succes:
        statut_label.config(text=f"Top {min(nb_films, len(resultats))} similaires à '{film_input}' :", fg=COULEUR_JAUNE_IMDB)
        for i, film in enumerate(resultats[:nb_films], 1):
            liste_widget.insert(tk.END, f"{i}. {film}")
    else:
        if resultats:
            statut_label.config(text=f"⚠️ Film introuvable. Vouliez-vous dire :", fg=COULEUR_JAUNE_IMDB)
            for film in resultats:
                liste_widget.insert(tk.END, f"{film}")
        else:
            statut_label.config(text=f"❌ Aucun résultat pour '{film_input}'", fg="red")

# Fonction pour l'effet de survol du bouton
def on_enter(e):
    e.widget['bg'] = COULEUR_BOUTON_HOVER
def on_leave(e):
    e.widget['bg'] = COULEUR_BOUTON

def creer_interface():
    root = tk.Tk()
    root.title("CinéMatch Assistant")
    root.geometry("750x800")
    root.config(bg=COULEUR_FOND)

    # Polices personnalisées
    font_titre = font.Font(family="Helvetica", size=22, weight="bold")
    font_label_bloc = font.Font(family="Arial", size=14, weight="bold")
    font_input = font.Font(family="Arial", size=14)
    font_resultat = font.Font(family="Helvetica", size=15, weight="bold")
    font_liste = font.Font(family="Verdana", size=13)

    # 1. EN-TÊTE
    tk.Label(root, text="🎬 CINE-MATCH", bg=COULEUR_FOND, fg="#E50914", font=font_titre).pack(pady=(20, 10))
    tk.Label(root, text="Trouvez votre prochain film préféré", bg=COULEUR_FOND, fg="gray", font=("Arial", 10)).pack(pady=(0, 20))

    # 2. BLOC ROUGE (ZONE DE COMMANDE)
    # On crée un Frame avec un fond rouge et une bordure (relief)
    frame_commandes = tk.Frame(root, bg=COULEUR_BLOC_SAISIE, bd=0, padx=20, pady=20)
    frame_commandes.pack(fill='x', padx=30, pady=10) # fill='x' pour prendre toute la largeur

    # -- Intérieur du Bloc Rouge --
    
    # Label Film
    tk.Label(frame_commandes, text="Quel film avez-vous aimé ?", bg=COULEUR_BLOC_SAISIE, fg=COULEUR_TEXTE_BLANC, font=font_label_bloc).pack(anchor='w')
    
    # Input Film (Large)
    entree_film = tk.Entry(frame_commandes, bg="white", fg="black", font=font_input, relief="flat")
    entree_film.pack(fill='x', pady=(5, 15), ipady=8) # ipady pour la hauteur interne
    
    # Conteneur pour "Nombre" et "Bouton" sur la même ligne pour gagner de la place
    frame_bas_bloc = tk.Frame(frame_commandes, bg=COULEUR_BLOC_SAISIE)
    frame_bas_bloc.pack(fill='x')
    
    # Partie Gauche : Nombre
    tk.Label(frame_bas_bloc, text="Nombre de films :", bg=COULEUR_BLOC_SAISIE, fg=COULEUR_TEXTE_BLANC, font=("Arial", 12, "bold")).pack(side=tk.LEFT)
    entree_nombre = tk.Entry(frame_bas_bloc, width=5, bg="white", fg="black", font=font_input, justify='center', relief="flat")
    entree_nombre.insert(0, "5")
    entree_nombre.pack(side=tk.LEFT, padx=10, ipady=5)

    # Partie Droite : Bouton
    btn = tk.Button(frame_bas_bloc, text="LANCER LA RECHERCHE  🔍", 
                    command=lambda: lancer_recherche_gui(entree_film, entree_nombre, liste_resultats, statut_label),
                    bg=COULEUR_BOUTON, fg="black", font=("Arial", 11, "bold"), relief="raised", cursor="hand2")
    btn.pack(side=tk.RIGHT, ipadx=10, ipady=5)
    
    # Effets de survol
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    # 3. ZONE RÉSULTATS
    statut_label = tk.Label(root, text="", bg=COULEUR_FOND, font=font_resultat)
    statut_label.pack(fill='x', padx=30, pady=(30, 10))
    
    # Frame Liste (Design type "Carte Sombre")
    frame_liste = tk.Frame(root, bg=COULEUR_ZONE_LISTE, bd=1, relief="solid")
    frame_liste.pack(padx=30, pady=(0, 30), fill='both', expand=True)
    
    scrollbar = tk.Scrollbar(frame_liste, bg=COULEUR_ZONE_LISTE)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    liste_resultats = tk.Listbox(frame_liste, bg=COULEUR_ZONE_LISTE, fg=COULEUR_TEXTE_BLANC, 
                                  font=font_liste, activestyle='none', 
                                  selectbackground=COULEUR_JAUNE_IMDB, selectforeground="black",
                                  yscrollcommand=scrollbar.set, bd=0, highlightthickness=0)
    
    liste_resultats.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
    scrollbar.config(command=liste_resultats.yview)

    root.mainloop()

if __name__ == "__main__":
    creer_interface()