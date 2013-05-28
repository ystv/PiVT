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

#pragma once

#include <string>

class PiVT_Config
{
public:
	PiVT_Config();
	virtual ~PiVT_Config();

	std::string get_videosfolder();
	std::string get_stopvideo();
	int get_port();

private:
	std::string videosfolder;
	std::string stopvideo;
	int port;
};

