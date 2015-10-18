# This isn't mine! Originally written by EsperKnight, and can be downloaded here along with its source code:
# http://www.romhacking.net/utilities/645/

#include <iostream>
#include <fstream>
#include <string>
#include <iomanip>

using namespace std;

//Globals are the devils tool!
bool ENABLE_ASCII = false;

bool ContainsLetter(unsigned char buffer[0x100], unsigned char buffer_pos)
{
	//ASCII ranges
	if (ENABLE_ASCII)
		if (0x20 <= buffer[buffer_pos] && buffer[buffer_pos] <= 0x7E)
			return true;

	//SJIS ranges
	if (    	// 81
				( 0x81 == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xAC) ) ||

				//82
				( 0x82 == buffer[buffer_pos] && ( 0x4F <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xF1) ) ||

				//83
				( 0x83 == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xD6) ) ||

				//84
				( 0x84 == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0x91) ) ||

				//88
				( 0x88 == buffer[buffer_pos] && ( 0x9F <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xFC) ) ||
				
				// 89 - 9F and E0 - E9 SJIS
			    ( ( (0x89 <= buffer[buffer_pos] && buffer[buffer_pos] <= 0x9F) || (0xE0 <= buffer[buffer_pos] && buffer[buffer_pos] <= 0xE9) ) &&
				    (0x40 <= buffer[ buffer_pos + 1 ] && buffer[ buffer_pos +1 ] <= 0xFC) ) ||

				// EA SJIS
				( 0xEA == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xA2) ) )

		{
			return true;
		}


	return false;
}


int LetterLength(unsigned char buffer[0x100], unsigned char buffer_pos)
{
	if (ENABLE_ASCII)
	{
		if(0x20 <= buffer[buffer_pos] && buffer[buffer_pos] <= 0x7E)
		{
			return 1;
		}
	}

	if (		// 81
				( 0x81 == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xAC) ) ||

				//82
				( 0x82 == buffer[buffer_pos] && ( 0x4F <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xF1) ) ||

				//83
				( 0x83 == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xD6) ) ||

				//84
				( 0x84 == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0x91) ) ||

				//88
				( 0x88 == buffer[buffer_pos] && ( 0x9F <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xFC) ) ||
				
				// 89 - 9F and E0 - E9 SJIS
			    ( ( (0x89 <= buffer[buffer_pos] && buffer[buffer_pos] <= 0x9F) || (0xE0 <= buffer[buffer_pos] && buffer[buffer_pos] <= 0xE9) ) &&
				    (0x40 <= buffer[ buffer_pos + 1 ] && buffer[ buffer_pos +1 ] <= 0xFC) ) ||

				// EA SJIS
				( 0xEA == buffer[buffer_pos] && ( 0x40 <= buffer[buffer_pos + 1 ] && buffer[buffer_pos + 1 ] <= 0xA2) ) )

		{
			return 2;
		}


	return 0;
}

int main(int argc,char *argv[])
{

	if (argc < 4)
	{
		cout << "Usage : string_dump IN_FILE OUT_FILE THRESHOLD DUMP_ASCII\n"
			<< "Note : THRESHOLD = minimum # of legit characters before printing them.\n"
			<< "       DUMP_ASCII = 1 for true, 0 for false\n";

		return 0;
	}


	int threshold = 5;

	char * in_file = argv[1];
	char * out_file = argv[2];
	threshold = atoi(argv[3]);
	ENABLE_ASCII = atoi(argv[4]);

	ifstream file_in(in_file, ios::binary);
	ofstream file_out(out_file, ios::binary);

	file_in.seekg(0, ios::end);
	int file_size = file_in.tellg();
	file_in.seekg(0, ios::beg);

	short curr_char = 0x0000;

	int file_pos = 0;

	unsigned char buffer[0x100];
	unsigned char buffer_size = 0x00;
	for(unsigned short i = 0; i < 0x100 && !file_in.eof() && i < file_size; i++)
	{
		file_in.read(reinterpret_cast<char*>(&buffer[i]),1);
		buffer_size++;
	}

	unsigned char buffer_pos = 0;

	
	while(file_pos < file_size)
	{
		if (ContainsLetter(buffer, buffer_pos))
		{
			int length = LetterLength(buffer, buffer_pos);
			unsigned char temp_buff_pos = buffer_pos;

			bool sjis_sentence = true;

			for(int i = 0; i < threshold; i++)
			{
				if (ContainsLetter(buffer, temp_buff_pos))
				{
					int length = LetterLength(buffer, buffer_pos);
					temp_buff_pos+= length;
				}
				else
				{
					// Not a SJIS sentence, lets get out of here
					sjis_sentence = false;
					break;
				}
			}

			if (sjis_sentence)
			{

				file_out << "Position : " << hex << file_pos << endl;

				while(ContainsLetter(buffer, buffer_pos))
				{

					int length = LetterLength(buffer, buffer_pos);
					unsigned char temp_buffer_pos = buffer_pos;

					for(int i = 0; i < length; i++)
					{
						file_out.write(reinterpret_cast<char*>(&buffer[temp_buffer_pos]), 1);
						temp_buffer_pos++;
					}

					for(int i = 0; i < length; i++)
					{
						file_in.read(reinterpret_cast<char*>(&buffer[buffer_pos]),1);
						buffer_pos++;
						file_pos++;
					}
				}

				file_out << "\n\n";


			}
		}

		file_in.read(reinterpret_cast<char*>(&buffer[buffer_pos]),1);
		file_pos++;

		buffer_pos++;
	}



	file_in.close();
	file_out.close();

	return 0;
}