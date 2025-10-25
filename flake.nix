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
        
        # Python environment with required packages
        pythonEnv = pkgs.python3.withPackages (ps: with ps; [
          requests
          pyaudio
          # Note: gutenbergpy and speech_recognition may need to be installed via pip
          # if not available in nixpkgs
        ]);
      in {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            pythonEnv
            git
            ollama
            # Additional tools for development
            python3Packages.pip  # For packages not in nixpkgs
          ];
          
          shellHook = ''
            echo "Book Companion POC Development Environment"
            echo "=========================================="
            echo "Python: $(python --version)"
            echo "Ollama available: $(which ollama)"
            echo ""
            echo "To get started:"
            echo "  1. Start Ollama: ollama serve &"
            echo "  2. Pull a model: ollama pull llama2"
            echo "  3. Install additional Python deps: pip install gutenbergpy speech_recognition"
            echo "  4. Run the companion: python companion.py"
          '';
        };
      }
    );
}
