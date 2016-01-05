all:
	g++ -o assured-gui/assured-nfc assured-gui/assured-nfc.cpp assured-gui/nfcreader.cpp `pkg-config --libs libnfc` -I assured-gui -std=c++11 -g

.PHONY: all
