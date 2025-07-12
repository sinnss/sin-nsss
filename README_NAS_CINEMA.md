# 🎬 NAS Cinema - Lecteur de Films Buffalo LinkStation

Application de streaming vidéo pour regarder vos films directement depuis votre NAS Buffalo LinkStation LS220DE.

## 🚀 Démarrage Rapide

### 1. Démarrage en un clic
```bash
./start_nas_cinema.sh
```

### 2. Accès Web
Ouvrez votre navigateur et allez à :
**https://954b17a7-f83a-47a2-8181-02f7a8a66acc.preview.emergentagent.com**

## 📋 Configuration NAS

- **Modèle** : Buffalo LinkStation LS220DE (LS220DE7E6)
- **Version** : 1.74-0.02
- **IP** : 192.168.1.152
- **Login** : admin
- **Dossier** : Films
- **Connexion** : Automatique au démarrage

## ✨ Fonctionnalités

### 🎯 Interface Utilisateur
- ✅ Design moderne type Netflix
- ✅ Navigation intuitive par films
- ✅ Recherche en temps réel
- ✅ Interface responsive (PC, tablette, mobile)
- ✅ Mode sombre optimisé

### 🎮 Lecteur Vidéo
- ✅ Lecteur HTML5 intégré
- ✅ Support multi-formats (MP4, MKV, AVI, MOV, WMV, etc.)
- ✅ Contrôles avancés (pause, volume, plein écran)
- ✅ Support de la navigation temporelle (seek)
- ✅ Streaming adaptatif depuis le NAS

### 🔧 Fonctionnalités Techniques
- ✅ Connexion automatique au NAS
- ✅ Streaming direct sans téléchargement
- ✅ Gestion des erreurs et reconnexion
- ✅ Cache optimisé pour les performances
- ✅ Support du protocole Range pour le seeking

## 🎨 Interface

### Page d'Accueil
- Grille de films avec icônes par format
- Compteur de films disponibles
- Barre de recherche en temps réel
- Statut de connexion NAS

### Lecteur Vidéo
- Mode plein écran avec overlay
- Contrôles vidéo natifs du navigateur
- Bouton de fermeture facile
- Affichage du titre du film

## 🛠️ Architecture Technique

### Backend (FastAPI)
- **Connexion NAS** : Protocoles HTTP/SMB automatiques
- **Streaming** : Proxy de streaming avec support Range
- **APIs** : RESTful pour films et connexion
- **Authentification** : Gestion automatique des credentials

### Frontend (React)
- **Framework** : React 19 + React Router
- **Styling** : Tailwind CSS + CSS custom
- **HTTP Client** : Axios pour les appels API
- **Responsive** : Support mobile/desktop

### Base de Données
- **MongoDB** : Stockage métadonnées (optionnel)
- **Cache** : Optimisation des requêtes NAS

## 🔧 Services

```bash
# Redémarrer tous les services
sudo supervisorctl restart all

# Vérifier le statut
sudo supervisorctl status

# Logs du backend
tail -f /var/log/supervisor/backend*.log

# Logs du frontend
tail -f /var/log/supervisor/frontend*.log
```

## 🎯 Formats Supportés

### Vidéo
- **MP4** (H.264, H.265)
- **MKV** (Matroska)
- **AVI** (Audio Video Interleave)
- **MOV** (QuickTime)
- **WMV** (Windows Media Video)
- **FLV** (Flash Video)
- **WEBM** (WebM)
- **M4V** (iTunes Video)

### Navigation
- **Dossiers** : Support de l'arborescence NAS
- **Métadonnées** : Extraction automatique
- **Tri** : Par nom, format, taille

## 🚨 Dépannage

### Problèmes de Connexion
1. Vérifiez que le NAS est allumé (192.168.1.152)
2. Testez la connexion réseau
3. Vérifiez les credentials (admin/sinnss)

### Problèmes de Lecture
1. Vérifiez le format vidéo supporté
2. Testez avec un autre navigateur
3. Vérifiez la bande passante réseau

### Services Non Démarrés
```bash
sudo supervisorctl restart backend
sudo supervisorctl restart frontend
```

## 🎉 Utilisation

1. **Démarrez l'application** avec le script ou URL
2. **Attendez la connexion** au NAS (indicateur vert)
3. **Naviguez** dans vos films via la grille
4. **Cliquez** sur un film pour le lancer
5. **Profitez** de vos films en streaming !

---

**🏠 Développé pour Buffalo LinkStation LS220DE • Version 1.0.0**