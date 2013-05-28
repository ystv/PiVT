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

#include "PiVTConfig.h"

PiVT_Config::PiVT_Config()
{
	stopvideo = "woodstock_sd.mp4";
	videosfolder = "/home/sam.nicholson/";
	port = 9815;

}

PiVT_Config::~PiVT_Config()
{
	// TODO Auto-generated destructor stub
}

std::string PiVT_Config::get_stopvideo()
{
	return stopvideo;
}

std::string PiVT_Config::get_videosfolder()
{
	return videosfolder;
}

int PiVT_Config::get_port()
{
	return port;
}

