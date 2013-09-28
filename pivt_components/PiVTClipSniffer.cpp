/*
 *      Copyright (C) 2013 York Student Television
 *      http://ystv.co.uk
 *
 *  This Program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2, or (at your option)
 *  any later version.
 *
 *  This Program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with PiVT; see the file COPYING.  If not, write to
 *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
 *  http://www.gnu.org/copyleft/gpl.html
 *
 */

#include <string>
#include <vector>
#include <sstream>
#include <boost/shared_ptr.hpp>

#include <dirent.h>
#include <sys/stat.h>

#include "DllAvFormat.h"
#include "DllAvCodec.h"

#include "PiVTClipSniffer.h"

void * sniffClips (void *psniffdata)
{
	// Extract some data
	PiVT_SnifferData *pd = (PiVT_SnifferData *)psniffdata;

	// List files in the directory
	std::vector<std::string> files;
    DIR *d;
    struct dirent *dir;
    d  = opendir(pd->folder.c_str());
    while ((dir = readdir(d)) != NULL)
    {
        std::string file = dir->d_name;

        struct stat st;
        if (pd->folder[pd->folder.length()-1] != '/')
        {
        	pd->folder += "/";
        }

        stat((pd->folder + "/" + file).c_str(),&st);

        if (S_ISREG (st.st_mode))
        {
            files.push_back(file);
        }
    }

    // Attempt to open each and grab the length
    std::vector<std::string> resultlines;

    AVFormatContext *pFormatCtx = avformat_alloc_context();

    for (std::string filename : files)
    {
    	if (avformat_open_input(&pFormatCtx, (pd->folder + filename).c_str(), NULL, NULL) != 0)
    	{
    		// File not opened
    		continue;
    	}
    	if (avformat_find_stream_info(pFormatCtx, NULL) < 0)
    	{
    		// Bad file formatting
    		continue;
    	}

    	// Assemble the response line
    	std::stringstream resp;

    	resp << "206 " << filename << " " << (pFormatCtx->duration / AV_TIME_BASE) << " seconds";
    	resultlines.push_back(resp.str());

    	avformat_close_input(&pFormatCtx);
    }

    // Send each result line
    for (std::string line : resultlines)
    {
    	pd->conn->writeData(line);
    }
    // Send terminator
    pd->conn->writeData("205 File listing complete");

    // Clean up
    delete pd;

    return NULL;
}
