#!/bin/bash

# Script de démarrage NAS Cinema
echo "🎬 Démarrage de NAS Cinema..."

# URL de l'application
APP_URL="https://954b17a7-f83a-47a2-8181-02f7a8a66acc.preview.emergentagent.com"

echo "📡 Vérification des services..."

# Vérifier que les services sont en cours d'exécution
sudo supervisorctl status

echo ""
echo "🎥 Application de streaming NAS prête !"
echo "📱 Ouvrez votre navigateur et allez à :"
echo "🔗 $APP_URL"
echo ""
echo "📋 Configuration NAS :"
echo "   • IP: 192.168.1.152"
echo "   • Model: Buffalo LinkStation LS220DE"
echo "   • Dossier: Films"
echo ""
echo "✨ Profitez de vos films !"

# Optionnel: ouvrir automatiquement dans le navigateur (si disponible)
if command -v xdg-open > /dev/null; then
    echo "🌐 Ouverture automatique du navigateur..."
    xdg-open "$APP_URL"
elif command -v open > /dev/null; then
    echo "🌐 Ouverture automatique du navigateur..."
    open "$APP_URL"
fi