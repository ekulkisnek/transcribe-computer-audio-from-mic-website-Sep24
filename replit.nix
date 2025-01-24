{pkgs}: {
  deps = [
    pkgs.xsimd
    pkgs.pkg-config
    pkgs.libxcrypt
    pkgs.llvm
    pkgs.ffmpeg-full
    pkgs.postgresql
  ];
}
