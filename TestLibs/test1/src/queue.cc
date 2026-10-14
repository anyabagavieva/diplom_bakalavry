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

#include "queue.h"
#include <cstring>
#include <stdio.h>
#include <cstdlib>

Define_Module(Queue);

void Queue::initialize()
{
    // TODO - Generated method body
    //curNum = 0;
    discarded = 0;
    maxVol = par("volume").intValue();
    //isServerFree = false;
    for (int i=0; i<3; i++) {
        isServerFree[i] = false;
    }
    queLenSignal = registerSignal("curLen");
    discardSignal = registerSignal("curDiscard");
    queueStateVec.setName("Queue State");
    discardNumVec.setName("Discarded Requests Number");
}

void Queue::handleMessage(cMessage *msg)
{
    // TODO - Generated method body
    if (strcmp(msg->getName(), "free server") == 0) {
        gateIdx = msg->getArrivalGate()->getIndex();    //what server message came from
        if (!queueArr.isEmpty()) {
            //--curNum;
            send((cMessage*)queueArr.pop(), "queueServer$o", gateIdx);      //send back to that server
            isServerFree[gateIdx] = false;
        }
        else {
            isServerFree[gateIdx] = true;
        }
        delete msg;
    }
    else {
        int freeIdx = getFreeGateIdx();
        if (freeIdx == -1) {
            //if (curNum < maxVol) {
            if (queueArr.getLength() < maxVol) {
                //++curNum;
                queueArr.insert(msg);
            }
            else {
                ++discarded;
                emit(discardSignal, discarded);
                delete msg;
            }
        }
        else {
            if (!queueArr.isEmpty()) {
                send((cMessage*)queueArr.pop(), "queueServer$o", freeIdx);
                isServerFree[freeIdx] = false;
                queueArr.insert(msg);
            }
            else {
                send(msg, "queueServer$o", freeIdx);
                isServerFree[freeIdx] = false;
            }
        }
    }
    emit(queLenSignal, queueArr.getLength());
    queueStateVec.record(queueArr.getLength());
    discardNumVec.record(discarded);
}

int Queue::getFreeGateIdx() {
    int idx = -1;
    for (int i=0; i<3; i++) {
        if (isServerFree[i] == true) {
            idx = i;
            break;
        }
    }
    return idx;
}
