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

#include "PiVTTCPConnection.h"

PiVT_TCPConnection::PiVT_TCPConnection (boost::asio::io_service& io_service,
        std::vector<PiVT_CommandData> *m_incoming) :
        m_socket(io_service)
{
    m_data_vector = m_incoming;
}

PiVT_TCPConnection::~PiVT_TCPConnection ()
{
}

boost::shared_ptr<PiVT_TCPConnection> PiVT_TCPConnection::create (
        boost::asio::io_service& io_service,
        std::vector<PiVT_CommandData> *m_pincoming)
{
    return boost::shared_ptr<PiVT_TCPConnection>(
            new PiVT_TCPConnection(io_service, m_pincoming));
}

boost::asio::ip::tcp::socket& PiVT_TCPConnection::socket ()
{
    return m_socket;
}

/**
 * Send a welcome message to a new client and set up a read.
 */
void PiVT_TCPConnection::start ()
{
    std::string message = "Welcome to PiVT.\r\n";

    boost::asio::write(m_socket, boost::asio::buffer(message));

    boost::asio::async_read_until(m_socket, m_messagedata, '\n',
            boost::bind(&PiVT_TCPConnection::handleIncomingData,
                    shared_from_this(), boost::asio::placeholders::error,
                    boost::asio::placeholders::bytes_transferred()));
}

void PiVT_TCPConnection::handleWrite ()
{
}

/**
 * Read a line of data into the queue to be processed. Also starts another read
 *
 * @param error
 * @param bytes_transferred
 */
void PiVT_TCPConnection::handleIncomingData (
        const boost::system::error_code& error, size_t bytes_transferred)
{
    if (error)
    {
        return;
    }
    PiVT_CommandData newdata;

    std::istream is(&m_messagedata);

    // First grab the instruction itself
    std::string command;
    std::getline(is, command, ' ');

    // Check and identify the instruction
    switch (command[0])
    {
    	case 'p':
    		newdata.command = PIVT_PLAY;
    		break;
    	case 'l':
    		newdata.command = PIVT_LOAD;
    		break;
    	case 's':
    		newdata.command = PIVT_STOP;
    		break;
    	case 'i':
    		newdata.command = PIVT_INFO;
    		break;
    	default:
    	{
    		newdata.command = PIVT_UNKNOWN;
			break;
    	}
    }

    // Handle bad instructions
    if (PIVT_UNKNOWN == newdata.command)
    {
    	boost::asio::write(m_socket, boost::asio::buffer("400 Invalid Command\r\n"));
    }
    else
    {
    	std::getline(is, newdata.arg);
    	newdata.arg.erase(std::remove(newdata.arg.begin(), newdata.arg.end(), '\r'), newdata.arg.end());
    	newdata.conn = shared_from_this();
    	m_data_vector->push_back(newdata);
    }

    boost::asio::async_read_until(m_socket, m_messagedata, '\n',
            boost::bind(&PiVT_TCPConnection::handleIncomingData,
                    shared_from_this(), boost::asio::placeholders::error,
                    boost::asio::placeholders::bytes_transferred()));
}

void PiVT_TCPConnection::writeData (std::string data)
{
	boost::asio::write(m_socket, boost::asio::buffer(data + "\r\n"));
}

