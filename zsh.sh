#!/bin/bash

# --- Couleurs pour l'affichage ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Vérification des dépendances ---
if ! command -v git &> /dev/null; then
    echo -e "${RED}Erreur : git n'est pas installé. Installe-le d'abord.${NC}"
    echo "Sous Debian/Ubuntu : sudo apt install git"
    echo "Sous Arch : sudo pacman -S git"
    exit 1
fi

if ! command -v zsh &> /dev/null; then
    echo -e "${RED}Erreur : zsh n'est pas installé. Installe-le d'abord.${NC}"
    echo "Sous Debian/Ubuntu : sudo apt install zsh"
    echo "Sous Arch : sudo pacman -S zsh"
    exit 1
fi

# --- Installation d'Oh My Zsh (si absent) ---
if [ ! -d "$HOME/.oh-my-zsh" ]; then
    echo -e "${BLUE}Installation d'Oh My Zsh...${NC}"
    sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
else
    echo -e "${GREEN}Oh My Zsh est déjà installé.${NC}"
fi

# --- Installation des plugins ---
PLUGINS_DIR="$HOME/.oh-my-zsh/custom/plugins"
mkdir -p "$PLUGINS_DIR"

# Liste des plugins à installer (format: "nom_du_dépôt url")
declare -A PLUGINS=(
    ["zsh-autosuggestions"]="https://github.com/zsh-users/zsh-autosuggestions.git"
    ["zsh-syntax-highlighting"]="https://github.com/zsh-users/zsh-syntax-highlighting.git"
    ["zsh-completions"]="https://github.com/zsh-users/zsh-completions.git"
    ["fast-syntax-highlighting"]="https://github.com/zdharma-continuum/fast-syntax-highlighting.git"
    ["zsh-you-should-use"]="https://github.com/MichaelAquilina/zsh-you-should-use.git"
    ["zsh-history-substring-search"]="https://github.com/zsh-users/zsh-history-substring-search.git"
    ["fzf-tab"]="https://github.com/Aloxaf/fzf-tab.git"
    ["colored-man-pages"]="https://github.com/ael-code/zsh-colored-man-pages.git"
    ["zsh-autopair"]="https://github.com/hlissner/zsh-autopair.git"
    ["zsh-alias-tips"]="https://github.com/djui/alias-tips.git"
#    ["zsh-interactive-cd"]="https://github.com/changyu95/zsh-interactive-cd.git"
)

echo -e "${BLUE}Installation des plugins Zsh...${NC}"
for plugin in "${!PLUGINS[@]}"; do
    if [ -d "$PLUGINS_DIR/$plugin" ]; then
        echo -e "${YELLOW}$plugin est déjà installé.${NC}"
    else
        echo -e "${GREEN}Installation de $plugin...${NC}"
        git clone --depth 1 "${PLUGINS[$plugin]}" "$PLUGINS_DIR/$plugin"
    fi
done

# --- Installation de fzf (requis pour fzf-tab et zsh-interactive-cd) ---
if ! command -v fzf &> /dev/null; then
    echo -e "${BLUE}Installation de fzf...${NC}"
    git clone --depth 1 https://github.com/junegunn/fzf.git ~/.fzf
    ~/.fzf/install --all --no-key-bindings --no-completion --no-update-rc
else
    echo -e "${GREEN}fzf est déjà installé.${NC}"
fi

# --- Installation de Powerlevel10k (thème) ---
if [ ! -d "$PLUGINS_DIR/themes/powerlevel10k" ]; then
    echo -e "${BLUE}Installation de Powerlevel10k...${NC}"
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$PLUGINS_DIR/themes/powerlevel10k"
else
    echo -e "${GREEN}Powerlevel10k est déjà installé.${NC}"
fi

# --- Configuration de ~/.zshrc ---
echo -e "${BLUE}Configuration de ~/.zshrc...${NC}"

# Sauvegarde du fichier existant
if [ -f "$HOME/.zshrc" ]; then
    cp "$HOME/.zshrc" "$HOME/.zshrc.bak"
    echo -e "${YELLOW}Sauvegarde de l'ancien ~/.zshrc dans ~/.zshrc.bak${NC}"
fi

# Écriture du nouveau ~/.zshrc
cat > "$HOME/.zshrc" << 'EOL'
# --- Configuration de base ---
export ZSH="$HOME/.oh-my-zsh"
ZSH_THEME="powerlevel10k/powerlevel10k"

# --- Plugins ---
plugins=(
    git
    zsh-autosuggestions
    fast-syntax-highlighting
    zsh-completions
    colored-man-pages
    zsh-you-should-use
    zsh-history-substring-search
    fzf-tab
    zsh-autopair
    zsh-alias-tips
    zsh-interactive-cd
)

source $ZSH/oh-my-zsh.sh

# --- Configuration de fzf-tab ---
zstyle ':fzf-tab:*' fzf-command ftb-tmux-popup # ou 'fzf' si tu n'utilises pas tmux
zstyle ':fzf-tab:complete:*' fzf-preview 'less -f ${(Q)realpath}'
zstyle ':fzf-tab:*' switch-group '<' '>'

# --- Alias pour le développement C ---
alias gcc='gcc -Wall -Wextra -Werror -g'
alias g++='g++ -Wall -Wextra -Werror -g'
alias mk='make'
alias mkc='make clean'
alias gdb='gdb -q'
alias valgrind='valgrind --leak-check=full --show-leak-kinds=all --track-origins=yes'

# --- Configuration de zsh-history-substring-search ---
bindkey '^[[A' history-substring-search-up    # Flèche haut
bindkey '^[[B' history-substring-search-down  # Flèche bas

# --- Configuration de zsh-autosuggestions ---
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE="fg=#666"

# --- Configuration de Powerlevel10k (à exécuter après l'installation) ---
if [[ ! -f "$HOME/.p10k.zsh" ]]; then
    echo "Pour configurer Powerlevel10k, exécute : p10k configure"
fi
EOL

# --- Application des changements ---
echo -e "${GREEN}Rechargement de la configuration Zsh...${NC}"
source "$HOME/.zshrc"

# --- Message final ---
echo -e "${GREEN}✅ Installation terminée !${NC}"
echo -e "${YELLOW}Redémarre ton terminal ou exécute 'exec zsh' pour appliquer les changements.${NC}"
echo -e "${YELLOW}Pour configurer Powerlevel10k, exécute : p10k configure${NC}"
