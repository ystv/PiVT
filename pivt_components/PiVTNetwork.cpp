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

#include "PiVTNetwork.h"

PiVT_Network::PiVT_Network(int port = 9815) :
	m_io_service(new boost::asio::io_service),
	m_acceptor(*m_io_service, boost::asio::ip::tcp::endpoint(boost::asio::ip::tcp::v4(), port))
{
	startAccept();
}

PiVT_Network::~PiVT_Network() {
	//destroy the IOservice object
	while (m_io_service != NULL)
	{
		m_io_service.reset();
	};
}

void PiVT_Network::startAccept ()
{
	boost::shared_ptr<PiVT_TCPConnection> new_connection = PiVT_TCPConnection::create(m_acceptor.get_io_service(), &m_incoming);

	m_acceptor.async_accept(new_connection->socket(),
			boost::bind(&PiVT_Network::handleAccept, this,
			new_connection, boost::asio::placeholders::error));
}

void PiVT_Network::handleAccept (boost::shared_ptr<PiVT_TCPConnection> new_connection,
		const boost::system::error_code& error)
{
	if (!error)
	{
		new_connection->start();
	}

	startAccept();
}

PiVT_CommandData PiVT_Network::tick ()
{
	m_io_service->poll();

	PiVT_CommandData temp;

	if (m_incoming.size() > 0)
	{
		temp = m_incoming.back();
		m_incoming.pop_back();
	}
	else
	{
		temp.command = PIVT_UNKNOWN;
	}
	return temp;

}
