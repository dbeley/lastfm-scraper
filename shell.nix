with import <nixpkgs> { };

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    python3Packages.pip

    python3Packages.requests
    python3Packages.pylast
    python3Packages.pandas
    python3Packages.beautifulsoup4
    python3Packages.lxml
    python3Packages.tqdm
    python3Packages.wordcloud

    pre-commit
  ];

}
