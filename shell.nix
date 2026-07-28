(import (
  fetchTarball {
    url = "https://github.com/edolstra/flake-compat/archive/master.tar.gz";
  }
) {
  src = ./.;
}).shellNix
