with import <nixpkgs> {};

let
  MyPython = python3.withPackages(ps: [
    ps.opencv3
    ps.pyopengl
  ]);
in
  stdenv.mkDerivation {
    name = "videofeedback";
    buildInputs = [
      MyPython
    ];
  }
