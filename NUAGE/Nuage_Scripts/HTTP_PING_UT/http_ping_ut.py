#!/usr/bin/env python

import subprocess
import json
import time

probe_uuid_1 = "cc6129d8-94ab-4680-91cf-b227071c3aa3"
probe_uuid_2 = "cc6129d8-94ab-4680-91cf-b227071c3aa3"
probe_uuid_3 = "cc6129d8-94ab-4680-91cf-b227071c3aa3"
probe_uuid_4 = "cc6129d8-94ab-4680-91cf-b227071c3aa3"
probe_uuid_5 = "cc6129d8-94ab-4680-91cf-b227071c3aa3"


def run_cmd(cmd):
    print cmd
    output = subprocess.check_output(["ovsdb-client", "transact", cmd])
    return output


def ovsdb_insert(probe_uuid, targets, timeout, rate, thr_cnt, svc_class):
    cmd = ("[\"Open_vSwitch\", {\"table\":"
           "\"Nuage_IKE_Monitor_Config\", \"row\": {\"probe_uuid\":"
           "\"%(probe_uuid)s\",\"destination_target_list\":\"%(target)s\","
           "\"down_threshold_count\":%(down_threshold_cnt)d,\"rate\":\"%(rate)s\",\"timeout\":%(timeout)d},"
           "\"op\": \"insert\"}]") % {"probe_uuid": probe_uuid, "target": targets,
                                      "down_threshold_cnt": thr_cnt, "rate":
                                      rate, "timeout": timeout}
    output = json.loads(run_cmd(cmd))
    print output
    row_uuid = output[0]['uuid'][1]
    return row_uuid


def ovsdb_update(row_uuid, targets=None, timeout=-1, rate=-1, thr_cnt=-1):

    if targets:
        cmd = ("[\"Open_vSwitch\", {\"table\":\"Nuage_IKE_Monitor_Config\","
               "\"row\":{\"destination_target_list\":\"%(target)s\"},"
               "\"where\": [[\"_uuid\", \"==\", [\"uuid\", \"%(row_uuid)s\"]]],"
               "\"op\": \"update\"}]") % {"row_uuid": row_uuid, "target":
                                          targets}
    if rate != -1:
        cmd = ("[\"Open_vSwitch\", {\"table\":\"Nuage_IKE_Monitor_Config\","
               "\"row\":{\"rate\":\"%(rate)d\"},"
               "\"where\": [[\"_uuid\", \"==\", [\"uuid\", \"%(row_uuid)s\"]]],"
               "\"op\": \"update\"}]") % {"row_uuid": row_uuid, "rate":
                                          rate}

    print run_cmd(cmd)


def ovsdb_delete(row_uuid):

    cmd = ("[\"Open_vSwitch\", {\"table\":\"Nuage_IKE_Monitor_Config\","
           "\"where\": [[\"_uuid\", \"==\", [\"uuid\", \"%(row_uuid)s\"]]],"
           "\"op\": \"delete\"}]") % {"row_uuid": row_uuid}
    print run_cmd(cmd)


def test1():
    insert = (probe_uuid_1,
              "http://135.115.177.144", 500, 1,
              3, 10)
    row_uuid = ovsdb_insert(*insert)
    time.sleep(10)

    target_update = "http://135.115.177.158"
    ovsdb_update(row_uuid, targets=target_update)
    time.sleep(10);

    target_update = "http://www.github.mv.usa.alcatel.com/"
    ovsdb_update(row_uuid, targets=target_update)
    time.sleep(10)

    ovsdb_delete(row_uuid)


def test2():
    insert = (probe_uuid_2,
            "http://135.115.177.144", 5000000, 0.20, 5, 10)

    row_uuid = ovsdb_insert(*insert)
    print row_uuid
    time.sleep(120)
    ovsdb_delete(row_uuid)


def test3():
    insert = (probe_uuid_3,
              "http://135.115.177.158,http://135.115.177.144", 10000, 1,
              3, 10)

    target_update = "http://135.115.177.144"

    row_uuid = ovsdb_insert(*insert)
    time.sleep(10)
    ovsdb_update(row_uuid, targets=target_update)
    time.sleep(10)
    ovsdb_delete(row_uuid)

def test4():
    insert = (probe_uuid_4,
              "http://135.115.177.158,http://135.115.177.144", 10000, 1,
              3, 10)

    row_uuid = ovsdb_insert(*insert)
    time.sleep(10)
    ovsdb_update(row_uuid, rate=3)
    time.sleep(10)
    ovsdb_delete(row_uuid)

def test5():
    insert = (probe_uuid_5,
              "http://135.115.177.144,http://135.115.177.158", 500, 1,
              3, 10)
    row_uuid = ovsdb_insert(*insert)
    time.sleep(10)

    target_update = "http://135.115.177.144,http://135.115.177.158,http://www.github.mv.usa.alcatel.com/"
    ovsdb_update(row_uuid, targets=target_update)
    time.sleep(10)

    ovsdb_delete(row_uuid)

if __name__ == "__main__":
    #test1()
    #time.sleep(5);
    test2()
    #time.sleep(5);
    #test3()
    #time.sleep(5);
    #test4()
    #time.sleep(5);
    #test5()
