# VHS demo: template_fill
# 生成: リポルートで nix-shell に入り `vhs packages/template_fill/demo.tape`
# 前提: .venv に requirements.txt がインストール済み

Output packages/template_fill/demo.gif

Set FontSize 18
Set Width 1000
Set Height 500
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "cat packages/template_fill/demo/mapping.yaml"
Enter
Sleep 2s

Type "cat packages/template_fill/demo/data.json"
Enter
Sleep 2s

Type ".venv/bin/python -m packages.template_fill packages/template_fill/demo/mapping.yaml packages/template_fill/demo/data.json -o generated/demo.xlsx"
Enter
Sleep 3s
