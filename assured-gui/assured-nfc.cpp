#include <stdio.h>
#include <unistd.h>
#include <inttypes.h>
#include <err.h>
#include <signal.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <iostream>

#include <nfc/nfc.h>
#include <nfc/nfc-types.h>

#include "nfcreader.hpp"

NfcReader reader;

volatile sig_atomic_t stop = 0;

static void stop_polling(int sig) 
{
	(void) sig;
	stop = 1;
	reader.abort_cmd();
}

int main(int argc, char *argv[])
{
	signal(SIGINT, stop_polling);
        signal(SIGTERM, stop_polling);
        signal(SIGKILL, stop_polling);

	try {
		reader.init();
	
		while (stop == 0) {
			if (reader.scan()) {
				//reader.print_target();
				std::cout << reader.get_uid() << '\n';
                                std::cout.flush();
				sleep(1);
				while (reader.target_present()) {}
			} else { // None found
				sleep(1);
			}
		}
	}
	catch (char const *error) {
		std::cerr << "Error: " << error << '\n';
	}
	
	return 0;
}
