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

#include <boost/asio.hpp>
#include <boost/bind.hpp>
#include <boost/enable_shared_from_this.hpp>
#include <queue>
#include <memory>
#include <string>
#include <algorithm>

enum PiVT_Command
{
    PIVT_LOAD,
    PIVT_PLAY,
    PIVT_STOP,
    PIVT_INFO,
    PIVT_LIST,
    PIVT_QUIT,
    PIVT_HELP,
    PIVT_UNKNOWN
};

class PiVT_TCPConnection;

struct PiVT_CommandData
{
    PiVT_Command command;
    std::string arg;
    boost::shared_ptr<PiVT_TCPConnection> conn;
};

class PiVT_TCPConnection: public boost::enable_shared_from_this<PiVT_TCPConnection>
{
public:
    PiVT_TCPConnection (boost::asio::io_service& io_service,
            std::vector<PiVT_CommandData> *m_incoming);
    ~PiVT_TCPConnection ();

    static boost::shared_ptr<PiVT_TCPConnection> create (
            boost::asio::io_service& io_service,
            std::vector<PiVT_CommandData> *m_incoming);
    boost::asio::ip::tcp::socket& socket ();

    void start ();
    void writeData (std::string data);

    void handleWrite ();
    void handleIncomingData (const boost::system::error_code& error,
            size_t bytes_transferred);

    boost::asio::ip::tcp::socket m_socket;
    std::vector<PiVT_CommandData> *m_data_vector;

    boost::asio::streambuf m_messagedata;
};

