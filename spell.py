#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import json
import pickle


class LCSObj:
    def __init__(self, obj_id, seq, line_id, refmt):
        self._refmt = refmt
        if isinstance(seq, str):
            self._lcs_seq = re.split(self._refmt, seq.strip())
        else:
            self._lcs_seq = seq
        self._line_ids = [line_id]
        self._pos = []  # placeholder positions
        self._sep = "	"
        self._id = obj_id
        return

    def __len__(self):
        return len(self._lcs_seq)

    def get_lcs(self, seq):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())
        count = 0
        last_match = -1
        for i in range(len(self._lcs_seq)):
            if i in self._pos:
                continue
            for j in range(last_match+1, len(seq)):
                if self._lcs_seq[i] == seq[j]:
                    last_match = j
                    count += 1
                    break
        return count

    def insert(self, seq, line_id):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())
        self._line_ids.append(line_id)
        temp = []
        last_match = -1
        placeholder = False

        for i, token in enumerate(self._lcs_seq):

            # adjacent placeholders are not allowed
            if i in self._pos:
                if not placeholder:
                    temp.append("*")
                placeholder = True
                continue

            # else :
            for j in range(last_match+1, len(seq)):
                if seq[j] == token:
                    placeholder = False
                    temp.append(token)
                    last_match = j
                    break
                elif not placeholder:
                    temp.append("*")
                    placeholder = True
                    
        self._lcs_seq = temp
        self._pos = self._get_pos()
        self._sep = self._get_sep()

    def to_json(self):
        return json.dumps({
            "lcsseq": self._lcs_seq,
            "lineids": self._line_ids,
            "position": self._pos
        })

    def param(self, seq):
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())

        j = 0
        ret = []
        for i in range(len(self)):
            slot = []
            if i in self._pos:
                while j < len(seq):
                    if i != len(self._lcs_seq)-1 and self._lcs_seq[i + 1] == seq[j]:
                        break
                    else:
                        slot.append(seq[j])
                    j += 1
                ret.append(slot)
            elif self._lcs_seq[i] != seq[j]:
                return None
            else:
                j += 1

        if j != len(seq):
            return None
        else:
            return ret

    def re_param(self, seq):
        if isinstance(seq, list):
            seq = ' '.join(seq)
        seq = seq.strip()

        ret = []
        print(self._sep)
        print(seq)
        p = re.split(self._sep, seq)
        for i in p:
            if len(i) != 0:
                ret.append(re.split(self._refmt, i.strip()))
        if len(ret) == len(self._pos):
            return ret
        else:
            return None

    def _get_sep(self):
        sep_token = []
        s = 0
        e = 0
        for i in range(len(self)):
            if i in self._pos:
                if s != e:
                    sep_token.append(" ".join(self._lcs_seq[s:e+1]))
                s = i + 1
                e = i + 1
            else:
                e = i
            if e == len(self) - 1:
                sep_token.append(" ".join(self._lcs_seq[s:e+1]))
                break

        ret = ""
        for i in range(len(sep_token)):
            if i == len(sep_token)-1:
                ret += sep_token[i]
            else:
                ret += sep_token[i] + '|'
        return ret

    def _get_pos(self):
        return [i for i, x in enumerate(self._lcs_seq) if x == '*']

    def get_id(self):
        return self._id


class LCSMap:
    def __init__(self, refmt):
        self._refmt = refmt
        self._lcsobjs = []
        self._lineid = 0
        self._id = 0

    def __len__(self):
        return len(self._lcsobjs)

    def insert(self, entry):
        seq = re.split(self._refmt, entry.strip())
        obj = self.match(seq)

        if obj is None:
            obj = LCSObj(self._id, seq, self._lineid, self._refmt)
            self._lcsobjs.append(obj)
            self._id += 1
        else:
            obj.insert(seq, self._lineid)
        self._lineid += 1
        return obj

    def match(self, seq):
        """
        Match a sequence with an object in the map
        :param seq: list or str
        :return: LCSObj or None
        """
        if isinstance(seq, str):
            seq = re.split(self._refmt, seq.strip())
        best_match = None
        best_match_len = 0
        seq_len = len(seq)
        for obj in self._lcsobjs:
            obj_len = len(obj)
            if obj_len < seq_len/2 or obj_len > seq_len*2:
                continue

            lcs = obj.get_lcs(seq)
            if lcs >= seq_len/2 and lcs > best_match_len:
                best_match = obj
                best_match_len = lcs
        return best_match

    def obj_at(self, idx):
        return self._lcsobjs[idx]

    def dump(self):
        for i in self._lcsobjs:
            print(i.tojson())


def save(filename, spell_lcs_map):
    if type(spell_lcs_map) == LCSMap:
        with open(filename, 'wb') as f:
            pickle.dump(spell_lcs_map, f)
    else:
        if __debug__:
            print("%s isnt slm object" % filename)


def load(filename):
    with open(filename, 'rb') as f:
        slm = pickle.load(f)
        if type(slm) == LCSMap:
            return slm
        else:
            if __debug__:
                print("%s isnt slm object" % filename)
            return None
