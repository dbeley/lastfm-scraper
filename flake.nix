{
  description = "lastfm-scraper - Scripts to extract data from Last.fm";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python3;
        pythonPackages = python.pkgs;
        pythonEnv = python.withPackages (ps: with ps; [
          pylast pandas requests beautifulsoup4 lxml tqdm wordcloud
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [ pythonEnv pythonPackages.ruff ];
        };
      });
}
