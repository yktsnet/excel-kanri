# VHS demo: watch_convert
# 生成: リポルートで nix-shell に入り `vhs packages/watch_convert/demo.tape`
# 前提: .venv に requirements.txt がインストール済み
# 示したいこと: ディレクトリへの保存を検知し、連続保存はデバウンスで束ねて、
#               静定後に1回だけ任意コマンドを実行する
# 注: 実変換（Gotenberg呼び出し）はapp/側の仕事。このモジュールが担う
#     検知とデバウンスだけを、自己完結のexecコマンドで示す。

Output packages/watch_convert/demo.gif

Set FontSize 18
Set Width 1000
Set Height 500
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "alias py=.venv/bin/python"
Enter
Sleep 500ms

Type "mkdir -p shared && rm -f shared/*.xlsx"
Enter
Sleep 500ms

Type "# 監視開始（debounce=1秒）: 保存を検知したらexecコマンドを1回実行する"
Enter
Sleep 800ms

Type "py -m packages.watch_convert shared --exec 'echo converted: {src}' --debounce 1 &"
Enter
Sleep 2s

Type "# ファイルを1つ置く → 検知して1回実行される"
Enter
Sleep 800ms

Type "touch shared/report.xlsx"
Enter
Sleep 3s

Type "# 同じファイルを0.2秒間隔で3回連続保存 → 実行は1回だけ"
Enter
Sleep 800ms

Type "for i in 1 2 3; do touch shared/report.xlsx; sleep 0.2; done"
Enter
Sleep 3s

Type "kill %1"
Enter
Sleep 1s
