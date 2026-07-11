# VHS demo: watch_convert
# 生成: リポルートで nix-shell に入り `vhs packages/watch_convert/demo.tape`
# 前提: .venv に requirements.txt がインストール済み。
#       Gotenberg コンテナが起動していること（例: docker compose up -d gotenberg）。
#       GOTENBERG_URL 未設定時は既定の http://localhost:3000 に接続する。

Output packages/watch_convert/demo.gif

Set FontSize 18
Set Width 1000
Set Height 500
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "# xlsxをディレクトリに置くと、Gotenbergでの実変換によりpdfが自動生成される"
Enter
Sleep 1s

Type "mkdir -p shared"
Enter
Sleep 1s

Type "ls shared/"
Enter
Sleep 2s

Type ".venv/bin/python -m packages.watch_convert shared --exec '.venv/bin/python -c \"import sys; from pathlib import Path; from app.gotenberg import convert_to_pdf; convert_to_pdf(Path(sys.argv[1]), Path(sys.argv[2]))\" {src} shared/report.pdf' --debounce 0.5 &"
Enter
Sleep 2s

Type "cp packages/template_fill/demo/template.xlsx shared/report.xlsx"
Enter
Sleep 3s

Type "ls shared/"
Enter
Sleep 2s

Type "kill %1"
Enter
Sleep 1s
