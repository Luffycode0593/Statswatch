# 🖥️ Moniteur Système - PC Stats (v1)

Une application moderne et interactive pour surveiller les performances de votre PC en temps réel, avec overlay personnalisable.

## ✨ Fonctionnalités principales

- **Widgets de monitoring** :
  - CPU/VPS (utilisation, fréquence, cœurs)
  - Mémoire (utilisation, total, disponible)
  - Disque (utilisation, espace total et libre)
  - Températures (CPU et GPU)
  - Réseau (données envoyées/reçues)
  - Infos globales (OS, uptime, démarrage)
- **Overlay flottant** (toujours visible sur le PC, en haut à gauche) :
  - Affichage personnalisable (Taux de rafraîchissement de l'écran (Hz), CPU, Réseau, Températures)
  - Activation/désactivation à tout moment
- **Boutons en bas à droite** :
  - 🔄 Rafraîchir : met à jour toutes les infos
  - 🏁 Overlay : ouvre la configuration de l'overlay
  - ⚙️ Paramètres : choix de la langue (français/anglais) et du thème (clair/sombre)
- **Interface moderne** :
  - Thème sombre ou clair
  - Traduction automatique FR/EN
  - Boutons visibles et accessibles
- **Logs en temps réel**

## 🚀 Installation

### Prérequis
- Python 3.7 ou supérieur
- Windows 10/11 (testé sur Windows)

### Installation des dépendances
```bash
pip install -r requirements.txt
```

> **Note :** Le module `screeninfo` est utilisé pour détecter le taux de rafraîchissement de l'écran (Hz).

## 🎯 Utilisation

### Lancer l'application
```bash
python system_monitor.py
```

### Interface principale
- **Panel de configuration** (haut à gauche) : active/désactive les widgets à afficher
- **Boutons** (en bas à droite) :
  - **🔄 Rafraîchir** : met à jour toutes les infos
  - **🏁 Overlay** : ouvre une fenêtre pour choisir ce que tu veux afficher dans l'overlay (Taux de rafraîchissement, CPU, Réseau, Températures)
  - **⚙️ Paramètres** : choisis la langue (français/anglais) et le thème (clair/sombre)

### Overlay flottant
- Clique sur **🏁 Overlay** puis sélectionne les infos à afficher
- Clique sur "Afficher l'overlay" pour l'activer
- L'overlay s'affiche en haut à gauche de l'écran, toujours au-dessus des autres fenêtres
- Pour fermer l'overlay : clique droit dessus
- **FPS** = Taux de rafraîchissement réel de l'écran principal (en Hz)

### Personnalisation
- **Langue** : français ou anglais (via ⚙️)
- **Thème** : sombre ou clair (via ⚙️)
- **Overlay** : choisis les infos à afficher à chaque activation

## 📝 Notes
- Les températures peuvent ne pas s'afficher si ton PC ne fournit pas les capteurs
- Le taux de rafraîchissement affiché correspond à la fréquence de l'écran principal (ex : 60Hz, 144Hz)
- L'application est en version **V1** : d'autres fonctionnalités peuvent être ajoutées !

---

<div align="right"><b>Created by Luffy | Contact: luffy._.f (Discord)</b></div> 
