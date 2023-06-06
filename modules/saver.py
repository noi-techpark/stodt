# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from modules.utilities import scale, mode_for


class Saver:
    def __init__(self, categories, data_dir):
        self.data_dir = data_dir
        self.config = {}
        for index in range(len(categories)):
            self.config[categories[index]["category"]] = categories[index]["allowed_data_types"]

        self.csv_file = open(self.data_dir + '/output.csv', "w")

    def write(self, category, data_type_id, records):
        mode = mode_for(data_type_id, self.config[category])

        for record in records:
            scaled_records = scale(record, data_type_id, mode)

            for scaled_record in scaled_records:
                self.csv_file.write("%s,%s,%s\n" % (scaled_record["data_type"], scaled_record["timestamp"], scaled_record["value"]))

    def save(self):
        self.csv_file.close()
