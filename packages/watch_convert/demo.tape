# VHS demo: watch_convert
# 生成: リポルートで nix-shell に入り `vhs packages/watch_convert/demo.tape`

Output packages/watch_convert/demo.gif

Set FontSize 18
Set Width 1000
Set Height 500
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "mkdir -p shared"
Enter
Type ".venv/bin/python -m packages.watch_convert shared --exec 'echo 変換実行: {src}' --debounce 0.5 &"
Enter
Sleep 2s

Type "cp packages/template_fill/demo/template.xlsx shared/report.xlsx"
Enter
Sleep 3s

Type "kill %1"
Enter
Sleep 1s
