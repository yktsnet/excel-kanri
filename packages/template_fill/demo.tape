# VHS demo: template_fill
# 生成: リポルートで nix-shell に入り `vhs packages/template_fill/demo.tape`
# 前提: .venv に requirements.txt がインストール済み
# 示したいこと: マッピングYAMLの「セル番地: 項目名」に従い、
#               JSONの値がテンプレートxlsxの該当セルに流し込まれる

Output packages/template_fill/demo.gif

Set FontSize 18
Set Width 1000
Set Height 500
Set Theme "Catppuccin Mocha"
Set TypingSpeed 40ms

Type "alias py=.venv/bin/python"
Enter
Sleep 500ms

Type "# セル番地と項目名の対応（YAML）"
Enter
Sleep 800ms

Type "cat packages/template_fill/demo/mapping.yaml"
Enter
Sleep 1500ms

Type "# 流し込む値（JSON）"
Enter
Sleep 800ms

Type "cat packages/template_fill/demo/data.json"
Enter
Sleep 1500ms

Type "# 流し込み前: テンプレートのB3/B5/B7はまだ空"
Enter
Sleep 800ms

Type `py -c "from openpyxl import load_workbook as lw; ws = lw('packages/template_fill/demo/template.xlsx').active; print('B3=', ws['B3'].value, 'B5=', ws['B5'].value, 'B7=', ws['B7'].value)"`
Enter
Sleep 2s

Type "# 実行: YAMLの対応でJSONの値を該当セルへ流し込む"
Enter
Sleep 800ms

Type "py -m packages.template_fill packages/template_fill/demo/mapping.yaml packages/template_fill/demo/data.json -o generated/demo.xlsx"
Enter
Sleep 2s

Type "# 流し込み後: 同じセルにdata.jsonの値が着地している"
Enter
Sleep 800ms

Type `py -c "from openpyxl import load_workbook as lw; ws = lw('generated/demo.xlsx').active; print('B3=', ws['B3'].value, 'B5=', ws['B5'].value, 'B7=', ws['B7'].value)"`
Enter
Sleep 3s
