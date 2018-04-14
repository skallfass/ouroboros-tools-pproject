$PYTHON setup.py install

cp pproject.sh $PREFIX/bin/pproject
if ! [ -d "$HOME/.config/pproject" ]; then
    mkdir "$HOME/.config/pproject";
fi
if ! [ -e "$HOME/.config/pproject/pproject_config.yml" ]; then
    cp ouroboros/tools/pproject/pproject_config.yml "$HOME/.config/pproject/pproject_config.yml";
fi
