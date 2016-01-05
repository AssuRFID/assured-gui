#include <nfc/nfc-types.h>

#include <string>

class NfcReader 
{
public:
	NfcReader();
	~NfcReader();
	void init();
	bool scan();
	void print_target();
	void abort_cmd();
	bool target_present();
	char *get_uid();
			
private:
	nfc_device *pnd;
	nfc_context *context;
	nfc_target nt;
	nfc_modulation nmModulation = {
		.nmt = NMT_ISO14443A, .nbr = NBR_106
	};
	int snprint_hex(char *dst, size_t size, const uint8_t *pbtData, const size_t szBytes);
		
};

	
