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

package test1;

network QueueingNetwork
{
    @display("bgb=226,199");
    submodules:
        generator: Generator {
            @display("p=200,100");
        }
        queue: Queue {
            @display("p=120,100");
        }
        server[3]: Server {
            @display("p=50,50,c,50");
        }
    connections:
        generator.out --> queue.in;
        for i=0..2 {
            queue.queueServer[i] <--> server[i].dup;
        }
}
