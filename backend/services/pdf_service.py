import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime

class PDFService:
    @staticmethod
    def generate_cycle_report(cycle, variete, recette, lectures, filePath):
        """Génère un rapport PDF complet pour un cycle de culture."""
        # S'assurer que le dossier existe
        os.makedirs(os.path.dirname(filePath), exist_ok=True)
        
        c = canvas.Canvas(filePath, pagesize=letter)
        width, height = letter

        # --- Entête ---
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(colors.HexColor("#4ade80"))
        c.drawString(1 * inch, height - 1 * inch, "Rapport de Culture HydroSerre")
        
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.grey)
        c.drawString(1 * inch, height - 1.2 * inch, f"Généré le : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        
        c.setStrokeColor(colors.lightgrey)
        c.line(1 * inch, height - 1.4 * inch, width - 1 * inch, height - 1.4 * inch)

        # --- Infos Cycle ---
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.black)
        c.drawString(1 * inch, height - 2 * inch, "Informations Générales")
        
        c.setFont("Helvetica", 12)
        c.drawString(1.2 * inch, height - 2.3 * inch, f"Cycle ID : #{cycle.id_cycle}")
        c.drawString(1.2 * inch, height - 2.55 * inch, f"Variété : {variete.nom}")
        c.drawString(1.2 * inch, height - 2.8 * inch, f"Recette : {recette.nom_recette}")
        c.drawString(1.2 * inch, height - 3.05 * inch, f"Date de début : {cycle.date_debut.strftime('%d/%m/%Y')}")
        c.drawString(1.2 * inch, height - 3.3 * inch, f"Statut : {cycle.statut.capitalize()}")

        # --- Résumé des Lectures ---
        c.setFont("Helvetica-Bold", 14)
        c.drawString(1 * inch, height - 4 * inch, "Statistiques des Capteurs")
        
        if lectures:
            # Calculer quelques moyennes simples (placeholder logic)
            # Dans une version réelle, on ferait des agrégations SQL
            c.setFont("Helvetica", 11)
            y = height - 4.3 * inch
            c.drawString(1.2 * inch, y, f"Nombre total de lectures enregistrées : {len(lectures)}")
            # ... on pourrait ajouter des graphes ou tableaux ici ...
        else:
            c.setFont("Helvetica-Oblique", 11)
            c.drawString(1.2 * inch, height - 4.3 * inch, "Aucune donnée de capteur disponible pour ce cycle.")

        # --- Footer ---
        c.setFont("Helvetica-Oblique", 8)
        c.setFillColor(colors.grey)
        c.drawCentredString(width/2, 0.5 * inch, "Document généré automatiquement par le système HydroSerre v1.0")

        c.showPage()
        c.save()
        return filePath

pdf_service = PDFService()
