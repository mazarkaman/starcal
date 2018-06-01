# Build with: nix-build ./nix/starcal3/
# Install with: nix-env -f ./nix/ -iA starcal3

with import (builtins.toPath (builtins.getEnv "NIXPKGS")) {};

pythonPackages.buildPythonApplication rec {
  version = "3.0.7-6-g8ebb37c8";
  commitid = "8ebb37c8c1466fb9b52ecb8253f4e31752d9f84d";
  sha256 = "3a0df12fb7356ffde79ece06ad64cea550e68d18d78f7d8147db07b61729beb5";
  pname = "starcal3";

  src = fetchurl {
    url = "https://github.com/ilius/starcal/archive/${commitid}.tar.gz";
    sha256 = sha256;
  };

  nativeBuildInputs = [
    pythonPackages.distutils_extra
    file
    which
    intltool
    gobjectIntrospection
    wrapGAppsHook
	getopt
  ];

  buildInputs = [
    gnome3.gtk
  ];

  propagatedBuildInputs = [
    pythonPackages.pygobject3
    pythonPackages.pycairo
    pythonPackages.pexpect
	pythonPackages.httplib2
	pythonPackages.psutil
	pythonPackages.requests
	pythonPackages.dateutil
	pythonPackages.pymongo # only for 3.0.x
  ];

  # Explicitly set the prefix dir in "setup.py" because setuptools is
  # not using "$out" as the prefix when installing catfish data. In
  # particular the variable "__catfish_data_directory__" in
  # "catfishconfig.py" is being set to a subdirectory in the python
  # path in the store.
#   postPatch = ''
#     sed -i "/^        if self.root/i\\        self.prefix = \"$out\"" setup.py
#   '';

  # Disable check because there is no test in the source distribution
  doCheck = false;

  installPhase = ''
	./install "$out" --prefix=/ --python python3.6
  '';

  meta = with stdenv.lib; {
    homepage = https://github.com/ilius/starcal;
    description = "A full-featured international calendar written in Python";
    longDescription = ''
		StarCalendar is a full-featured international calendar written in Python,
		using Gtk3-based interface, that supports Jalai(Iranian), Hijri(Islamic),
		and Indian National calendars, as well as common Gregorian calendar
		Homepage: http://ilius.github.io/starcal
    '';
    license = licenses.gpl3Plus;
    platforms = platforms.linux;
    # maintainers = [ maintainers.ilius ];
  };
}
