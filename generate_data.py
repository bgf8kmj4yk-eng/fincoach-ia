"""
generate_data.py
----------------
Script de génération de données financières fictives pour FinCoach IA.
Génère un fichier 'transactions.csv' contenant 100 transactions réparties sur 3 mois.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_financial_data(output_file: str = "transactions.csv", num_records: int = 100) -> pd.DataFrame:
    """
    Génère un jeu de données de transactions financières et l'enregistre en CSV.
    
    Parameters:
        output_file (str): Chemin du fichier CSV de sortie.
        num_records (int): Nombre total de transactions à générer (défaut: 100).
        
    Returns:
        pd.DataFrame: DataFrame contenant les données générées.
    """
    # Fixer la graine aléatoire pour la répétabilité
    np.random.seed(42)
    random.seed(42)

    # Plage de dates : 3 derniers mois jusqu'à aujourd'hui
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    # Définition des éléments récurrents et aléatoires par catégorie
    income_templates = [
        ("Salaire Mensuel", 2800.0, "Revenu", "Revenu"),
        ("Prime de Performance", 450.0, "Revenu", "Revenu"),
        ("Vente objet occasion", 60.0, "Revenu", "Revenu"),
        ("Remboursement Santé", 45.0, "Revenu", "Revenu"),
    ]
    
    savings_templates = [
        ("Virement PEA - ETF MSCI World", -400.0, "Epargne", "Investissement & Epargne"),
        ("Virement Livret A - Épargne Sécurité", -200.0, "Epargne", "Investissement & Epargne"),
        ("Investissement Crypto / SCPI", -100.0, "Epargne", "Investissement & Epargne"),
    ]

    expense_templates = [
        # Logement & Charges
        ("Loyer Appartement", -850.0, "Dépense", "Logement & Charges"),
        ("Électricité & Gaz - EDF", -95.0, "Dépense", "Logement & Charges"),
        ("Assurance Habitation", -28.0, "Dépense", "Logement & Charges"),
        ("Charges de Copropriété", -65.0, "Dépense", "Logement & Charges"),

        # Alimentation
        ("Courses Supermarché Carrefour", -110.0, "Dépense", "Alimentation"),
        ("Courses Bio - Biocoop", -65.0, "Dépense", "Alimentation"),
        ("Boulangerie du Coin", -8.5, "Dépense", "Alimentation"),
        ("Marché Hebdomadaire", -42.0, "Dépense", "Alimentation"),
        ("Petit Commerce de Proximité", -18.0, "Dépense", "Alimentation"),

        # Sorties & Plaisirs
        ("Restaurant Le Bistrot", -55.0, "Dépense", "Sorties & Plaisirs"),
        ("Verres entre amis - Bar", -32.0, "Dépense", "Sorties & Plaisirs"),
        ("Place de Cinéma", -14.5, "Dépense", "Sorties & Plaisirs"),
        ("Week-end Escapade", -140.0, "Dépense", "Sorties & Plaisirs"),
        ("Concert / Théâtre", -48.0, "Dépense", "Sorties & Plaisirs"),

        # Shopping & Perso
        ("Achat Vêtements - Zara", -75.0, "Dépense", "Shopping & Perso"),
        ("Pharmacie & Soins", -24.0, "Dépense", "Shopping & Perso"),
        ("Commandes Amazon (Maison)", -39.0, "Dépense", "Shopping & Perso"),
        ("Coiffeur / Esthétique", -45.0, "Dépense", "Shopping & Perso"),
        ("Cadeau Anniversaire", -50.0, "Dépense", "Shopping & Perso"),

        # Abonnements
        ("Abonnement Netflix", -15.99, "Dépense", "Abonnements"),
        ("Abonnement Spotify Premium", -10.99, "Dépense", "Abonnements"),
        ("Forfait Mobile & Fibre", -34.99, "Dépense", "Abonnements"),
        ("Abonnement Salle de Sport", -29.99, "Dépense", "Abonnements"),
        ("Abonnement Presse / Media", -9.90, "Dépense", "Abonnements"),
    ]

    transactions = []

    # 1. Génération des transactions récurrentes mensuelles (3 mois)
    for month_offset in range(3):
        month_date = start_date + timedelta(days=month_offset * 30)
        
        # Salaire au 1er du mois
        pay_date = month_date.replace(day=1) + timedelta(days=random.randint(0, 2))
        transactions.append({
            "Date": pay_date.strftime("%Y-%m-%d"),
            "Description": "Salaire Mensuel",
            "Montant": 2800.0 + random.choice([-50, 0, 50]),
            "Type": "Revenu",
            "Categorie": "Revenu"
        })
        
        # Loyer au 3 du mois
        rent_date = month_date.replace(day=3)
        transactions.append({
            "Date": rent_date.strftime("%Y-%m-%d"),
            "Description": "Loyer Appartement",
            "Montant": -850.0,
            "Type": "Dépense",
            "Categorie": "Logement & Charges"
        })
        
        # Virements d'Épargne au 5 du mois (dont PEA)
        pea_date = month_date.replace(day=5)
        transactions.append({
            "Date": pea_date.strftime("%Y-%m-%d"),
            "Description": "Virement PEA - ETF MSCI World",
            "Montant": -400.0,
            "Type": "Epargne",
            "Categorie": "Investissement & Epargne"
        })
        transactions.append({
            "Date": pea_date.strftime("%Y-%m-%d"),
            "Description": "Virement Livret A - Épargne Sécurité",
            "Montant": -200.0,
            "Type": "Epargne",
            "Categorie": "Investissement & Epargne"
        })

    # 2. Compléter le reste des transactions jusqu'à atteindre num_records
    remaining_count = num_records - len(transactions)
    
    for _ in range(remaining_count):
        # Choisir une date aléatoire sur les 90 derniers jours
        random_days = random.randint(0, 90)
        t_date = start_date + timedelta(days=random_days)
        
        # Déterminer le type de transaction (majorité de dépenses courantes)
        p = random.random()
        if p < 0.08:
            # Petit revenu ponctuel
            desc, amount, t_type, cat = random.choice(income_templates[1:])
            amount = round(amount * random.uniform(0.8, 1.2), 2)
        elif p < 0.15:
            # Épargne complémentaire
            desc, amount, t_type, cat = random.choice(savings_templates)
            amount = round(amount * random.uniform(0.7, 1.3), 2)
        else:
            # Dépense courante
            desc, base_amount, t_type, cat = random.choice(expense_templates)
            # Variations réalistes autour du montant de base
            amount = round(base_amount * random.uniform(0.7, 1.3), 2)

        transactions.append({
            "Date": t_date.strftime("%Y-%m-%d"),
            "Description": desc,
            "Montant": amount,
            "Type": t_type,
            "Categorie": cat
        })

    # Trier par date croissante
    df = pd.DataFrame(transactions)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date").reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")

    # Exporter en CSV
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Jeu de données généré avec succès : {output_file} ({len(df)} transactions)")
    return df

if __name__ == "__main__":
    generate_financial_data()
