{pkgs}: {
  deps = [
    pkgs.zbar
    pkgs.libGLU
    pkgs.libGL
    pkgs.glibcLocales
    pkgs.freetype
    pkgs.postgresql
    pkgs.openssl
  ];
}
