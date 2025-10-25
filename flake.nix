{
  description = "Book Companion POC development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
    systems.url = "github:nix-systems/default";
    flake-utils = {
      url = "github:numtide/flake-utils";
      inputs.systems.follows = "systems";
    };
  };

  outputs = {
    nixpkgs,
    flake-utils,
    ...
  }:
    flake-utils.lib.eachDefaultSystem (
      system: let
        pkgs = import nixpkgs {
          inherit system;
          config = {
            allowUnfree = true;
          };
        };

        # Python environment with all required packages
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          textual
          requests
          speechrecognition
          pocketsphinx
          pyaudio
        ]);
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            pythonEnv
            git
            ollama
          ];

          shellHook = ''
            echo "Book Companion POC"
            echo "=================="
            echo ""
            echo "All dependencies installed via Nix"
            echo ""
            echo "Setup:"
            echo "  ollama serve &"
            echo "  ollama pull llama2"
            echo ""
            echo "Run:"
            echo "  python companion.py"
          '';
        };
      }
    );
}
