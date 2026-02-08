{

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { self, nixpkgs }:
    let
      supportedSystems = [ "aarch64-darwin" "aarch64-linux" "x86_64-darwin" "x86_64-linux" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      nixpkgsFor = forAllSystems (system:
        import nixpkgs {
          inherit system;
          overlays = [ self.overlays.default ];
        });
    in
    {

      formatter = forAllSystems (system: nixpkgsFor.${system}.nixpkgs-fmt);

      devShells = forAllSystems (system: {
        default = nixpkgsFor.${system}.callPackage
          ({ mkShell, python3, pre-commit, ... }:
            mkShell {
              buildInputs = [
                pre-commit
                (python3.withPackages (p: with p; [
                  argcomplete
                  black
                  colorama
                  requests
                ]))
              ];
            })
          { };
      });

      packages = forAllSystems (system:
        let pkgs = nixpkgsFor.${system}; in {
          default = self.packages.${system}.bonn-mensa;
          bonn-mensa = pkgs.callPackage
            ({ lib, python3 }:

              python3.pkgs.buildPythonApplication {
                pname = "bonn-mensa";
                version = (lib.strings.removePrefix ''__version__ = "'' (lib.strings.removeSuffix ''"
              ''
                  (builtins.readFile "${self}/src/bonn_mensa/version.py")
                ));
                pyproject = true;

                src = self;

                nativeBuildInputs = with python3.pkgs; [
                  pkgs.installShellFiles
                  argcomplete
                  setuptools
                ];

                propagatedBuildInputs = with python3.pkgs; [
                  argcomplete
                  colorama
                  holidays
                  requests
                ];

                postInstall = ''
                  installShellCompletion --cmd mensa \
                    --bash <(register-python-argcomplete mensa --shell bash) \
                    --fish <(register-python-argcomplete mensa --shell fish) \
                    --zsh <(register-python-argcomplete mensa --shell zsh)
                '';

                pythonImportsCheck = [ "bonn_mensa" ];

                meta = with lib; {
                  description = "Meal plans for university canteens in Bonn";
                  homepage = "https://github.com/alexanderwallau/bonn-mensa";
                  license = licenses.mit;
                  maintainers = with maintainers; [ alexanderwallau MayNiklas ];
                  mainProgram = "mensa";
                };
              })
            { };
        });

      overlays.default = final: prev:
        let system = "${final.system}"; in {
          bonn-mensa = self.packages.${system}.bonn-mensa;
        };

    };
}
