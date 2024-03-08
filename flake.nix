{
  description = "Python development environment with specific packages";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        python = pkgs.python311;
        python_packages = python.withPackages (ps: with ps; [
          pyautogui
          appdirs
          toml
          screeninfo
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            python_packages
            pkgs.rsync
            pkgs.zip
          ];
        };
      }
    );
}
