import distutils.core

distutils.core.setup(
    name = "txMsgpack",
    version = "1.0",
    packages = ["txmsgpack"],
    package_dir = {"": "lib/python"},
    author = "Donal McMullan",
    author_email = "donal.mcmullan@gmail.com",
    url = "https://github.com/donalm/txMsgpack",
    license = "MIT",
    description = "txMsgpack is a Twisted Protocol to support msgpack-rpc.",
)
