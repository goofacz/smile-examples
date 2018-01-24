#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http:#www.gnu.org/licenses/.
#

import os.path
import argparse
import numpy as np
import scipy.constants
from smile.frames import Frames
from smile.nodes import Nodes

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process Single Sided Two-Way ranging data.')
    parser.add_argument('logs_directory_path', type=str, nargs=1, help='Path to directory holding CSV logs')
    arguments = parser.parse_args()

    logs_directory_path = arguments.logs_directory_path[0]

    # Load data from CSV files
    anchors = Nodes.load_csv(os.path.join(logs_directory_path, 'ss_twr_anchor_nodes.csv'))
    mobiles = Nodes.load_csv(os.path.join(logs_directory_path, 'ss_twr_mobile_nodes.csv'))
    frames = Frames.load_csv(os.path.join(logs_directory_path, 'ss_twr_frames.csv'))

    # Construct POLL frames filter, i.e. transmitted frames ('TX' directions) sent by mobile node
    # (frames.mac_addresses[:, 0] equal to mobile nod'se MAC address)
    poll_frames_condition = np.logical_and(frames[:, Frames.DIRECTION] == hash('TX'),
                                           frames[:, Frames.SOURCE_MAC_ADDRESS] == mobiles[0, Nodes.MAC_ADDRESS])

    # Construct REPONSE frames filter, i.e. transmitted frames ('RX' directions) sent to mobile node
    # (frames.mac_addresses[:, 1] equal to mobile nod'se MAC address)
    response_frames_condition = np.logical_and(frames[:, Frames.DIRECTION] == hash('RX'),
                                               frames[:, Frames.DESTINATION_MAC_ADDRESS] == mobiles[0, Nodes.MAC_ADDRESS])

    # Apply filters constructed above
    response_frames = frames[response_frames_condition]
    poll_frames = frames[poll_frames_condition]

    # Here we will store distance between mobile node and three anchors, each row will contain value in meters and
    # anchor's MAC address
    distances = np.zeros((3, 2))

    processing_delay = 4  # ms
    processing_delay = processing_delay * 1e+9  # ms -> ps

    c = scipy.constants.value('speed of light in vacuum')
    c = c * 1e-12  # m/s -> m/ps

    # Iterate over POLL and RESPONSE frames
    sequence_numbers = (1, 2, 3)
    for i in range(len(sequence_numbers)):
        # Lookup POLL
        sequence_number = sequence_numbers[i]
        poll_frame = poll_frames[poll_frames[:, Frames.SEQUENCE_NUMBER] == sequence_number]
        response_frame = response_frames[response_frames[:, Frames.SEQUENCE_NUMBER] == sequence_number]

        # Compute ToF and fill time_of_flights array
        tof = (response_frame[0, Frames.BEGIN_CLOCK_TIMESTAMP] - poll_frame[0, Frames.BEGIN_CLOCK_TIMESTAMP] - processing_delay) / 2
        distances[i, 0] = tof * c
        distances[i, 1] = response_frame[0, Frames.DESTINATION_MAC_ADDRESS]

    A = np.zeros((3, 3))
    A[:, (0, 1)] = -2 * anchors[:, Nodes.POSITION_2D]
    A[:, 2] = 1

    B = np.zeros((3, 3))
    B[:, 0] = distances[:, 0]
    B[:, (1, 2)] = anchors[:, Nodes.POSITION_2D]
    B = np.power(B, 2)
    B = B[:, 0] - B[:, 1] - B[:, 2]

    tmp, _, _, _ = np.linalg.lstsq(A, B, rcond=None)

    pass  # TODO
