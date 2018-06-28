brew install tor

tor --hash-password my_password #copy the result

add following text to /usr/local/etc/tor/torrc

```
controlPort 9051
HashedControlPassword "HASH_PASSWORD_GENERATED_BY_ABOVE_COMMAND"
CookieAuthentication 1
```

brew services restart tor

pip install stem

export PYCURL_SSL_LIBRARY=openssl

pip install pycurl

python test_tor_stem_privoxy.py
