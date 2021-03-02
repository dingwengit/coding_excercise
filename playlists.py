import csv
import json


class PlayListChange():
    """
    PlayListChange class
        takes 3 input file names, apply change file on input file, and write
        output file as json format
    """
    def __init__(self, input_file, change_file, output_file):
        if not input_file or not change_file or not output_file:
            raise ValueError("Invalid input data: input_file {}, "
                             "change_file{}, output_file"
                             .format(input_file, change_file, output_file))
        self.input_file, self.change_file, self.output_file = \
            input_file, change_file, output_file
        self.playlist_add, self.song_add, self.playlist_remove = \
            dict(), dict(), set()
        self.user_ids, self.song_ids = set(), set()
        self.first_playlist = None

    def __get_ids(self, f, data_set):
        """
        get user_ids and song_ids to make sure change_file contains valid ids
        :param f: input_file
        :param data_set: user_ids or song_ids
        :return:
        """
        for line in f:
            filter_line = line.replace(" ", '')
            if filter_line == "],\n" or filter_line == "]\n":
                return
            if filter_line == "{\n":
                json_blob = [line]
            elif filter_line == "},\n" or filter_line == "}\n":
                json_blob.append("}")
                try:
                    item = json.loads(''.join(json_blob))
                    data_set.add(item['id'])
                except Exception as ex:
                    print("Failed to load json_blob:{} due to exception {"
                          "}".format(json_blob, ex))
            else:
                json_blob.append(line)

    def __get_user_song_ids(self):
        """
        get user_ids and song_ids from input_file and store them into set
        :return:
        """
        with open(self.input_file, 'r') as f:
            for line in f:
                if line.replace(' ', '') == "\"users\":[\n":
                    self.__get_ids(f, self.user_ids)
                if line.replace(' ', '') == "\"songs\":[\n":
                    self.__get_ids(f, self.song_ids)

    def __update_songs(self, list_songs, new_songs):
        """
        keey track song list for a specific user_id based on the sequence
        in the change_file
        :param list_songs: class member's song list for an user_id
        :param new_songs: song list in one line of change_file
        :return:
        """
        for song in new_songs:
            if song not in list_songs:
                list_songs.append(song)

    def __get_valid_song_ids(self, songs):
        """
        filter out song_ids of change_file which does not show up in input_file
        :param songs: song_ids in one line of change_file
        :return:
        """
        return [song for song in songs if song in self.song_ids]

    def __process_change_file(self):
        # loop through all the lines of change_file in the following CSV
        # format, and store the changes into 3 hashtables
        # CSV format:
        # add playlist: playlist add user_id, song_ids
        # add song:     song add user_id, song_ids
        # remove playlist: playlist remove user_id
        with open(self.change_file, 'r') as f:
            reader = csv.reader(f)
            for line in reader:
                if len(line) < 3:
                    print("insufficient data - skip this row {}".format(row))
                row = list(map(str.strip, line))
                user_id, songs = row[2], self.__get_valid_song_ids(row[3:])
                if user_id not in self.user_ids:
                    print("user_id {} not found in input_file, "
                          "skip it".format(user_id))
                    continue
                # playlist add
                if row[0] == 'playlist' and row[1] == 'add':
                    if len(songs) < 1:
                        raise Exception("Playlist add must have at least one "
                                        "song: {}".format(row))
                    if user_id not in self.playlist_add:
                        self.playlist_add[user_id] = songs
                    else:
                        self.__update_songs(self.playlist_add[user_id],
                                            songs)
                # "song add" will handle previous "playlist add" and "playlist
                # remove" if user_id is the same
                if row[0] == 'song' and row[1] == 'add':
                    if user_id not in self.song_add:
                        self.song_add[user_id] = songs
                    else:
                        self.__update_songs(self.song_add[user_id], songs)
                    if user_id in self.playlist_add:
                        self.__update_songs(self.playlist_add[user_id], songs)
                    if user_id in self.playlist_remove:
                        self.playlist_remove.remove(user_id)

                # "playlist remove" will handle previous "playlist add" and "song
                # add" if user_id is the same
                if row[0] == 'playlist' and row[1] == 'remove':
                    self.playlist_remove.add(user_id)
                    if user_id in self.playlist_add:
                        del self.playlist_add[user_id]
                    if user_id in self.song_add:
                        del self.song_add[user_id]

    def __apply_change(self, one_playlist):
        """
        apply changes to one_playlist if user_id matches
        :param one_playlist: one playlist json blob
        :return:
        """
        user_id = one_playlist['user_id']
        # first check if user_id is in playlist_add hashtable
        if user_id in self.playlist_add:
            for song in self.playlist_add[user_id]:
                if song not in one_playlist['song_ids']:
                    one_playlist['song_ids'].append(song)
            del self.playlist_add[user_id]
        # add or remove songs
        if user_id in self.song_add:
            for song in self.song_add[user_id]:
                if song not in one_playlist['song_ids']:
                    one_playlist['song_ids'].append(song)
        if user_id in self.playlist_remove:
            one_playlist['song_ids'] = None

        # one_playlist['song_ids'] = sorted(one_playlist['song_ids'],
        #                                   key = lambda k: int(k))

    def __add_playlist(self, output, max_playlist_id):
        """
        now apply playlist_add if we are at end_of_playlist
        :param output: output file
        :param max_playlist_id: current max playlist_id
        :return:
        """
        json_obj, cnt = dict(), 0
        for k, v in self.playlist_add.items():
            max_playlist_id += 1
            cnt += 1
            json_obj.clear()
            json_obj['id'] = str(max_playlist_id)
            json_obj['user_id'] = k
            json_obj['song_ids'] = v
            self.__format_one_playlist(output, json_obj)

    def __format_one_playlist(self, output, one_playlist):
        """
        convert json obj into string
        :param output: output file
        :param one_playlist: one playlist json object
        :return:
        """
        if one_playlist['song_ids'] is None: # playlist deleted
            return
        if self.first_playlist is None:
            self.first_playlist = True
        json_str = json.dumps(one_playlist, indent=6, separators=(",", ":"))
        json_str = json_str.replace("{", "    {")
        json_str = json_str.replace("}", '')
        if self.first_playlist:
            output.write(json_str)
            self.first_playlist = False
        else:
            output.write("    }},\n{}".format(json_str))

    def __process_playlist(self, input, output):
        """
        now process the entire section of playlist in input file
        :param input: input file
        :param output: output file
        :return:
        """
        json_blob, max_playlist_id, end_of_playlist = [], 0, False
        for line in input:
            filter_line = line.replace(" ", '')
            if filter_line == "],\n":
                if self.first_playlist is not None:
                    output.write("    }\n")
                output.write(line)
                return
            if filter_line == "{\n":
                json_blob = [line]
            elif filter_line == "},\n" or filter_line == "}\n":
                json_blob.append("}")
                try:
                    one_playlist = json.loads(''.join(json_blob))
                    if int(one_playlist['id']) > max_playlist_id:
                        max_playlist_id = int(one_playlist['id'])
                    self.__apply_change(one_playlist)
                    if filter_line == "}\n":
                        if len(self.playlist_add) == 0:
                            self.__format_one_playlist(output, one_playlist)
                        else:
                            self.__format_one_playlist(output, one_playlist)
                            self.__add_playlist(output, max_playlist_id)
                    else:
                        self.__format_one_playlist(output, one_playlist)
                except Exception as ex:
                    print("Failed to load json_blob:{} due to exception {"
                          "}".format(json_blob, ex))
            else:
                json_blob.append(line)

    def __process_input_file(self, output):
        """
        print out input line if it is not in playlists section, otherwise
        process entire playlists json
        :param output: output file
        :return:
        """
        with open(self.input_file, 'r') as f:
            for line in f:
                if line.replace(' ', '') == "\"playlists\":[\n":
                    # playlist_start = True
                    output.write(line)
                    self.__process_playlist(f, output)
                else:
                    output.write(line)

    def start(self):
        # process input file to get user ids, and song ids
        self.__get_user_song_ids()

        # process change file
        self.__process_change_file()

        # apply changes to input file
        with open(self.output_file, "w") as output:
            self.__process_input_file(output)