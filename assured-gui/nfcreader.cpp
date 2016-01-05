#include "nfcreader.hpp"

#include <exception>
#include <iostream>
#include <sstream>
#include <cstdlib>

#include <nfc/nfc.h>
#include <nfc/nfc-types.h>

NfcReader::NfcReader() 
{
}

void NfcReader::init()
{
	nfc_init(&context);
	if (context == NULL) {
		throw "Unable to init libnfc (malloc)";
	}
	pnd = nfc_open(context, NULL);
	if (pnd == NULL) {
		nfc_exit(context);
		throw "Unable to open NFC device";
	}
	if (nfc_initiator_init(pnd) < 0) {
		nfc_close(pnd);
		nfc_exit(context);
		throw "nfc_initiator_init";
	}
	
	//std::cout << "NFC reader " << nfc_device_get_name(pnd) << " opened.\n";
}

NfcReader::~NfcReader()
{
	//abort_cmd();
	//nfc_close(pnd);
	//nfc_exit(context);
}

bool NfcReader::scan() 
{
	int res = nfc_initiator_select_passive_target(pnd, nmModulation, NULL, 0, &nt);
	if (res < 0) {
		nfc_close(pnd);
		nfc_exit(context);
		throw "nfc_initiator_select_passive_target";
	}
	if (res == 0) return false;
	else return true;
	
}

void NfcReader::print_target()
{
	char *s;
	str_nfc_target(&s, &nt, false);
	std::cout << s;
	nfc_free(s);
}

bool NfcReader::target_present()
{
	return nfc_initiator_target_is_present(pnd, NULL) == 0;
}

void NfcReader::abort_cmd() 
{
	if (pnd != NULL)
		nfc_abort_command(pnd);
}

int NfcReader::snprint_hex(char *dst, size_t size, const uint8_t *pbtData, const size_t szBytes) 
{
	size_t szPos;
	size_t res = 0;
	for (szPos = 0; szPos < szBytes; szPos++) {
		res += snprintf(dst+res, size-res, "%02x", pbtData[szPos]);
	}
	return res;
}

char *NfcReader::get_uid()
{
	char *buf = new char[20];
	buf[0] = '\0';
	snprint_hex(buf, 20, nt.nti.nai.abtUid, nt.nti.nai.szUidLen);
	return buf;
}
