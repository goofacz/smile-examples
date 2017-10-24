//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

#pragma once

#include "inet/common/queue/IPassiveQueue.h"
#include "omnetpp.h"

namespace smile {

class DelayingQueue : public omnetpp::cSimpleModule, public inet::IPassiveQueue
{
 public:
  DelayingQueue() = default;
  DelayingQueue(const DelayingQueue& source) = delete;
  DelayingQueue(DelayingQueue&& source) = delete;
  ~DelayingQueue() override = default;

  DelayingQueue& operator=(const DelayingQueue& source) = delete;
  DelayingQueue& operator=(DelayingQueue&& source) = delete;

 protected:
  void requestPacket() override;
  int getNumPendingRequests() override;
  bool isEmpty() override;
  void clear() override;
  cMessage* pop() override;

  void addListener(inet::IPassiveQueueListener* listener) override;
  void removeListener(inet::IPassiveQueueListener* listener) override;
};

}  // namespace smile