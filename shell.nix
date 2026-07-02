{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python313
    pkgs.python313Packages.venvShellHook
    pkgs.nodejs_22
  ];

  venvDir = "./.venv";

  postVenvCreation = ''
    pip install -r requirements.txt
  '';

  postShellHook = ''
    pip install -r requirements.txt --quiet
  '';
}
