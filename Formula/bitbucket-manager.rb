class BitbucketManager < Formula
  include Language::Python::Virtualenv

  desc "TUI suite for managing Bitbucket Cloud from the terminal"
  homepage "https://github.com/AlanStefanov/bitbucket-manager"
  url "https://github.com/AlanStefanov/bitbucket-manager/archive/refs/tags/v0.4.1.tar.gz"
  sha256 "1264c5bb8d5652db7aad125cc13bd92804eb2985bb9df5d47acfed0c11d0e18e"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_create(libexec, "python3.12")
    system libexec/"bin/pip", "install", buildpath
    bin.install_symlink libexec/"bin/bitbucket-manager"
  end

  test do
    assert_match "Bitbucket Manager", shell_output("#{bin}/bitbucket-manager --help")
  end
end
