//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

#include "generator.h"
#include <cstdlib>
#include <stdio.h>

Define_Module(Generator);

void Generator::initialize()
{
    // TODO - Generated method body
    curNum = 0;
    generateRequest = new cMessage();    //create request
    scheduleAt(0, generateRequest);      //reminder to send first request
}

void Generator::handleMessage(cMessage *msg)
{
    // TODO - Generated method body
    if (msg == generateRequest) {
        //create message to send
        char msgName[32];
        sprintf(msgName, "request %d", ++curNum);
        cMessage* newRequest = new cMessage(msgName);
        send(newRequest, "out");    //sending
        //plan time to schedule next message
        simtime_t timeHop = exponential(par("meanGenTime").doubleValue());   //generate random time between events (normal distribution)
        scheduleAt(simTime() + timeHop, generateRequest);
    }
    else {
        delete msg;     //unplanned message
    }
}
