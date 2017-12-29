**Vedant's Development Environment**
-------------------------------------------------------

 - BASH - Contains bashrc and other files. Copy them directly to your home directory to use.
 - TMUX - Contains tmux scripts and plugins useful for periodic backup/restore of tmux sessions.
 - NUAGE - Contains nuage specific scripts.
 - VIM - Contains vim colors and a GIT submodule `vim_runtime` containing numerous vim plugins and scripts.

**Installation of `vim_runtime`**

    git clone https://github.com/mathurvedant/dev-env.git
    git submodule update --init --recursive
    ln -s dev-env/VIM/vim_runtime ~/.vim_runtime
    sh ~/.vim_runtime/install_awesome_vimrc.sh
    cd .vim_runtime/my_plugins/YouCompleteMe/
    ./install.py --clang-completer

 - Clone this repo in your home directory.
 - Init and update all git submodules recursively.
 - Create a symlink called `.vim_runtime` which points to the `vim_runtime` submodule from the repo which was cloned into the home directory.
 - Run the install vimrc script.
 - Run the install YCM script for C autocomplete and on the fly compilation.


