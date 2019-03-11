docker build -t signer .
docker run -p 5000:5000 --device=/dev/bus/usb/003/006 signer