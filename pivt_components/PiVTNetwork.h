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

#include <memory>
#include <string>
#include <algorithm>
#include <boost/asio.hpp>
#include <boost/enable_shared_from_this.hpp>

#include "PiVTTCPConnection.h"

class PiVT_Network {
public:
    PiVT_Network(int port);

    ~PiVT_Network();

    PiVT_CommandData tick();

    void sendall (std::string message);

private:
    boost::shared_ptr<boost::asio::io_service> m_io_service;
	boost::asio::ip::tcp::acceptor m_acceptor;
	void startAccept ();
	void handleAccept (boost::shared_ptr<PiVT_TCPConnection> new_connection,
			const boost::system::error_code& error);


	std::vector<PiVT_CommandData> m_incoming;
	std::vector<boost::weak_ptr<PiVT_TCPConnection>> m_clients;
};

