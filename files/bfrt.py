from netaddr import IPAddress
p4p7 = bfrt.p7_polka.pipe_p7
p4user = bfrt.p7calc_mod.pipe
p4mirror = bfrt.mirror

def clear_all(verbose=True, batching=True):
    global p4p7
    global p4user
    global bfrt

    for table_types in (['MATCH_DIRECT', 'MATCH_INDIRECT_SELECTOR'],
                        ['SELECTOR'],
                        ['ACTION_PROFILE']):
        for table in p4p7.info(return_info=True, print_info=False):
            if table['type'] in table_types:
                if verbose:
                    print("Clearing table {:<40} ... ".
                          format(table['full_name']), end='', flush=True)
                table['node'].clear(batch=batching)
                if verbose:
                    print('Done')
        for table in p4user.info(return_info=True, print_info=False):
            if table['type'] in table_types:
                if verbose:
                    print("Clearing table {:<40} ... ".
                          format(table['full_name']), end='', flush=True)
                table['node'].clear(batch=batching)
                if verbose:
                    print('Done')

clear_all(verbose=True)

vlan_fwd = p4p7.SwitchIngress.vlan_fwd
vlan_fwd.add_with_match(vid=1920, ingress_port=168,   link=0, routeIdPacket=3729119541)

vlan_fwd = p4p7.SwitchIngress.vlan_fwd
vlan_fwd.add_with_match(vid=1920, ingress_port=160,   link=8, routeIdPacket=4123070420)

arp_fwd = p4p7.SwitchIngress.arp_fwd
arp_fwd.add_with_match_arp(vid=1920, ingress_port=168,   link=0, routeIdPacket=3729119541)

arp_fwd = p4p7.SwitchIngress.arp_fwd
arp_fwd.add_with_match_arp(vid=1920, ingress_port=160,   link=8, routeIdPacket=4123070420)

slice_dst = p4p7.SwitchIngress.slice_dst
slice_dst.add_with_slice_select_dst(diffserv=21, dest_ip=IPAddress('10.0.0.20'), routeIdPacket=7126279, pot_k=10)
slice_dst.add_with_slice_select_dst(diffserv=21, dest_ip=IPAddress('10.0.0.10'), routeIdPacket=343953, pot_k=10)

slice_dst = p4p7.SwitchIngress.slice_dst
slice_dst.add_with_slice_select_dst(diffserv=22, dest_ip=IPAddress('10.0.0.20'), routeIdPacket=1619189, pot_k=3)
slice_dst.add_with_slice_select_dst(diffserv=22, dest_ip=IPAddress('10.0.0.10'), routeIdPacket=6180130, pot_k=4)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=0, dest_ip=IPAddress('10.0.0.20'),   sw_id=0)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=1, dest_ip=IPAddress('10.0.0.20'),   sw_id=1)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=7, dest_ip=IPAddress('10.0.0.10'),   sw_id=4)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=8, dest_ip=IPAddress('10.0.0.10'),   sw_id=5)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=6, dest_ip=IPAddress('10.0.0.10'),   sw_id=3)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=4, dest_ip=IPAddress('10.0.0.10'),   sw_id=2)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=3, dest_ip=IPAddress('10.0.0.20'),   sw_id=3)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=6, dest_ip=IPAddress('10.0.0.20'),   sw_id=4)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=3, dest_ip=IPAddress('10.0.0.10'),   sw_id=1)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=7, dest_ip=IPAddress('10.0.0.20'),   sw_id=5)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=5, dest_ip=IPAddress('10.0.0.20'),   sw_id=4)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=5, dest_ip=IPAddress('10.0.0.10'),   sw_id=2)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=4, dest_ip=IPAddress('10.0.0.20'),   sw_id=3)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=2, dest_ip=IPAddress('10.0.0.10'),   sw_id=1)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=1, dest_ip=IPAddress('10.0.0.10'),   sw_id=0)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send_next(sw=2, dest_ip=IPAddress('10.0.0.20'),   sw_id=2)

basic_fwd = p4p7.SwitchIngress.basic_fwd
basic_fwd.add_with_send(sw=0, dest_ip=IPAddress('10.0.0.10'),   port=168)
basic_fwd.add_with_send(sw=8, dest_ip=IPAddress('10.0.0.20'),   port=160)

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_1(sw_id=0, dest_ip=IPAddress('10.0.0.20'), link_id=1)
basic_fwd_hash.add_with_send_next_1(sw_id=0, dest_ip=IPAddress('10.0.0.10'), link_id=0)
basic_fwd_hash.add_with_send_next_6(sw_id=5, dest_ip=IPAddress('10.0.0.10'), link_id=7)
basic_fwd_hash.add_with_send_next_6(sw_id=5, dest_ip=IPAddress('10.0.0.20'), link_id=8)

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_2(sw_id=1, dest_ip=IPAddress('10.0.0.20'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_2(sw_id=1, dest_ip=IPAddress('10.0.0.10'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_3(sw_id=2, dest_ip=IPAddress('10.0.0.20'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_3(sw_id=2, dest_ip=IPAddress('10.0.0.10'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_4(sw_id=3, dest_ip=IPAddress('10.0.0.20'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_4(sw_id=3, dest_ip=IPAddress('10.0.0.10'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_5(sw_id=4, dest_ip=IPAddress('10.0.0.20'))

basic_fwd_hash = p4p7.SwitchIngress.basic_fwd_hash
basic_fwd_hash.add_with_send_next_5(sw_id=4, dest_ip=IPAddress('10.0.0.10'))


calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add(sw_id= 0, dst_addr = IPAddress('10.0.0.10'), value = 4)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add(sw_id= 0, dst_addr = IPAddress('10.0.0.20'), value = 10)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 1, dst_addr = IPAddress('10.0.0.10'), value = 5)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 1, dst_addr = IPAddress('10.0.0.20'), value = 11)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 2, dst_addr = IPAddress('10.0.0.10'), value = 6)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 2, dst_addr = IPAddress('10.0.0.20'), value = 12)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 3, dst_addr = IPAddress('10.0.0.10'), value = 7)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 3, dst_addr = IPAddress('10.0.0.20'), value = 13)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 4, dst_addr = IPAddress('10.0.0.10'), value = 8)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add2(sw_id= 4, dst_addr = IPAddress('10.0.0.20'), value = 14)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add(sw_id= 5, dst_addr = IPAddress('10.0.0.10'), value = 9)
calculate = p4user.SwitchIngress.calculate
calculate.add_with_operation_add(sw_id= 5, dst_addr = IPAddress('10.0.0.20'), value = 15)


bfrt.complete_operations()

print("""
******************* PROGAMMING RESULTS *****************
""")
print ("Table vlan_fwd:")
vlan_fwd.dump(table=True)
print ("Table arp_fwd:")
arp_fwd.dump(table=True)
print ("Table basic_fwd:")
basic_fwd.dump(table=True)
print ("Table calculate:")
calculate.dump(table=True)
print ("Mirror:")
p4mirror.dump()
